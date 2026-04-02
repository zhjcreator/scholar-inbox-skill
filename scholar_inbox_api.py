#!/usr/bin/env python3
"""
Scholar Inbox Python API

A Python client library for Scholar Inbox API.
https://api.scholar-inbox.com

Supports:
- Authentication via sha_key
- Paper search and discovery (trending, digest, search, semantic search)
- Bookmarks and collections management
- Paper rating (like/dislike)

Usage:
    from scholar_inbox_api import ScholarInboxClient

    # With sha_key (OpenClaw/WorkBuddy environment variable)
    client = ScholarInboxClient(sha_key="your-sha-key")

    # Or load from environment variable SCHOLAR_INBOX_SHA_KEY
    client = ScholarInboxClient.from_env()

    # Login with sha_key
    client.login_with_sha_key("your-sha-key")

    # Get trending papers
    papers = client.get_trending(category="ALL", days=7)

    # Search papers
    papers = client.search("transformers", limit=10)

    # Rate a paper (1=like, 0=dislike)
    client.make_rating(paper_id="4636621", rating=1)
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

import httpx

# Default API base URL
DEFAULT_API_BASE = "https://api.scholar-inbox.com"

# Config file path
CONFIG_PATH = Path.home() / ".config" / "scholar_inbox_api" / "config.json"


@dataclass
class ApiError(Exception):
    """API error exception."""
    message: str
    status_code: int | None = None
    detail: Any = None

    def __str__(self) -> str:
        if self.status_code:
            return f"ApiError({self.status_code}): {self.message}"
        return f"ApiError: {self.message}"


@dataclass
class SessionInfo:
    """Session information."""
    sha_key: str | None = None
    user_id: str | None = None
    username: str | None = None
    email: str | None = None
    is_authenticated: bool = False

    @classmethod
    def from_dict(cls, data: dict) -> SessionInfo:
        return cls(
            sha_key=data.get("sha_key"),
            user_id=data.get("user_id"),
            username=data.get("username"),
            email=data.get("email"),
            is_authenticated=data.get("is_authenticated", False),
        )


@dataclass
class Paper:
    """Paper representation."""
    _id: str
    title: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    year: int | None = None
    venue: str = ""
    citation_count: int = 0
    openreview_id: str | None = None
    arxiv_id: str | None = None
    pdf_url: str | None = None
    rating: int | None = None  # 1=liked, 0=disliked, None=not rated

    @classmethod
    def from_dict(cls, data: dict) -> Paper:
        return cls(
            _id=data.get("_id", ""),
            title=data.get("title", ""),
            authors=data.get("authors", []),
            abstract=data.get("abstract", ""),
            year=data.get("year"),
            venue=data.get.get("venue", ""),
            citation_count=data.get("citation_count", 0),
            openreview_id=data.get("openreview_id"),
            arxiv_id=data.get("arxiv_id"),
            pdf_url=data.get("pdf"),
            rating=data.get("rating"),
        )


class ScholarInboxClient:
    """
    Client for Scholar Inbox API.

    Supports authentication via sha_key and all Scholar Inbox operations.
    """

    def __init__(
        self,
        api_base: str | None = None,
        sha_key: str | None = None,
        no_retry: bool = False,
    ):
        """
        Initialize the Scholar Inbox client.

        Args:
            api_base: API base URL (default: https://api.scholar-inbox.com)
            sha_key: SHA key for authentication (optional, can be set later)
            no_retry: Disable automatic retry on rate limiting
        """
        self.api_base = api_base or os.environ.get(
            "SCHOLAR_INBOX_API_BASE"
        ) or DEFAULT_API_BASE
        self.sha_key = sha_key or os.environ.get("SCHOLAR_INBOX_SHA_KEY")
        self.no_retry = no_retry
        self._session: httpx.Client | None = None

    @classmethod
    def from_env(cls) -> ScholarInboxClient:
        """Create client from environment variables (SCHOLAR_INBOX_SHA_KEY)."""
        return cls()

    def _get_client(self) -> httpx.Client:
        """Get or create HTTP client with authentication headers."""
        if self._session is None:
            headers = {}
            if self.sha_key:
                headers["X-sha-key"] = self.sha_key
            self._session = httpx.Client(
                base_url=self.api_base,
                timeout=30.0,
                headers=headers,
                follow_redirects=True,
            )
        return self._session

    def _request(
        self,
        method: str,
        url: str,
        **kwargs: Any,
    ) -> Any:
        """Make an HTTP request with error handling and retry logic."""
        client = self._get_client()
        retries = 0

        while True:
            resp = client.request(method, url, **kwargs)

            # Check for authentication redirect
            if 300 <= resp.status_code < 400:
                location = resp.headers.get("location", "")
                if "/api/logout" in location or "/login" in location:
                    raise ApiError(
                        "Not authenticated (redirected to login)",
                        resp.status_code,
                        resp.text,
                    )

            # Handle rate limiting with exponential backoff
            if resp.status_code == 429 and not self.no_retry and retries < 3:
                time.sleep(1.5 * (2**retries))
                retries += 1
                continue

            # Handle errors
            if resp.status_code >= 400:
                try:
                    error_detail = resp.json()
                except Exception:
                    error_detail = resp.text
                raise ApiError(
                    f"Request failed: {url}",
                    resp.status_code,
                    error_detail,
                )

            # Parse JSON response
            content_type = resp.headers.get("content-type", "")
            if "application/json" in content_type:
                return resp.json()

            try:
                return resp.json()
            except Exception:
                return resp.text

    # ==================== Authentication ====================

    def login_with_sha_key(self, sha_key: str) -> SessionInfo:
        """
        Login with a sha_key.

        Args:
            sha_key: The sha_key from magic link login

        Returns:
            SessionInfo object with user details
        """
        self.sha_key = sha_key
        # Update session headers
        if self._session:
            self._session.headers["X-sha-key"] = sha_key
        else:
            self._get_client()

        return self.session_info()

    def session_info(self) -> SessionInfo:
        """
        Get current session information.

        Returns:
            SessionInfo with user details
        """
        data = self._request("GET", "/api/session_info")
        return SessionInfo.from_dict(data)

    def check_auth(self) -> bool:
        """Check if currently authenticated."""
        try:
            info = self.session_info()
            return info.is_authenticated
        except ApiError:
            return False

    # ==================== Paper Discovery ====================

    def get_digest(
        self,
        date: str | None = None,
        json: bool = True,
    ) -> dict | str:
        """
        Get daily digest of papers.

        Args:
            date: Date in MM-DD-YYYY format (default: today)
            json: Return JSON format (default: True)

        Returns:
            Digest data as dict or formatted text
        """
        params = {}
        if date:
            params["date"] = date
        if json:
            params["json"] = "true"

        return self._request("GET", "/api/", params=params)

    def get_trending(
        self,
        category: str = "ALL",
        days: int = 7,
        limit: int | None = None,
    ) -> dict:
        """
        Get trending papers.

        Args:
            category: Category filter (ALL, ML, Systems, NLP, etc.)
            days: Number of days to look back
            limit: Maximum number of papers to return

        Returns:
            Dict with trending papers data
        """
        params: dict[str, Any] = {
            "category": category,
            "days": days,
        }
        if limit is not None:
            params["limit"] = limit

        return self._request("GET", "/api/trending", params=params)

    def search(
        self,
        query: str,
        limit: int = 10,
        offset: int = 0,
    ) -> dict:
        """
        Search papers by keyword.

        Args:
            query: Search query string
            limit: Maximum number of results (default: 10)
            offset: Result offset for pagination

        Returns:
            Dict with search results
        """
        return self._request(
            "POST",
            "/api/get_search_results/",
            json={
                "query": query,
                "limit": limit,
                "offset": offset,
            },
        )

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
    ) -> dict:
        """
        Semantic search for papers.

        Args:
            query: Natural language search query
            limit: Maximum number of results

        Returns:
            Dict with semantic search results
        """
        return self._request(
            "POST",
            "/api/semantic-search",
            json={
                "query": query,
                "limit": limit,
            },
        )

    def get_interactions(
        self,
        interaction_type: str | None = None,
    ) -> dict:
        """
        Get paper interaction history (liked/disliked/read).

        Args:
            interaction_type: Filter by type (liked, disliked, read) or None for all

        Returns:
            Dict with interaction data
        """
        params = {}
        if interaction_type:
            params["type"] = interaction_type

        return self._request("GET", "/api/interactions", params=params)

    # ==================== Rating ====================

    def make_rating(
        self,
        paper_id: str,
        rating: int,
    ) -> dict:
        """
        Rate a paper (like or dislike).

        Args:
            paper_id: Paper ID (from _id field)
            rating: Rating value: 1 = like, 0 = dislike

        Returns:
            Updated paper object with new rating

        Raises:
            ApiError: If rating value is invalid
        """
        if rating not in (0, 1):
            raise ApiError(
                "Invalid rating value",
                400,
                "Rating must be 0 (dislike) or 1 (like)",
            )

        return self._request(
            "POST",
            "/api/make_rating/",
            json={
                "id": paper_id,
                "rating": rating,
            },
        )

    def like_paper(self, paper_id: str) -> dict:
        """Like a paper (convenience method)."""
        return self.make_rating(paper_id, rating=1)

    def dislike_paper(self, paper_id: str) -> dict:
        """Dislike a paper (convenience method)."""
        return self.make_rating(paper_id, rating=0)

    # ==================== Bookmarks ====================

    def get_bookmarks(self) -> dict:
        """
        Get bookmarked papers.

        Returns:
            Dict with bookmarked papers
        """
        return self._request("GET", "/api/bookmark_paper/")

    def add_bookmark(self, paper_id: str | int) -> dict:
        """
        Add a paper to bookmarks.

        Args:
            paper_id: Paper ID to bookmark

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/bookmark_paper/",
            json={"paper_id": paper_id},
        )

    def remove_bookmark(self, paper_id: str | int) -> dict:
        """
        Remove a paper from bookmarks.

        Args:
            paper_id: Paper ID to remove

        Returns:
            Response from API
        """
        return self._request(
            "DELETE",
            f"/api/bookmark_paper/{paper_id}/",
        )

    # ==================== Collections ====================

    def get_collections(self) -> dict:
        """
        Get all user collections.

        Returns:
            Dict with collections list
        """
        return self._request("GET", "/api/get_collections")

    def get_collection_papers(
        self,
        collection_name: str,
        limit: int = 50,
    ) -> dict:
        """
        Get papers in a collection.

        Args:
            collection_name: Name of the collection
            limit: Maximum papers to return

        Returns:
            Dict with collection papers
        """
        return self._request(
            "GET",
            "/api/collection-papers",
            params={
                "collection_name": collection_name,
                "limit": limit,
            },
        )

    def create_collection(self, name: str) -> dict:
        """
        Create a new collection.

        Args:
            name: Name for the new collection

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/create_collection/",
            json={"name": name},
        )

    def rename_collection(
        self,
        old_name: str,
        new_name: str,
    ) -> dict:
        """
        Rename a collection.

        Args:
            old_name: Current collection name
            new_name: New collection name

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/rename_collection/",
            json={
                "collection_name": old_name,
                "new_name": new_name,
            },
        )

    def delete_collection(self, name: str) -> dict:
        """
        Delete a collection.

        Args:
            name: Name of collection to delete

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/delete_collection/",
            json={"name": name},
        )

    def add_to_collection(
        self,
        collection_name: str,
        paper_ids: list[str | int],
    ) -> dict:
        """
        Add papers to a collection.

        Args:
            collection_name: Target collection name
            paper_ids: List of paper IDs to add

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/add_paper_to_collection/",
            json={
                "collection_name": collection_name,
                "paper_ids": paper_ids,
            },
        )

    def remove_from_collection(
        self,
        collection_name: str,
        paper_ids: list[str | int],
    ) -> dict:
        """
        Remove papers from a collection.

        Args:
            collection_name: Collection name
            paper_ids: List of paper IDs to remove

        Returns:
            Response from API
        """
        return self._request(
            "POST",
            "/api/remove_paper_from_collection/",
            json={
                "collection_name": collection_name,
                "paper_ids": paper_ids,
            },
        )

    def get_similar_papers(
        self,
        collection_name: str,
        sort: str = "relevance",
    ) -> dict:
        """
        Get similar papers based on a collection.

        Args:
            collection_name: Collection name to find similar papers for
            sort: Sort order (relevance, year)

        Returns:
            Dict with similar papers
        """
        return self._request(
            "GET",
            "/api/get_collections_similar_papers/",
            params={
                "collection_name": collection_name,
                "sort": sort,
            },
        )

    # ==================== Conferences ====================

    def get_conferences(self) -> dict:
        """
        Get list of available conferences.

        Returns:
            Dict with conference list
        """
        return self._request("GET", "/api/conference_list")

    def explore_conference(self, conference: str | None = None) -> dict:
        """
        Explore conference papers.

        Args:
            conference: Conference name (optional)

        Returns:
            Dict with conference papers
        """
        params = {}
        if conference:
            params["conference"] = conference

        return self._request("GET", "/api/conference-explorer", params=params)

    # ==================== Utility ====================

    def close(self) -> None:
        """Close the HTTP client."""
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> ScholarInboxClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()


# ==================== CLI Interface ====================

def main() -> None:
    """CLI interface for Scholar Inbox API."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Scholar Inbox Python API"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Login with sha_key")
    login_parser.add_argument("sha_key", help="Your sha_key")

    # Session info command
    subparsers.add_parser("session", help="Get session info")

    # Trending command
    trending_parser = subparsers.add_parser(
        "trending", help="Get trending papers"
    )
    trending_parser.add_argument(
        "--category", default="ALL", help="Category filter"
    )
    trending_parser.add_argument("--days", type=int, default=7, help="Days")
    trending_parser.add_argument(
        "--json", action="store_true", help="Output JSON"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search papers")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--limit", type=int, default=10, help="Result limit"
    )
    search_parser.add_argument(
        "--semantic", action="store_true", help="Use semantic search"
    )

    # Rate command
    rate_parser = subparsers.add_parser("rate", help="Rate a paper")
    rate_parser.add_argument("paper_id", help="Paper ID")
    rate_parser.add_argument(
        "rating", type=int, choices=[0, 1], help="Rating: 0=dislike, 1=like"
    )

    # Bookmarks command
    subparsers.add_parser("bookmarks", help="Get bookmarks")

    # Collections command
    collections_parser = subparsers.add_parser(
        "collections", help="Get collections"
    )
    collections_parser.add_argument(
        "--papers", help="Get papers in collection"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    client = ScholarInboxClient.from_env()

    if args.command == "login":
        client.login_with_sha_key(args.sha_key)
        print("Login successful!")
        print(json.dumps(client.session_info().__dict__, indent=2))

    elif args.command == "session":
        info = client.session_info()
        print(json.dumps(info.__dict__, indent=2, default=str))

    elif args.command == "trending":
        result = client.get_trending(
            category=args.category, days=args.days
        )
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "search":
        if args.semantic:
            result = client.semantic_search(args.query, limit=args.limit)
        else:
            result = client.search(args.query, limit=args.limit)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "rate":
        result = client.make_rating(args.paper_id, args.rating)
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "bookmarks":
        result = client.get_bookmarks()
        print(json.dumps(result, indent=2, default=str))

    elif args.command == "collections":
        if args.papers:
            result = client.get_collection_papers(args.papers)
        else:
            result = client.get_collections()
        print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
