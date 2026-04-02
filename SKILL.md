---
name: scholar-inbox-api
description: |
  This skill provides access to Scholar Inbox (https://www.scholar-inbox.com) via a Python API
  (scholar_inbox_api.py). Use this skill when the user wants to search academic papers, browse
  trending research, get daily paper digests, manage bookmarks and collections, explore conference
  proceedings, perform semantic paper searches, or rate papers (like/dislike). The tool is designed
  for both human researchers and AI agents, with JSON output support for programmatic use.
metadata:
  openclaw:
    requires:
      bins: ["uv"]
      env: ["SCHOLAR_INBOX_SHA_KEY"]
    primaryEnv: "SCHOLAR_INBOX_SHA_KEY"
---

# Scholar Inbox Python API

Interact with the Scholar Inbox academic paper platform via the Python API (`scholar_inbox_api.py`).
Provides paper discovery, search, bookmarking, collection management, and paper rating.

## Prerequisites

1. **Install uv** (if not already installed):

   - macOS/Linux: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `pip install uv` or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

2. **Install httpx** (required by the API):

```bash
uv pip install httpx
```

Or use the setup script:

```bash
./scripts/setup_env.sh
```

## Authentication

The API uses `X-sha-key` header for authentication. Set the `SCHOLAR_INBOX_SHA_KEY` environment
variable or pass the sha_key directly when initializing the client.

### Getting your sha_key

1. Visit https://www.scholar-inbox.com and **log in** to your account
2. Open browser **Developer Tools** (press `F12` or `Cmd+Option+I` on Mac)
3. Go to the **Network** tab
4. Refresh the page if needed
5. Look for a request to `https://api.scholar-inbox.com/api/session_info`
6. Click on it → select the **Response** tab
7. Find the `sha_key` field (a long hexadecimal string like `a1b2c3d4e5f6...`)
8. **Copy this value** — this is your authentication key

### Configure in OpenClaw

For OpenClaw users, set the sha_key in your configuration file:

```bash
# Edit ~/.openclaw/openclaw.json
```

Add this configuration:

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

The `SCHOLAR_INBOX_SHA_KEY` environment variable will be automatically injected when the skill loads.

### Python API Usage

```python
from scholar_inbox_api import ScholarInboxClient

# Create client (reads SCHOLAR_INBOX_SHA_KEY from environment)
client = ScholarInboxClient.from_env()

# Or with explicit sha_key
client = ScholarInboxClient(sha_key="your-sha-key")

# Login and verify
client.login_with_sha_key("your-sha-key")
session = client.session_info()
print(f"Logged in as: {session.username}")
```

### Check authentication status

```python
# Check if authenticated
is_auth = client.check_auth()

# Get session info
session = client.session_info()
print(f"Authenticated: {session.is_authenticated}")
```

Override the API base URL with the `SCHOLAR_INBOX_API_BASE` environment variable.

## Core Workflow

### Python API Usage Pattern

Always parse JSON responses for structured data in AI agent workflows:

```python
from scholar_inbox_api import ScholarInboxClient

client = ScholarInboxClient.from_env()

# Search papers
results = client.search("transformers", limit=5)
papers = results.get("digest_df", [])

# Present results
for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper.get('authors', []))}")
    print(f"Venue: {paper.get('display_venue', 'N/A')}")
    print()
```

### Presenting results to the user

When displaying paper results from JSON, extract and present these key fields:

| Field | JSON path | Description |
|-------|-----------|-------------|
| Title | `title` | Paper title |
| Authors | `authors` | Author list |
| Date | `publication_date` | Publication date (YYYY-MM-DD) |
| Venue | `display_venue` | e.g., "NeurIPS 2022", "ArXiv 2026 (March 28)" |
| Abstract | `abstract` | Full abstract text |
| Link | `url` | Direct PDF link (arxiv.org/pdf/...) |
| ArXiv ID | `arxiv_id` | ArXiv identifier |
| Citations | `citations` | Citation count (null if unavailable) |
| Likes | `total_likes` | Number of likes on the platform |
| Reads | `total_read` | Number of reads on the platform |
| GitHub | `github_url` | Associated GitHub repo link |
| HTML | `html_link` | ArXiv HTML version link |
| Conference | `conference` / `abbreviation` | Full name / short name of associated conference |
| Paper ID | `_id` | Unique paper ID (needed for rating) |
| Similarity | `similarity` | (semantic search only) 0-100 similarity score |
| Highlights | `inferredHighlights` | Auto-detected key passages with `startIndex`/`endIndex` |

For the full JSON response schema, read `references/json-response-schema.md`.

## Common Tasks

### Daily Digest

Fetch daily paper recommendations for a specific date:

```python
# Get today's digest
digest = client.get_digest()

# Get digest for a specific date (MM-DD-YYYY)
digest = client.get_digest(date="04-01-2026")
```

Date format is `MM-DD-YYYY`. Omit `date` for today.

Response structure:
- `current_digest_date`: the date of the digest
- `conf_notification_text`: notification about newly added conference proceedings
- `digest_df`: array of paper objects

### Trending Papers

Browse trending papers by category and time range:

```python
# Get trending papers
trending = client.get_trending(category="ALL", days=7)

# Filter by specific category
trending = client.get_trending(category="Machine Learning", days=30)
```

The `category` value maps to the **display category name** on Scholar Inbox, NOT the ArXiv
category code. Common values:

| Category | Description |
|----------|-------------|
| `ALL` | All categories (default) |
| `Language` | NLP, CL, etc. |
| `Machine Learning` | ML, LG, etc. |
| `Computer Vision and Graphics` | CV, CG, etc. |
| `Artificial Intelligence` | AI |
| `Robotics` | Robotics |
| `Sound and Audio Processing` | Audio/Speech |
| `Interdisciplinary` | Interdisciplinary topics |

Use `days` parameter to set the lookback period (default: 7).

### Keyword Search

Search papers by keywords with highlighting:

```python
# Search for papers
results = client.search("graph neural networks", limit=10)
papers = results.get("digest_df", [])

# Access highlighting info
highlights = results.get("abstract_highlighting_starts_ends", [])
```

Response includes:
- `digest_df`: array of paper objects (same schema as other commands)
- `abstract_highlighting_starts_ends`: array of highlight ranges per paper
- `authors_highlighting_starts_ends`: array of author name highlight ranges

### Semantic Search

Find papers by semantic similarity using natural language descriptions:

```python
# Semantic search
results = client.semantic_search(
    "how to improve reasoning in large language models",
    limit=5
)
papers = results.get("digest_df", [])
```

Each result includes a `similarity` field (0-100) and `similarity_color` for relevance ranking.
Semantic search understands meaning and context, making it more effective for exploratory queries.

### Bookmarks

```python
# List all bookmarks
bookmarks = client.get_bookmarks()

# Add a paper to bookmarks
client.add_bookmark("12345")

# Remove a paper from bookmarks
client.remove_bookmark("12345")
```

### Collections

```python
# List all collections
collections = client.get_collections()

# Create a new collection
client.create_collection("My Papers")

# Rename a collection
client.rename_collection("Old Name", "New Name")

# Delete a collection
client.delete_collection("My Papers")

# Add papers to a collection
client.add_to_collection("My Papers", ["12345", "67890"])

# Remove papers from a collection
client.remove_from_collection("My Papers", ["12345"])

# View papers in a collection
papers = client.get_collection_papers("My Papers")

# Get similar paper recommendations
similar = client.get_similar_papers("My Papers", sort="year")
```

### Conference Papers

```python
# List available conferences
conferences = client.get_conferences()

# Explore papers from a specific conference
papers = client.explore_conference("ICLR 2025")
```

Conference response fields: `conference_id`, `short_title` (e.g., "CVPR 2024"),
`full_title`, `conference_url`, `start_date`, `end_date`.

### Interaction History

View reading, liked, and disliked papers:

```python
# Get all interactions
interactions = client.get_interactions()

# Filter by type
liked = client.get_interactions(interaction_type="liked")
disliked = client.get_interactions(interaction_type="disliked")
```

### Rate Papers

Rate a paper (like/dislike) using the Python API:

```python
# Like a paper (rating: 1)
result = client.make_rating(paper_id="4636621", rating=1)

# Dislike a paper (rating: 0)
result = client.make_rating(paper_id="4636621", rating=0)

# Convenience methods
client.like_paper("4636621")
client.dislike_paper("4636621")
```

**Request fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `paper_id` | string | Yes | Paper ID (from `_id` field in API responses) |
| `rating` | int | Yes | `1` = like, `0` = dislike |

**Tip**: You can find paper IDs from other commands (e.g., `trending`, `search`, `digest`) in the `_id` field of each paper object.

## CLI Interface

The API also provides a CLI interface for quick commands:

```bash
# Login
python scholar_inbox_api.py login YOUR_SHA_KEY

# Get session info
python scholar_inbox_api.py session

# Get trending papers
python scholar_inbox_api.py trending --category ALL --days 7

# Search papers
python scholar_inbox_api.py search "transformers" --limit 10

# Semantic search
python scholar_inbox_api.py search "reasoning in LLMs" --semantic

# Rate a paper
python scholar_inbox_api.py rate 4636621 1

# Get bookmarks
python scholar_inbox_api.py bookmarks

# List collections
python scholar_inbox_api.py collections
```

## Troubleshooting

- **Authentication errors**: Re-run `login_with_sha_key()` with a fresh sha_key
- **Collection operations failing**: Retry or verify via the web interface
- **"uv not found"**: Install uv first via `brew install uv`
- **httpx not installed**: Run `uv pip install httpx` or `./scripts/setup_env.sh`
- **SCHOLAR_INBOX_SHA_KEY not set**: Configure it in `~/.openclaw/openclaw.json` (OpenClaw) or export it in your shell

## Reference

- `scholar_inbox_api.py` — Complete Python API with all methods documented
- `references/cli-reference.md` — Complete CLI command reference with all flags and options
- `references/json-response-schema.md` — Detailed JSON response field documentation
