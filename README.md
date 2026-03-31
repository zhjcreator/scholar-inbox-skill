# Scholar Inbox CLI Skill

A [WorkBuddy](https://www.codebuddy.cn) skill that provides CLI access to [Scholar Inbox](https://www.scholar-inbox.com) — an academic paper discovery and management platform. Search papers, browse trending research, get daily digests, manage bookmarks and collections, explore conference proceedings, and perform semantic searches, all from the command line.

Powered by [scholarinboxcli](https://github.com/mrshu/scholarinboxcli) with environment managed by [uv](https://docs.astral.sh/uv/).

## Features

- 📄 **Daily Digest** — Get personalized paper recommendations for any date
- 🔥 **Trending Papers** — Browse trending research by category and time range
- 🔍 **Keyword Search** — Full-text paper search with keyword highlighting
- 🧠 **Semantic Search** — Find papers by natural language descriptions
- 📑 **Bookmarks** — Manage personal paper bookmarks
- 📁 **Collections** — Create, organize, and explore paper collections
- 🎓 **Conferences** — Browse CVPR, NeurIPS, ICLR, ICML, ACL, etc.
- 📊 **Interaction History** — Track reading, liked, and disliked papers

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
  ```bash
  # macOS / Linux
  brew install uv
  # or
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  pip install uv
  ```

- A [Scholar Inbox](https://www.scholar-inbox.com) account (free)

## Installation

### As a WorkBuddy Skill

1. Download `scholar-inbox-skill.zip` from the [latest release](https://github.com/zhjcreator/scholar-inbox-skill/releases) (or clone this repo)
2. Extract and move to your WorkBuddy skills directory:
   ```bash
   cp -r scholar-inbox-skill ~/.workbuddy/skills/scholar-inbox
   ```
3. Set up the environment:
   ```bash
   bash ~/.workbuddy/skills/scholar-inbox/scripts/setup_env.sh
   ```

### Standalone CLI Usage

If you just want to use `scholarinboxcli` without WorkBuddy:
```bash
uv tool install scholarinboxcli
```

## Authentication

### Getting Your `sha_key`

You need a `sha_key` to authenticate. Here's how to find it:

1. Open your browser and go to [https://www.scholar-inbox.com](https://www.scholar-inbox.com)
2. **Log in** to your account
3. Open **Developer Tools** (`F12` or `Cmd+Option+I` on macOS)
4. Switch to the **Network** tab
5. Refresh the page or navigate to any page
6. Look for a request to `https://api.scholar-inbox.com/api/session_info`
7. Click on it and check the **Response** tab — you'll find your `sha_key` in the JSON response
8. Alternatively, check the **Preview** tab for a formatted view

### Logging In

Once you have your `sha_key`, authenticate:

```bash
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=YOUR_SHA_KEY&date=MM-DD-YYYY"
```

> Replace `MM-DD-YYYY` with today's date (e.g., `04-01-2026`).

Verify your session:

```bash
scholarinboxcli auth status --json
```

## Usage Examples

### Get Today's Paper Digest

```bash
scholarinboxcli digest --json
```

### Search for Papers

```bash
# Keyword search
scholarinboxcli search "large language models" --limit 10 --json

# Semantic search (natural language)
scholarinboxcli semantic "how to improve reasoning in large language models" --limit 5 --json
```

### Browse Trending Research

```bash
# All categories, last 7 days
scholarinboxcli trending --category ALL --days 7 --json

# Machine Learning papers, last 30 days
scholarinboxcli trending --category "Machine Learning" --days 30 --json
```

### Manage Collections

```bash
# List collections
scholarinboxcli collection list --json

# Create a new collection
scholarinboxcli collection create "My Research"

# Add papers by ID
scholarinboxcli collection add "My Research" 12345 67890

# View papers in a collection
scholarinboxcli collection papers "My Research" --json

# Get similar paper recommendations
scholarinboxcli collection similar "My Research" --json
```

### Explore Conferences

```bash
# List available conferences
scholarinboxcli conference list --json

# Explore papers from ICLR 2025
scholarinboxcli conference explore "ICLR 2025" --json
```

## Project Structure

```
scholar-inbox-skill/
├── .gitignore                # Exclude .venv from version control
├── SKILL.md                  # WorkBuddy skill definition (metadata + instructions)
├── README.md                 # This file
├── LICENSE                   # MIT License
├── references/
│   ├── cli-reference.md      # Complete CLI command reference with all flags
│   └── json-response-schema.md  # JSON response field documentation
└── scripts/
    └── setup_env.sh          # Environment setup script (uv-managed)
```

## How It Works

This skill wraps the [scholarinboxcli](https://github.com/mrshu/scholarinboxcli) Python package (v0.1.3) into a WorkBuddy-compatible skill format. The `setup_env.sh` script:

1. Checks that `uv` is installed
2. Creates an isolated Python virtual environment (`.venv/`)
3. Installs `scholarinboxcli` and its dependencies
4. Reports the CLI binary path for use in commands

All commands support `--json` output for structured, machine-readable results — making them ideal for AI agent workflows.

## Available Categories for Trending

| Category | Description |
|----------|-------------|
| `ALL` | All categories |
| `Language` | NLP, Computational Linguistics |
| `Machine Learning` | ML, Deep Learning |
| `Computer Vision and Graphics` | CV, CG |
| `Artificial Intelligence` | AI |
| `Robotics` | Robotics |
| `Sound and Audio Processing` | Audio, Speech |
| `Interdisciplinary` | Interdisciplinary topics |

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `uv: command not found` | Install uv: `brew install uv` |
| `Login failed` | Get a fresh `sha_key` from the Network tab (see Authentication section) |
| `Bookmarks appear as a collection` | Expected — bookmarks are stored as a special "Bookmarks" collection server-side |
| Collection operations failing | Retry or verify via the [web interface](https://www.scholar-inbox.com) |

## License

[MIT](./LICENSE)

## Acknowledgments

- [Scholar Inbox](https://www.scholar-inbox.com) — The academic paper platform
- [scholarinboxcli](https://github.com/mrshu/scholarinboxcli) — The CLI tool this skill wraps
- [uv](https://docs.astral.sh/uv/) — Python package manager
