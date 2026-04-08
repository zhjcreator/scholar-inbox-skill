---
name: scholar-inbox-skill
description: |
  Access Scholar Inbox (https://www.scholar-inbox.com) via the scholarinboxcli CLI tool.
  Use this skill when the user wants to search academic papers, browse trending research,
  get daily paper digests, manage bookmarks and collections, explore conference proceedings,
  perform semantic paper searches, or rate papers (like/dislike).
metadata:
  openclaw:
    requires:
      bins: ["uv", "scholarinboxcli"]
      env: []
    primaryEnv: ""
---

# Scholar Inbox Skill

Interact with the Scholar Inbox academic paper platform using the `scholarinboxcli` CLI tool.

## Setup

Run the setup script to install the CLI from the fork repository:

```bash
./scripts/setup_env.sh
```

This installs `scholarinboxcli` from `https://github.com/zhjcreator/scholarinboxcli` into a local `.venv`.

After setup, the CLI is available at:
```
.venv/bin/scholarinboxcli
```

You can also install globally:
```bash
uv tool install git+https://github.com/zhjcreator/scholarinboxcli.git
```

## Authentication

### Login with magic link URL

Get your login URL from Scholar Inbox:
1. Log in to your account on https://www.scholar-inbox.com
2. Find the magic link URL in your email, or extract the `sha_key` from the Network tab (F12 → Network → `api/session_info`) and construct: `https://www.scholar-inbox.com/login?sha_key=YOUR_KEY&date=MM-DD-YYYY`

```bash
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"
```

### Check Authentication Status

```bash
scholarinboxcli auth status
```

### Logout

```bash
scholarinboxcli auth logout
```

## Core Workflow

All commands support `--json` for machine-readable output. Use `--json` when processing results programmatically.

### Daily Digest

```bash
# Get today's paper digest
scholarinboxcli digest --json

# Get digest for a specific date (MM-DD-YYYY format)
scholarinboxcli digest --date 04-01-2026 --json
```

Response structure (JSON):
- `current_digest_date`: date of the digest
- `conf_notification_text`: conference notification text
- `digest_df`: array of paper objects

### Trending Papers

```bash
# Get trending papers (default: ALL categories, last 7 days)
scholarinboxcli trending --json

# Filter by category and time range
scholarinboxcli trending --category "Machine Learning" --days 30 --json

# Sort options
scholarinboxcli trending --sort hype --json        # default: sort by hype
scholarinboxcli trending --sort citations --asc --json
```

Common `--category` values:

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

### Keyword Search

```bash
# Search papers by keyword
scholarinboxcli search "graph neural networks" --json

# Limit results
scholarinboxcli search "transformers" --limit 10 --json

# Pagination
scholarinboxcli search "LLM" --limit 5 --offset 10 --json
```

### Semantic Search

Find papers by semantic similarity using natural language:

```bash
# Semantic search
scholarinboxcli semantic "how to improve reasoning in large language models" --json

# With limit
scholarinboxcli semantic "diffusion models for image generation" --limit 5 --json

# Read query from file
scholarinboxcli semantic --file query.txt --json
```

Each result includes a `similarity` field (0-100) for relevance ranking.

### Rate Papers

Rate a paper (upvote / downvote / remove rating):

```bash
# Upvote a paper
scholarinboxcli rate PAPER_ID 1

# Downvote a paper
scholarinboxcli rate PAPER_ID -1

# Remove rating
scholarinboxcli rate PAPER_ID 0
```

**Tip**: Get paper IDs from the `_id` field in search/digest/trending results.

### Bookmarks

```bash
# List all bookmarks
scholarinboxcli bookmark list --json

# Add a paper to bookmarks
scholarinboxcli bookmark add PAPER_ID

# Remove a paper from bookmarks
scholarinboxcli bookmark remove PAPER_ID
```

### Collections

```bash
# List all collections
scholarinboxcli collection list --json

# Create a new collection
scholarinboxcli collection create "My Papers"

# View papers in a collection
scholarinboxcli collection papers "My Papers" --json

# Add a paper to a collection
scholarinboxcli collection add "My Papers" PAPER_ID

# Remove a paper from a collection
scholarinboxcli collection remove "My Papers" PAPER_ID

# Rename a collection
scholarinboxcli collection rename "Old Name" "New Name"

# Delete a collection
scholarinboxcli collection delete "My Papers"

# Get similar paper recommendations based on collection(s)
scholarinboxcli collection similar "My Papers" --json
```

### Conference Papers

```bash
# List available conferences
scholarinboxcli conference list --json

# Explore papers from conferences
scholarinboxcli conference explore --json
```

### Interaction History

```bash
# Get your interaction history (viewed, rated, etc.)
scholarinboxcli interactions --json
```

## Presenting Results to the User

When displaying paper results from `--json` output, extract and present these key fields:

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

## Troubleshooting

- **"scholarinboxcli: command not found"**: Run `./scripts/setup_env.sh` or install via `uv tool install git+https://github.com/zhjcreator/scholarinboxcli.git`
- **Authentication errors**: Re-login with a fresh sha_key: `scholarinboxcli auth login --sha-key NEW_KEY`
- **"uv not found"**: Install uv first: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **SSL/TLS errors**: Ensure Python 3.10+ with OpenSSL 1.1.1+

## Reference

- `references/cli-reference.md` — Complete CLI command reference
- `references/json-response-schema.md` — Detailed JSON response field documentation
- Fork repository: https://github.com/zhjcreator/scholarinboxcli
