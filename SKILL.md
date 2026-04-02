---
name: scholar-inbox-api
description: |
  This skill provides access to Scholar Inbox (https://www.scholar-inbox.com) via a Python API
  (scholar_inbox_api.py). Use this skill when the user wants to search academic papers, browse
  trending research, get daily paper digests, manage bookmarks and collections, explore conference
  proceedings, perform semantic paper searches, or rate papers (like/dislike). The tool is designed
  for both human researchers and AI agents, with JSON output support for programmatic use.
  
  **This module inherits from scholarinboxcli.ScholarInboxClient** - all parent class methods are
  available plus extended functionality.
metadata:
  openclaw:
    requires:
      bins: ["uv"]
      env: ["SCHOLAR_INBOX_SHA_KEY"]
    primaryEnv: "SCHOLAR_INBOX_SHA_KEY"
---

# Scholar Inbox Python API

Interact with the Scholar Inbox academic paper platform via the Python API (`scripts/scholar_inbox_api.py`).
This module **inherits from `scholarinboxcli.ScholarInboxClient`** and extends it with additional
convenience methods and paper rating functionality.

## Architecture

```
scholarinboxcli.ScholarInboxClient (父类)
    │
    └── MyScholarInboxClient (子类)
            ├── 继承所有父类方法 (search, get_digest, collections, etc.)
            ├── login_with_sha_key() - sha_key 登录
            ├── rate_paper() - 论文评分
            ├── like_paper() / dislike_paper() - 点赞/点踩
            └── 更多便捷方法...
```

## Prerequisites

1. **Python 3.10+** (Important: Python 3.9 with LibreSSL may have TLS compatibility issues)

   - Check version: `python3 --version`
   - If you see SSL/TLS errors, use Python 3.10+ or the managed Python in WorkBuddy
   - Managed Python: `/Users/zhj/.workbuddy/binaries/python/versions/3.13.12/bin/python3`

2. **Install uv** (if not already installed):

   - macOS/Linux: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `pip install uv` or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

3. **Install dependencies**:

```bash
uv pip install scholarinboxcli httpx
```

Or use the setup script:

```bash
./scripts/setup_env.sh
```

**⚠️ SSL/TLS Note**: If you encounter SSL errors like `TLSV1_ALERT_PROTOCOL_VERSION`, your Python/OpenSSL
version is too old. Use Python 3.10+ with OpenSSL 1.1.1+ or 3.x.

## Authentication

The API supports two authentication methods:

### Method 1: Using sha_key (Recommended)

Get your sha_key from https://www.scholar-inbox.com:
1. Log in to your account
2. Open browser Developer Tools (F12 or Cmd+Option+I)
3. Go to Network tab
4. Find request to `api/session_info`
5. Copy the `sha_key` value from response

### Method 2: Using magic link

Use the full login URL from Scholar Inbox.

### Python API Usage

```python
from scripts.scholar_inbox_api import MyScholarInboxClient

# Method 1: From environment variable (SCHOLAR_INBOX_SHA_KEY)
client = MyScholarInboxClient.from_env()

# Method 2: With explicit sha_key
client = MyScholarInboxClient.from_sha_key("your-sha-key")

# Method 3: With magic link
client = MyScholarInboxClient.from_magic_link("https://www.scholar-inbox.com/login?sha_key=...")

# Check authentication
if client.is_authenticated:
    print("Logged in!")
    user = client.get_current_user()
    print(f"User: {user}")
```

### Check authentication status

```python
# Property-based check
if client.is_authenticated:
    print("Authenticated")

# Get current user
user = client.get_current_user()
if user:
    print(f"Logged in as: {user}")
```

Override the API base URL with `SCHOLAR_INBOX_API_BASE` environment variable.

## Core Workflow

### Python API Usage Pattern

All parent class methods are inherited. Use them directly:

```python
from scripts.scholar_inbox_api import MyScholarInboxClient

client = MyScholarInboxClient.from_env()

# Search papers (inherited from parent)
results = client.search("transformers", limit=5)
papers = results.get("digest_df", [])

# Get digest (inherited from parent)
digest = client.get_digest()

# Trending papers (inherited from parent)
trending = client.get_trending(category="ALL", days=7)

# Collections (inherited from parent)
collections = client.collections_list()
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
| Paper ID | `_id` | Unique paper ID (needed for rating) |
| Similarity | `similarity` | (semantic search only) 0-100 similarity score |

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
```

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

### Bookmarks

```python
# List all bookmarks
bookmarks = client.bookmarks()

# Add a paper to bookmarks
client.bookmark_add("12345")

# Remove a paper from bookmarks
client.bookmark_remove("12345")
```

### Collections

```python
# List all collections
collections = client.collections_list()

# Create a new collection
client.collection_create("My Papers")

# View papers in a collection
papers = client.collection_papers("collection_id")

# Get similar paper recommendations
similar = client.collections_similar(["collection_id1", "collection_id2"])
```

### Conference Papers

```python
# List available conferences
conferences = client.conference_list()

# Explore papers from a specific conference
papers = client.conference_explorer()
```

### Rate Papers (Extended Feature)

Rate a paper (like/dislike) using the extended API:

```python
# Like a paper (rating: 1)
result = client.like_paper("4637041")

# Dislike a paper (rating: -1)
result = client.dislike_paper("4637041")

# Or use the generic rate method
result = client.rate_paper("4637041", rating=1)  # 1=upvote, -1=downvote, 0=neutral

# Remove rating
result = client.remove_rating("4637041")
```

**Tip**: You can find paper IDs from other commands (e.g., `trending`, `search`, `digest`) in the `paper_id` field of each paper object.

### Quick Search Convenience Method

```python
# Simple wrapper around search()
results = client.quick_search("LLM", limit=5)

# Find papers with mode selection
results = client.find_papers("reasoning", mode="keyword", limit=10)
results = client.find_papers("reasoning", mode="semantic", limit=10)
```

## CLI Interface

The API also provides a CLI interface for quick commands:

```bash
# Login
python scripts/scholar_inbox_api.py login YOUR_SHA_KEY

# Get session info
python scripts/scholar_inbox_api.py status

# Get today's digest
python scripts/scholar_inbox_api.py digest

# Get digest for specific date
python scripts/scholar_inbox_api.py digest --date 04-01-2026

# Get trending papers
python scripts/scholar_inbox_api.py trending --category ALL --days 7

# Search papers
python scripts/scholar_inbox_api.py search "transformers" --limit 10

# Semantic search
python scripts/scholar_inbox_api.py search "reasoning in LLMs" --semantic

# Rate a paper
python scripts/scholar_inbox_api.py rate 4637041 1
```

## API Response Format Notes

Some APIs return wrapped response objects. Handle them accordingly:

```python
# collections_list() returns {"success": true, "collections": [...]}
data = client.collections_list()
collections = data.get("collections", [])

# bookmarks() returns {"success": true, "collections": [...]}
data = client.bookmarks()
bookmarks = data.get("collections", [])

# conference_list() returns {"success": true, "conferences": [...]}
data = client.conference_list()
conferences = data.get("conferences", [])

# For papers, always access digest_df
results = client.search("LLM")
papers = results.get("digest_df", [])
```

## Troubleshooting

- **Authentication errors**: Re-run `login_with_sha_key()` with a fresh sha_key
- **Collection operations failing**: Retry or verify via the web interface
- **"uv not found"**: Install uv first via `brew install uv`
- **scholarinboxcli not installed**: Run `uv pip install scholarinboxcli` or `./scripts/setup_env.sh`
- **SCHOLAR_INBOX_SHA_KEY not set**: Configure it in your environment or pass sha_key directly

## Reference

- `scripts/scholar_inbox_api.py` — Extended Python API (inherits from scholarinboxcli)
- `references/cli-reference.md` — Complete CLI command reference
- `references/json-response-schema.md` — Detailed JSON response field documentation
