# Scholar Inbox API — Complete Reference

> This skill includes a Python API (`scholar_inbox_api.py`) for Scholar Inbox.
> A CLI interface is also provided for quick commands.

## Python API

### Installation

```bash
uv pip install httpx
```

### Basic Usage

```python
from scholar_inbox_api import ScholarInboxClient

# Create client (reads SCHOLAR_INBOX_SHA_KEY from environment)
client = ScholarInboxClient.from_env()

# Or with explicit sha_key
client = ScholarInboxClient(sha_key="your-sha-key")

# Login and verify
client.login_with_sha_key("your-sha-key")
session = client.session_info()
```

### ScholarInboxClient Methods

#### Authentication

| Method | Description |
|--------|-------------|
| `login_with_sha_key(sha_key)` | Login with sha_key |
| `session_info()` | Get session info |
| `check_auth()` | Check if authenticated |

#### Paper Discovery

| Method | Description |
|--------|-------------|
| `get_digest(date=None)` | Get daily digest |
| `get_trending(category, days)` | Get trending papers |
| `search(query, limit)` | Keyword search |
| `semantic_search(query, limit)` | Semantic search |
| `get_interactions(type=None)` | Get interaction history |

#### Rating

| Method | Description |
|--------|-------------|
| `make_rating(paper_id, rating)` | Rate paper (1=like, 0=dislike) |
| `like_paper(paper_id)` | Like a paper |
| `dislike_paper(paper_id)` | Dislike a paper |

#### Bookmarks

| Method | Description |
|--------|-------------|
| `get_bookmarks()` | List bookmarks |
| `add_bookmark(paper_id)` | Add bookmark |
| `remove_bookmark(paper_id)` | Remove bookmark |

#### Collections

| Method | Description |
|--------|-------------|
| `get_collections()` | List all collections |
| `get_collection_papers(name)` | Get papers in collection |
| `create_collection(name)` | Create collection |
| `rename_collection(old, new)` | Rename collection |
| `delete_collection(name)` | Delete collection |
| `add_to_collection(name, paper_ids)` | Add papers |
| `remove_from_collection(name, paper_ids)` | Remove papers |
| `get_similar_papers(name, sort)` | Get similar papers |

#### Conferences

| Method | Description |
|--------|-------------|
| `get_conferences()` | List conferences |
| `explore_conference(name)` | Explore conference papers |

---

## CLI Interface

The API also provides a CLI interface:

```bash
python scholar_inbox_api.py <command> [options]
```

### Authentication Commands

```bash
# Login with sha_key
python scholar_inbox_api.py login YOUR_SHA_KEY

# Get session info
python scholar_inbox_api.py session
```

### Discovery Commands

```bash
# Get trending papers
python scholar_inbox_api.py trending --category ALL --days 7

# Search papers
python scholar_inbox_api.py search "transformers" --limit 10

# Semantic search
python scholar_inbox_api.py search "reasoning in LLMs" --semantic
```

### Rating Commands

```bash
# Rate a paper (1=like, 0=dislike)
python scholar_inbox_api.py rate PAPER_ID RATING

# Example: like paper 4636621
python scholar_inbox_api.py rate 4636621 1

# Example: dislike paper 4636621
python scholar_inbox_api.py rate 4636621 0
```

### Bookmark Commands

```bash
# List bookmarks
python scholar_inbox_api.py bookmarks
```

### Collection Commands

```bash
# List collections
python scholar_inbox_api.py collections

# Get papers in a collection
python scholar_inbox_api.py collections --papers "Collection Name"
```

---

## API Reference

### Endpoint: make_rating

Rate a paper (like/dislike).

```
POST https://api.scholar-inbox.com/api/make_rating/
```

**Headers**:

| Header | Required | Description |
|--------|----------|-------------|
| `Content-Type` | Yes | Must be `application/json` |
| `X-sha-key` | Yes | Your `SCHOLAR_INBOX_SHA_KEY` |

**Body** (JSON):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `rating` | integer | Yes | `1` = like, `0` = dislike |
| `id` | string | Yes | Paper ID (from `_id` field) |

**Example**:

```python
# Using Python API
client.make_rating(paper_id="4636621", rating=1)

# Using curl
curl -X POST "https://api.scholar-inbox.com/api/make_rating/" \
  -H "Content-Type: application/json" \
  -H "X-sha-key: $SCHOLAR_INBOX_SHA_KEY" \
  -d '{"rating": 1, "id": "4636621"}'
```

### Finding Paper IDs

Paper IDs can be found in the `_id` field of paper objects:

```python
# Get trending papers and extract IDs
results = client.get_trending(category="ALL", days=7)
papers = results.get("digest_df", [])
for paper in papers:
    print(f"ID: {paper['_id']}, Title: {paper['title']}")
```

---

## Configuration

| Environment Variable | Description |
|---------------------|-------------|
| `SCHOLAR_INBOX_SHA_KEY` | Authentication key |
| `SCHOLAR_INBOX_API_BASE` | API base URL (default: https://api.scholar-inbox.com) |

**OpenClaw Configuration** (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "scholar-inbox-api": {
        "enabled": true,
        "env": {
          "SCHOLAR_INBOX_SHA_KEY": "your-sha-key-here"
        }
      }
    }
  }
}
```
