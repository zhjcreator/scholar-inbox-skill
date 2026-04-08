# Scholar Inbox CLI — Complete Reference

`scholarinboxcli` is the official CLI for Scholar Inbox.
This skill uses a fork at `https://github.com/zhjcreator/scholarinboxcli` which adds:
- `auth login --sha-key` — login directly with a sha_key (no full URL needed)
- `rate PAPER_ID RATING` — upvote / downvote / remove rating for a paper

---

## Authentication

```bash
# Login with magic link URL
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY"

# Check login status
scholarinboxcli auth status

# Logout
scholarinboxcli auth logout
```

---

## Paper Discovery

### Digest

```bash
scholarinboxcli digest [--date MM-DD-YYYY] [--json] [--no-retry]
```

Examples:
```bash
scholarinboxcli digest --json
scholarinboxcli digest --date 04-01-2026 --json
```

### Trending

```bash
scholarinboxcli trending [--category CATEGORY] [--days N] [--sort FIELD] [--asc] [--json] [--no-retry]
```

Examples:
```bash
scholarinboxcli trending --json
scholarinboxcli trending --category "Machine Learning" --days 30 --json
scholarinboxcli trending --sort citations --asc --json
```

### Keyword Search

```bash
scholarinboxcli search QUERY [-n LIMIT] [--offset N] [--sort FIELD] [--json] [--no-retry]
```

Examples:
```bash
scholarinboxcli search "transformers" --json
scholarinboxcli search "graph neural networks" --limit 10 --json
scholarinboxcli search "LLM" --limit 5 --offset 10 --json
```

### Semantic Search

```bash
scholarinboxcli semantic [TEXT] [--file FILE] [-n LIMIT] [--offset N] [--json] [--no-retry]
```

Examples:
```bash
scholarinboxcli semantic "reasoning in large language models" --json
scholarinboxcli semantic "diffusion models" --limit 5 --json
scholarinboxcli semantic --file query.txt --json
```

---

## Paper Rating (fork feature)

```bash
scholarinboxcli rate PAPER_ID RATING [--no-retry]
```

| Rating | Meaning |
|--------|---------|
| `1` | Upvote |
| `-1` | Downvote |
| `0` | Remove rating |

Examples:
```bash
scholarinboxcli rate 4637041 1    # upvote
scholarinboxcli rate 4637041 -1   # downvote
scholarinboxcli rate 4637041 0    # remove rating
```

---

## Bookmarks

```bash
scholarinboxcli bookmark list [--json]
scholarinboxcli bookmark add PAPER_ID
scholarinboxcli bookmark remove PAPER_ID
```

---

## Collections

```bash
scholarinboxcli collection list [--json]
scholarinboxcli collection create NAME
scholarinboxcli collection rename OLD_NAME NEW_NAME
scholarinboxcli collection delete NAME
scholarinboxcli collection papers NAME [--json]
scholarinboxcli collection add NAME PAPER_ID
scholarinboxcli collection remove NAME PAPER_ID
scholarinboxcli collection similar NAME [--json]
```

---

## Conferences

```bash
scholarinboxcli conference list [--json]
scholarinboxcli conference explore [--json]
```

---

## Interactions

```bash
scholarinboxcli interactions [--json]
```

---

## Global Options

| Option | Description |
|--------|-------------|
| `--json` | Output as JSON (machine-readable) |
| `--no-retry` | Disable automatic retry on rate limits |
| `--help` | Show help for any command |

---

## Finding Paper IDs

Paper IDs are in the `_id` field of paper objects returned by `digest`, `search`, `trending`, and `semantic`:

```bash
# Get trending papers and extract IDs (with jq)
scholarinboxcli trending --json | jq '.digest_df[] | {id: ._id, title: .title}'
```

---

## Configuration

Cookies are stored at `~/.scholarinboxcli/cookies.json` after login.

Override base URL via environment variable:
```bash
export SCHOLAR_INBOX_API_BASE="https://www.scholar-inbox.com"
```
