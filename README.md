# Scholar Inbox Skill

A WorkBuddy skill for interacting with [Scholar Inbox](https://www.scholar-inbox.com) — an AI-powered academic paper discovery platform.

## Features

- **Paper Discovery**: Daily digest, trending papers, keyword search, semantic search
- **Ratings**: Rate papers (upvote / downvote / remove) — fork only
- **Collections**: Create, manage, and organize paper collections
- **Bookmarks**: Save papers for later reading
- **Conferences**: Browse conference proceedings
- **CLI Interface**: Full command-line access via `scholarinboxcli`

## Requirements

- Python 3.10+ (with OpenSSL 1.1.1+ or 3.x)
- [uv](https://astral.sh/uv) package manager

## Installation

```bash
# Install uv (if needed)
brew install uv   # macOS
# or: curl -LsSf https://astral.sh/uv/install.sh | sh

# Install from fork (includes rate command)
./scripts/setup_env.sh

# Or install globally
uv tool install git+https://github.com/zhjcreator/scholarinboxcli.git
```

## Authentication

```bash
# Get login URL from Scholar Inbox email, or construct manually:
# https://www.scholar-inbox.com/login?sha_key=<KEY>&date=MM-DD-YYYY
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"

scholarinboxcli auth status      # check session
scholarinboxcli auth logout      # clear session
```

## Usage

```bash
# Daily digest
scholarinboxcli digest --json

# Trending papers
scholarinboxcli trending --category "Machine Learning" --days 7

# Keyword search
scholarinboxcli search "transformers" --limit 10 --json

# Semantic search
scholarinboxcli semantic "graph neural networks" --limit 5 --json

# Rate papers (fork only)
scholarinboxcli rate PAPER_ID 1    # upvote
scholarinboxcli rate PAPER_ID -1   # downvote
scholarinboxcli rate PAPER_ID 0    # remove rating

# Bookmarks
scholarinboxcli bookmark list --json
scholarinboxcli bookmark add PAPER_ID

# Collections
scholarinboxcli collection list --json
scholarinboxcli collection create "My Papers"
scholarinboxcli collection papers "My Papers" --json

# Conferences
scholarinboxcli conference list --json

# Interactions
scholarinboxcli interactions --json
```

## Verify Installation

```bash
./scripts/test_skill.sh
```

## Directory Structure

```
scholar-inbox-skill/
├── scripts/
│   ├── setup_env.sh       # Install scholarinboxcli from fork
│   └── test_skill.sh      # Verify installation
├── references/
│   ├── cli-reference.md           # CLI command syntax
│   └── json-response-schema.md    # JSON response fields
├── assets/                   # Assets
├── SKILL.md                  # Skill definition (for WorkBuddy)
├── README.md / README_zh.md # This file
└── LICENSE                  # MIT
```

## License

MIT
