---
name: scholar-inbox-cli
description: |
  This skill provides access to Scholar Inbox (https://www.scholar-inbox.com) via its command-line
  interface scholarinboxcli. Use this skill when the user wants to search academic papers, browse
  trending research, get daily paper digests, manage bookmarks and collections, explore conference
  proceedings, or perform semantic paper searches. The tool is designed for both human researchers
  and AI agents, with JSON output support for programmatic use.
---

# Scholar Inbox CLI

Interact with the Scholar Inbox academic paper platform via `scholarinboxcli`, a Python CLI tool
managed with `uv`. Provides paper discovery, search, bookmarking, and collection management.

## Prerequisites

1. **Install uv** (if not already installed):

   - macOS/Linux: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `pip install uv` or `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`

2. **Install the CLI tool**:

```bash
uv tool install scholarinboxcli
```

Or install into a local virtual environment:

```bash
uv venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install scholarinboxcli
```

The CLI binary will be available as `scholarinboxcli` (if using `uv tool install`) or at
`.venv/bin/scholarinboxcli` (if using local venv).

## Authentication

First-time use requires authentication via a Magic Link from the Scholar Inbox web app:

### Getting your sha_key

1. Visit https://www.scholar-inbox.com and log in to your account
2. Open browser Developer Tools (F12) → Network tab
3. Find the request to `https://api.scholar-inbox.com/api/session_info`
4. Look at the Response — find the `sha_key` field (a long hex string like `a1b2c3d4...`)
5. Copy this value

### Login with sha_key

Construct the Magic Link URL using your sha_key and today's date:

```bash
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=YOUR_SHA_KEY&date=MM-DD-YYYY"
```

Replace `YOUR_SHA_KEY` with your actual key and `MM-DD-YYYY` with today's date.

### Check authentication status

Always verify authentication before executing commands:

```bash
scholarinboxcli auth status
```

Response fields:
- `is_logged_in`: boolean — whether the session is active
- `name`: string — user's display name
- `user_id`: integer — user ID
- `sha_key`: string — the authentication key
- `onboarding_status`: string — e.g., `"finished_fast_track"`

### Log out

```bash
scholarinboxcli auth logout
```

Config is stored at `~/.config/scholarinboxcli/config.json`. Override the API base URL with
the `SCHOLAR_INBOX_API_BASE` environment variable.

## Core Workflow

### Always use `--json` for structured output

Append `--json` to every command to get machine-readable JSON output. This is critical for AI agent
workflows where results need to be parsed and summarized.

```bash
scholarinboxcli search "transformers" --limit 5 --json
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
| Similarity | `similarity` | (semantic search only) 0-100 similarity score |
| Highlights | `inferredHighlights` | Auto-detected key passages with `startIndex`/`endIndex` |

For the full JSON response schema, read `references/json-response-schema.md`.

## Common Tasks

### Daily Digest

Fetch daily paper recommendations for a specific date:

```bash
scholarinboxcli digest --date 04-01-2026 --json
```

Date format is `MM-DD-YYYY`. Omit `--date` for today.

Response structure:
- `current_digest_date`: the date of the digest
- `conf_notification_text`: notification about newly added conference proceedings
- `digest_df`: array of paper objects

### Trending Papers

Browse trending papers by category and time range:

```bash
scholarinboxcli trending --category ALL --days 7 --json
```

The `--category` value maps to the **display category name** on Scholar Inbox, NOT the ArXiv
category code. Common values:

| Category Flag | Description |
|--------------|-------------|
| `ALL` | All categories (default) |
| `Language` | NLP, CL, etc. |
| `Machine Learning` | ML, LG, etc. |
| `Computer Vision and Graphics` | CV, CG, etc. |
| `Artificial Intelligence` | AI |
| `Robotics` | Robotics |
| `Sound and Audio Processing` | Audio/Speech |
| `Interdisciplinary` | Interdisciplinary topics |

Use `--days` to set the lookback period (default: 7).

### Keyword Search

Search papers by keywords with highlighting:

```bash
scholarinboxcli search "graph neural networks" --limit 10 --json
```

Response includes:
- `digest_df`: array of paper objects (same schema as other commands)
- `abstract_highlighting_starts_ends`: array of highlight ranges per paper (for keyword emphasis)
- `authors_highlighting_starts_ends`: array of author name highlight ranges

### Semantic Search

Find papers by semantic similarity using natural language descriptions:

```bash
scholarinboxcli semantic "how to improve reasoning in large language models" --limit 5 --json
```

Each result includes a `similarity` field (0-100) and `similarity_color` for relevance ranking.
Semantic search understands meaning and context, making it more effective for exploratory queries.

### Bookmarks

```bash
# List all bookmarks
scholarinboxcli bookmark list --json
```

Response returns a `collections` array with a single "Bookmarks" collection containing a `papers`
array. Bookmarks are a special server-side collection — this is expected behavior.

### Collections

```bash
# List all collections
scholarinboxcli collection list --json

# Create a new collection
scholarinboxcli collection create "Collection Name"

# Rename a collection
scholarinboxcli collection rename "Old Name" "New Name"

# Delete a collection
scholarinboxcli collection delete "Collection Name"

# Add papers to a collection (by paper ID)
scholarinboxcli collection add "CollectionName" 12345 67890

# Remove papers from a collection
scholarinboxcli collection remove "CollectionName" 12345

# View papers in a collection
scholarinboxcli collection papers "CollectionName" --json

# Get similar paper recommendations based on a collection
scholarinboxcli collection similar "CollectionName" --sort year --asc --json
```

### Conference Papers

```bash
# List available conferences
scholarinboxcli conference list --json

# Explore papers from a specific conference
scholarinboxcli conference explore "ICLR 2025" --json
```

Conference list response fields: `conference_id`, `short_title` (e.g., "CVPR 2024"),
`full_title`, `conference_url`, `start_date`, `end_date`.

### Interaction History

View reading, liked, and disliked papers:

```bash
scholarinboxcli interactions list --json
```

## Output Modes

- **Interactive mode** (default): Rich table display in terminal via `rich`
- **JSON mode** (`--json`): Structured JSON output
- **Pipe mode** (stdout is not a TTY): Automatically outputs JSON

## Troubleshooting

- **Authentication errors**: Re-run `auth login` with a fresh Magic Link
- **Collection operations failing**: Retry or verify via the web interface
- **"uv not found"**: Install uv first via `brew install uv`
- **CLI not found after install**: Ensure uv's tool bin directory is in your PATH, or use the full path to the venv binary

## Reference

- `references/cli-reference.md` — Complete CLI command reference with all flags and options
- `references/json-response-schema.md` — Detailed JSON response field documentation
