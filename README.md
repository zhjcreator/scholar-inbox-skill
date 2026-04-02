# Scholar Inbox API Skill

A WorkBuddy skill for interacting with [Scholar Inbox](https://www.scholar-inbox.com) - an AI-powered academic paper discovery platform.

## Features

- **Paper Discovery**: Daily digest, trending papers, keyword search, semantic search
- **Ratings**: Like/dislike papers, rate papers
- **Collections**: Create, manage, and organize paper collections
- **Bookmarks**: Save papers for later reading
- **Conferences**: Browse conference proceedings
- **Full API**: Both Python API and CLI interface

## Architecture

This skill inherits from `scholarinboxcli.ScholarInboxClient` and extends it with additional functionality:

```
scholarinboxcli.ScholarInboxClient (Parent)
    │
    └── MyScholarInboxClient (Extended)
            ├── Inherited: search, get_digest, collections, bookmarks, etc.
            ├── login_with_sha_key() - SHA key authentication
            ├── rate_paper() - Rate papers
            ├── like_paper() / dislike_paper() - Vote on papers
            └── More convenience methods...
```

## Installation

### Prerequisites

- Python 3.10+ (with OpenSSL 1.1.1+ or 3.x)
- uv package manager

```bash
# Install uv (if not installed)
brew install uv  # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install scholarinboxcli httpx

# Or use the setup script
./scripts/setup_env.sh
```

### Authentication

Get your `sha_key` from https://www.scholar-inbox.com:
1. Log in to your account
2. Open Developer Tools (F12)
3. Go to Network tab
4. Find request to `api/session_info`
5. Copy the `sha_key` value

Set the environment variable:
```bash
export SCHOLAR_INBOX_SHA_KEY="your-sha-key"
```

## Usage

### Python API

```python
from scripts.scholar_inbox_api import MyScholarInboxClient

# Initialize with environment variable
client = MyScholarInboxClient.from_env()

# Or with explicit sha_key
client = MyScholarInboxClient.from_sha_key("your-sha-key")

# Check authentication
if client.is_authenticated:
    user = client.get_current_user()
    print(f"Logged in as: {user}")

# Search papers
results = client.search("machine learning", limit=5)
papers = results.get("digest_df", [])

# Get daily digest
digest = client.get_digest()

# Get trending papers
trending = client.get_trending(category="Machine Learning", days=7)

# Semantic search
results = client.semantic_search("how to improve LLM reasoning", limit=5)

# Rate papers
client.like_paper("12345")      # Like
client.dislike_paper("12345")   # Dislike
client.rate_paper("12345", 1)   # Explicit rating

# Collections
collections = client.collections_list()
client.collection_create("My ML Papers")
```

### CLI Interface

```bash
# Check status
python scripts/scholar_inbox_api.py status

# Get daily digest
python scripts/scholar_inbox_api.py digest

# Search papers
python scripts/scholar_inbox_api.py search "transformers" --limit 10

# Semantic search
python scripts/scholar_inbox_api.py search "reasoning" --semantic

# Rate a paper
python scripts/scholar_inbox_api.py rate 4636621 1  # paper_id, rating
```

## Running Tests

```bash
# Using Python 3.13 (recommended for TLS compatibility)
PYTHON=/Users/zhj/.workbuddy/binaries/python/versions/3.13.12/bin/python3
PYTHONPATH="/path/to/scholarinboxcli/src:$PYTHONPATH" \
  $PYTHON scripts/test_skill.py
```

## SSL/TLS Note

If you encounter SSL errors like `TLSV1_ALERT_PROTOCOL_VERSION`, your Python/OpenSSL version is too old. Use Python 3.10+ with OpenSSL 1.1.1+ or 3.x.

## Directory Structure

```
scholar-inbox/
├── scripts/
│   ├── __init__.py
│   ├── scholar_inbox_api.py   # Main API
│   ├── test_skill.py          # Tests
│   └── setup_env.sh           # Setup script
├── references/
│   ├── cli-reference.md      # CLI docs
│   └── json-response-schema.md # JSON schema docs
├── assets/                    # Assets (empty)
├── SKILL.md                   # Skill definition
└── README.md                  # This file
```

## License

MIT
