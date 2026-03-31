# Scholar Inbox CLI Skill

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-Skill-blue)](https://clawhub.ai)

An [OpenClaw](https://clawhub.ai) skill for interacting with [Scholar Inbox](https://www.scholar-inbox.com) — a personalized academic paper recommendation platform. Search papers, browse trending research, manage bookmarks and collections, all via command line.

## Features

- **Daily Digest** — Get personalized paper recommendations for any date
- **Trending Papers** — Browse what's hot across categories (ML, NLP, CV, etc.)
- **Keyword Search** — Find papers with highlighted matching terms
- **Semantic Search** — Natural language queries with similarity scores
- **Bookmarks & Collections** — Organize papers into custom collections
- **Conference Papers** — Explore proceedings from major ML/AI conferences
- **JSON Output** — Structured data for AI agent workflows

## Requirements

- [uv](https://github.com/astral-sh/uv) — Python package manager
- `SCHOLAR_INBOX_SHA_KEY` environment variable (see Authentication section)

## Installation

### 1. Install uv

```bash
# macOS/Linux
brew install uv

# Or via curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
pip install uv
# Or
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Install the CLI

```bash
# Option 1: Install globally with uv
uv tool install scholarinboxcli

# Option 2: Use the setup script (creates local venv)
bash scripts/setup_env.sh
```

### 3. Configure OpenClaw (if using OpenClaw)

Add to `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "scholar-inbox-cli": {
        "enabled": true,
        "env": {
          "SCHOLAR_INBOX_SHA_KEY": "your-sha-key-here"
        }
      }
    }
  }
}
```

The skill declares `metadata.openclaw.requires.env: ["SCHOLAR_INBOX_SHA_KEY"]` so OpenClaw will:
- Check that this environment variable is set before loading the skill
- Inject it into the process environment when the skill is invoked

## Authentication

Scholar Inbox requires authentication via a Magic Link using a `sha_key`.

### Getting your sha_key

1. Visit https://www.scholar-inbox.com and **log in** to your account
2. Open browser **Developer Tools** (press `F12` or `Cmd+Option+I` on Mac)
3. Go to the **Network** tab
4. Refresh the page if needed
5. Look for a request to `https://api.scholar-inbox.com/api/session_info`
6. Click on it → select the **Response** tab
7. Find the `sha_key` field (a long hexadecimal string like `a1b2c3d4e5f6...`)
8. **Copy this value** — this is your authentication key

![Where to find sha_key](https://i.imgur.com/placeholder.png)

> **Security Note:** The `sha_key` is sensitive — treat it like a password. Don't commit it to git or share it publicly.

### Login

Once you have the `SCHOLAR_INBOX_SHA_KEY` environment variable set:

```bash
# Using environment variable (recommended)
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=$SCHOLAR_INBOX_SHA_KEY&date=$(date +%m-%d-%Y)"

# Or with explicit key
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=YOUR_KEY&date=04-01-2026"
```

### Verify authentication

```bash
scholarinboxcli auth status
```

Expected output:
```json
{
  "is_logged_in": true,
  "name": "Your Name",
  "user_id": 12345,
  "sha_key": "a1b2c3d4...",
  "onboarding_status": "finished_fast_track"
}
```

## Usage

### Always use `--json` for AI workflows

```bash
# Daily digest
scholarinboxcli digest --date 04-01-2026 --json

# Trending papers (last 7 days, all categories)
scholarinboxcli trending --category ALL --days 7 --json

# Keyword search
scholarinboxcli search "transformer architecture" --limit 5 --json

# Semantic search
scholarinboxcli semantic "how to improve reasoning in LLMs" --limit 5 --json

# List your collections
scholarinboxcli collection list --json

# List bookmarks
scholarinboxcli bookmark list --json

# Explore conference papers
scholarinboxcli conference list --json
scholarinboxcli conference explore "ICLR 2025" --json
```

### Categories for Trending

| Category | Description |
|----------|-------------|
| `ALL` | All categories |
| `Machine Learning` | ML, deep learning |
| `Language` | NLP, computational linguistics |
| `Computer Vision and Graphics` | CV, computer graphics |
| `Artificial Intelligence` | AI, agents, planning |
| `Robotics` | Robotics, manipulation |
| `Sound and Audio Processing` | Audio, speech, music |
| `Interdisciplinary` | Cross-domain topics |

## Response Format

All commands with `--json` return structured data. Key paper fields:

| Field | Description |
|-------|-------------|
| `title` | Paper title |
| `authors` | List of authors |
| `publication_date` | Date (YYYY-MM-DD) |
| `display_venue` | Venue name (e.g., "NeurIPS 2022") |
| `abstract` | Full abstract |
| `url` | PDF link |
| `arxiv_id` | ArXiv identifier |
| `citations` | Citation count |
| `total_likes` / `total_read` | Platform engagement |
| `similarity` | Semantic search score (0-100) |

See `references/json-response-schema.md` for complete schema documentation.

## Project Structure

```
scholar-inbox-skill/
├── SKILL.md                          # Skill definition & usage guide
├── README.md                         # This file
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
├── references/
│   ├── cli-reference.md              # Complete CLI command reference
│   └── json-response-schema.md       # API response field documentation
└── scripts/
    └── setup_env.sh                  # Environment setup script
```

## CLI Reference

| Command | Description |
|---------|-------------|
| `auth login --url URL` | Authenticate with Magic Link |
| `auth status` | Check authentication state |
| `auth logout` | Log out |
| `digest [--date DATE]` | Daily paper recommendations |
| `trending --category CAT --days N` | Trending papers |
| `search QUERY [--limit N]` | Keyword search |
| `semantic QUERY [--limit N]` | Semantic/natural language search |
| `bookmark list` | List bookmarks |
| `collection list` | List collections |
| `collection create NAME` | Create collection |
| `collection add NAME ID...` | Add papers to collection |
| `conference list` | List available conferences |
| `conference explore NAME` | Explore conference papers |

See `references/cli-reference.md` for all commands and options.

## OpenClaw Integration

This skill is designed for [OpenClaw](https://clawhub.ai) with the following metadata:

```yaml
metadata:
  openclaw:
    requires:
      bins: ["uv"]
      env: ["SCHOLAR_INBOX_SHA_KEY"]
    primaryEnv: "SCHOLAR_INBOX_SHA_KEY"
```

This ensures:
- The skill only loads if `uv` is installed
- The skill only loads if `SCHOLAR_INBOX_SHA_KEY` is configured
- The environment variable is automatically injected when the skill runs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `uv: command not found` | Install uv first (see Installation) |
| `SCHOLAR_INBOX_SHA_KEY not set` | Configure in `~/.openclaw/openclaw.json` or export in shell |
| `scholarinboxcli: command not found` | Use full path: `.venv/bin/scholarinboxcli` or add uv tool bin to PATH |
| Authentication fails | Get a fresh sha_key from browser (they may expire) |
| Empty results | Check auth status first: `scholarinboxcli auth status` |

## License

MIT License — see [LICENSE](LICENSE) file.

## Links

- [Scholar Inbox](https://www.scholar-inbox.com)
- [scholarinboxcli on PyPI](https://pypi.org/project/scholarinboxcli/)
- [OpenClaw/ClawHub](https://clawhub.ai)
- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Original CLI Repository](https://github.com/mrshu/scholarinboxcli)
