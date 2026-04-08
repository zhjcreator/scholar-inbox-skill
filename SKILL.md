---
name: scholar-inbox-skill
description: |
  Access Scholar Inbox (https://www.scholar-inbox.com) via the scholarinboxcli CLI tool.
  Use this when the user wants to search academic papers, browse trending research,
  get daily digests, manage bookmarks and collections, explore conferences,
  perform semantic searches, or rate papers.
metadata:
  openclaw:
    requires:
      bins: ["uv", "scholarinboxcli"]
      env: []
    primaryEnv: ""
---

# Scholar Inbox Skill

All commands support `--json` for machine-readable output.

## Setup

```bash
./scripts/setup_env.sh          # install into local .venv
.venv/bin/scholarinboxcli       # use the CLI

# or install globally
uv tool install git+https://github.com/zhjcreator/scholarinboxcli.git
```

## Authentication

```bash
# Get login URL from Scholar Inbox email, or construct:
# https://www.scholar-inbox.com/login?sha_key=<KEY>&date=MM-DD-YYYY
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"

scholarinboxcli auth status      # check session
scholarinboxcli auth logout      # clear session
```

## Daily Digest

```bash
scholarinboxcli digest --json              # today's digest
scholarinboxcli digest --date 04-01-2026  # specific date (MM-DD-YYYY)
```

## Trending Papers

```bash
scholarinboxcli trending --json                         # default: ALL, 7 days
scholarinboxcli trending --category "Machine Learning" --days 30
scholarinboxcli trending --sort hype --json             # sort by hype (default)
scholarinboxcli trending --sort citations --asc --json
```

Categories: `ALL`, `Language`, `Machine Learning`, `Computer Vision and Graphics`, `Artificial Intelligence`, `Robotics`, `Sound and Audio Processing`, `Interdisciplinary`.

## Search

```bash
scholarinboxcli search "transformers" --limit 10 --json
scholarinboxcli search "LLM" --limit 5 --offset 10     # pagination
scholarinboxcli semantic "graph neural networks" --limit 5 --json  # semantic
scholarinboxcli semantic --file query.txt --json        # query from file
```

Semantic results include a `similarity` field (0-100).

## Rate Papers

**Requires the fork** (`zhjcreator/scholarinboxcli`):

```bash
scholarinboxcli rate PAPER_ID 1    # upvote
scholarinboxcli rate PAPER_ID -1   # downvote
scholarinboxcli rate PAPER_ID 0    # remove rating
```

Get `PAPER_ID` from the `_id` field in any search/digest/trending result.

## Bookmarks

```bash
scholarinboxcli bookmark list --json
scholarinboxcli bookmark add PAPER_ID
scholarinboxcli bookmark remove PAPER_ID
```

## Collections

```bash
scholarinboxcli collection list --json
scholarinboxcli collection create "My Papers"
scholarinboxcli collection papers "My Papers" --json
scholarinboxcli collection add "My Papers" PAPER_ID
scholarinboxcli collection remove "My Papers" PAPER_ID
scholarinboxcli collection rename "Old" "New"
scholarinboxcli collection delete "My Papers"
scholarinboxcli collection similar "My Papers" --json   # recommendations
```

## Conferences & Interactions

```bash
scholarinboxcli conference list --json
scholarinboxcli conference explore --json
scholarinboxcli interactions --json       # your view/like/dislike history
```

## Output Fields

When presenting papers from `--json`, key fields:

| Field | Path | Description |
|-------|------|-------------|
| Title | `title` | Paper title |
| Authors | `authors` | Author list |
| Date | `publication_date` | YYYY-MM-DD |
| Venue | `display_venue` | e.g., "NeurIPS 2022" |
| Abstract | `abstract` | Full abstract |
| PDF Link | `url` | arxiv.org/pdf/... |
| Citations | `citations` | Citation count |
| Likes | `total_likes` | Platform likes |
| Reads | `total_read` | Platform reads |
| Paper ID | `_id` | Unique ID (for rating) |
| Similarity | `similarity` | Semantic search only (0-100) |

Full schema: `references/json-response-schema.md`

## Troubleshooting

- **"command not found"**: Run `./scripts/setup_env.sh`
- **Auth errors**: Re-login: `scholarinboxcli auth login --url "..."`
- **"uv not found"**: `brew install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`
