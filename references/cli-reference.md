# scholarinboxcli — Complete CLI Reference

> Version 0.1.3 | Python >=3.10 | MIT License
> Source: https://github.com/mrshu/scholarinboxcli

## Binary Path

After running `scripts/setup_env.sh`, the CLI binary is located at:

```
~/.workbuddy/skills/scholar-inbox/.venv/bin/scholarinboxcli
```

## Global Options

```
scholarinboxcli --help    Show help message
scholarinboxcli --version Show version
```

All subcommands support `--json` for JSON output (append before subcommand flags where applicable).

---

## auth — Authentication

Manage login sessions with the Scholar Inbox API.

### `auth login`

Authenticate using a Magic Link from the web app.

```bash
scholarinboxcli auth login --url "https://www.scholar-inbox.com/login?sha_key=KEY&date=MM-DD-YYYY"
```

| Flag       | Required | Description                              |
|------------|----------|------------------------------------------|
| `--url`    | Yes      | Full Magic Link URL from scholar-inbox.com |

The Magic Link URL format: `https://www.scholar-inbox.com/login?sha_key=...&date=MM-DD-YYYY`

### `auth status`

Check current authentication session status. Always run this before other commands.

```bash
scholarinboxcli auth status --json
```

**JSON response fields**:

| Field              | Type    | Description                        |
|--------------------|---------|------------------------------------|
| `is_logged_in`     | boolean | Whether the session is active      |
| `is_admin`         | boolean | Whether the user is an admin       |
| `name`             | string  | User's display name                |
| `user_id`          | integer | User ID                            |
| `sha_key`          | string  | Authentication key                 |
| `onboarding_status`| string  | Onboarding state (e.g., `"finished_fast_track"`) |
| `profile_picture`  | string\|null | Profile picture URL              |

No additional flags.

### `auth logout`

Clear local authentication config.

```bash
scholarinboxcli auth logout
```

No additional flags.

**Config location**: `~/.config/scholarinboxcli/config.json`
**Env override**: `SCHOLAR_INBOX_API_BASE` — custom API base URL

---

## digest — Daily Paper Digest

Fetch daily paper recommendations.

```bash
scholarinboxcli digest --date MM-DD-YYYY --json
```

| Flag     | Required | Description                          |
|----------|----------|--------------------------------------|
| `--date` | No       | Date in `MM-DD-YYYY` format. Defaults to today. |

**JSON response fields**:

| Field                   | Type   | Description                                      |
|-------------------------|--------|--------------------------------------------------|
| `current_digest_date`   | string | Date of the digest (YYYY-MM-DD)                  |
| `conf_notification_text`| string | Notification about newly added conference papers (may contain HTML) |
| `custom_digest_range`   | boolean| Whether a custom date range was used              |
| `digest_df`             | array  | Array of paper objects (see json-response-schema.md) |

**Example**:
```bash
scholarinboxcli digest --date 04-01-2026 --json
```

---

## trending — Trending Papers

Browse trending papers by category and time range.

```bash
scholarinboxcli trending --category CATEGORY --days N --json
```

| Flag        | Required | Description                                      |
|-------------|----------|--------------------------------------------------|
| `--category` | No      | Display category name (NOT ArXiv code). Defaults to `ALL`. |
| `--days`    | No       | Number of days to look back.                     |

**IMPORTANT**: The `--category` flag uses the Scholar Inbox **display category name**, not the
ArXiv subject code. For example, use `"Machine Learning"` instead of `"cs.LG"`.

| Category Flag | Description |
|--------------|-------------|
| `ALL` | All categories |
| `Language` | Computation and Language, NLP |
| `Machine Learning` | Machine Learning, LG |
| `Computer Vision and Graphics` | Computer Vision, Computer Graphics |
| `Artificial Intelligence` | AI |
| `Robotics` | Robotics |
| `Sound and Audio Processing` | Audio, Speech Processing |
| `Interdisciplinary` | Interdisciplinary topics |

**JSON response fields**:

| Field       | Type  | Description                              |
|-------------|-------|------------------------------------------|
| `success`   | boolean| Whether the request succeeded            |
| `digest_df` | array | Array of paper objects                   |

Each paper includes a `digest_date` field (epoch ms) and a `category` field with the display name.

**Example**:
```bash
scholarinboxcli trending --category "Machine Learning" --days 14 --json
```

---

## search — Keyword Search

Search papers by keywords with highlighting support.

```bash
scholarinboxcli search "QUERY" --limit N --json
```

| Flag       | Required | Description                     |
|------------|----------|---------------------------------|
| `QUERY`    | Yes      | Search query string (positional)|
| `--limit`  | No       | Maximum number of results       |

**JSON response fields**:

| Field                                | Type         | Description                                |
|--------------------------------------|--------------|--------------------------------------------|
| `digest_df`                          | array        | Array of paper objects                     |
| `abstract_highlighting_starts_ends`  | array[array] | Highlight ranges per paper (pairs of start/end indices in the abstract) |
| `authors_highlighting_starts_ends`   | array[array] | Highlight ranges per paper (pairs of start/end indices in the author string) |

Each paper object also includes a `has_ranking` field (boolean) and `ranking_score` (float).

**Example**:
```bash
scholarinboxcli search "transformers attention mechanism" --limit 10 --json
```

---

## semantic — Semantic Search

Find papers by semantic similarity using natural language descriptions.

```bash
scholarinboxcli semantic "DESCRIPTION" --limit N --json
```

| Flag       | Required | Description                               |
|------------|----------|-------------------------------------------|
| `DESCRIPTION` | Yes   | Natural language description (positional) |
| `--limit`  | No       | Maximum number of results                 |

**Additional response fields** (compared to keyword search):

| Field            | Type   | Description                                      |
|------------------|--------|--------------------------------------------------|
| `similarity`     | integer| 0-100 similarity score                          |
| `similarity_color`| array  | RGBA color array for UI rendering               |
| `distances`      | float  | Raw distance metric from the embedding model     |

Semantic search understands meaning and context, making it more effective than keyword search
for exploratory queries.

**Example**:
```bash
scholarinboxcli semantic "how attention mechanisms improve vision transformer performance" --limit 5 --json
```

---

## interactions — Interaction History

View reading, liked, and disliked papers.

```bash
scholarinboxcli interactions list --json
```

No additional flags beyond `--json`.

---

## bookmark — Bookmarks

Manage personal bookmarks (stored internally as a "Bookmarks" collection).

### `bookmark list`

List all bookmarked papers.

```bash
scholarinboxcli bookmark list --json
```

**JSON response**:

```json
{
  "success": true,
  "collections": [
    {
      "id": 166105,
      "name": "Bookmarks",
      "isSelected": false,
      "lastSelectionDate": null,
      "permission": "owner",
      "color": "#969696",
      "papers": []
    }
  ]
}
```

The `papers` array contains the same paper objects as other commands.

---

## collection — Collections

Manage paper collections (create, organize, explore).

### `collection list`

List all collections.

```bash
scholarinboxcli collection list --json
```

**JSON response fields** (each collection object):

| Field        | Type   | Description                        |
|--------------|--------|------------------------------------|
| `id`         | integer| Collection ID                      |
| `name`       | string | Collection name                    |
| `uuid`       | string | UUID of the collection             |
| `permission` | string | `"owner"` or `"viewer"`            |
| `color`      | string | Hex color code (e.g., `"#969696"`) |

### `collection create`

Create a new collection.

```bash
scholarinboxcli collection create "NAME"
```

| Argument | Required | Description       |
|----------|----------|-------------------|
| `NAME`   | Yes      | Collection name   |

### `collection rename`

Rename an existing collection.

```bash
scholarinboxcli collection rename "OLD_NAME" "NEW_NAME"
```

| Argument   | Required | Description       |
|------------|----------|-------------------|
| `OLD_NAME` | Yes      | Current name      |
| `NEW_NAME` | Yes      | New name          |

### `collection delete`

Delete a collection.

```bash
scholarinboxcli collection delete "NAME"
```

| Argument | Required | Description       |
|----------|----------|-------------------|
| `NAME`   | Yes      | Collection name   |

### `collection add`

Add papers to a collection by paper ID.

```bash
scholarinboxcli collection add "COLLECTION" PAPER_ID [PAPER_ID2 ...]
```

| Argument     | Required | Description                     |
|--------------|----------|---------------------------------|
| `COLLECTION` | Yes      | Collection name or ID           |
| `PAPER_ID`   | Yes      | One or more paper IDs to add    |

**Example**:
```bash
scholarinboxcli collection add "AIAgents" 10759 4559909
```

### `collection remove`

Remove papers from a collection.

```bash
scholarinboxcli collection remove "COLLECTION" PAPER_ID [PAPER_ID2 ...]
```

| Argument     | Required | Description                        |
|--------------|----------|------------------------------------|
| `COLLECTION` | Yes      | Collection name or ID              |
| `PAPER_ID`   | Yes      | One or more paper IDs to remove    |

### `collection papers`

View papers in a collection.

```bash
scholarinboxcli collection papers "COLLECTION" --json
```

| Argument     | Required | Description       |
|--------------|----------|-------------------|
| `COLLECTION` | Yes      | Collection name   |

### `collection similar`

Get similar paper recommendations based on a collection's content.

```bash
scholarinboxcli collection similar "COLLECTION" --sort FIELD --asc --json
```

| Argument     | Required | Description                                  |
|--------------|----------|----------------------------------------------|
| `COLLECTION` | Yes      | Collection name                              |
| `--sort`     | No       | Sort field (e.g., `year`, `relevance`)       |
| `--asc`      | No       | Sort in ascending order (default: descending)|

**Note**: Results are in the `digest_df` field of the JSON response.

---

## conference — Conference Papers

Explore academic conferences and their papers.

### `conference list`

List available conferences.

```bash
scholarinboxcli conference list --json
```

**JSON response fields** (each conference object):

| Field            | Type   | Description                            |
|------------------|--------|----------------------------------------|
| `conference_id`  | integer| Internal conference ID                 |
| `short_title`    | string | Short name (e.g., `"CVPR 2024"`)       |
| `full_title`     | string | Full name (e.g., `"The IEEE/CVF Conference on Computer Vision and Pattern Recognition 2024"`) |
| `conference_url` | string | URL slug (e.g., `"cvpr/2024"`)         |
| `start_date`     | string | Start date                             |
| `end_date`       | string | End date                               |

### `conference explore`

Explore papers from a specific conference.

```bash
scholarinboxcli conference explore "CONFERENCE_NAME" --json
```

| Argument          | Required | Description         |
|-------------------|----------|---------------------|
| `CONFERENCE_NAME` | Yes      | Conference short title (e.g., `"ICLR 2025"`) |

---

## make_rating — Rate Papers

Rate a paper (like/dislike) via the Scholar Inbox API.

> **Note**: This is a direct API call. The `scholarinboxcli` CLI does not have a built-in `rate` or `make_rating` subcommand. Use `curl` or any HTTP client to call this endpoint.

### Endpoint

```
POST https://api.scholar-inbox.com/api/make_rating/
```

### Request

**Headers**:

| Header          | Required | Description                       |
|-----------------|----------|-----------------------------------|
| `Content-Type`  | Yes      | Must be `application/json`        |
| `X-sha-key`     | Yes      | Your `SCHOLAR_INBOX_SHA_KEY`     |

**Body** (JSON):

| Field   | Type    | Required | Description                                      |
|---------|---------|----------|--------------------------------------------------|
| `rating`| integer | Yes      | `1` = like, `0` = dislike                        |
| `id`    | string  | Yes      | Paper ID (from `_id` field in other API responses) |

### Examples

```bash
# Like a paper (rating: 1)
curl -X POST "https://api.scholar-inbox.com/api/make_rating/" \
  -H "Content-Type: application/json" \
  -H "X-sha-key: $SCHOLAR_INBOX_SHA_KEY" \
  -d '{"rating": 1, "id": "4636621"}'

# Dislike a paper (rating: 0)
curl -X POST "https://api.scholar-inbox.com/api/make_rating/" \
  -H "Content-Type: application/json" \
  -H "X-sha-key: $SCHOLAR_INBOX_SHA_KEY" \
  -d '{"rating": 0, "id": "4636621"}'
```

### Finding Paper IDs

Paper IDs can be found in the `_id` field of paper objects returned by other commands:

```bash
# Get trending papers and extract IDs
scholarinboxcli trending --category ALL --days 7 --json | jq '.digest_df[]._id'
```

---

## Output Modes

| Mode       | Trigger                      | Description                    |
|------------|------------------------------|--------------------------------|
| Interactive| Default (TTY)                | Rich tables via `rich` library |
| JSON       | `--json` flag                | Formatted JSON output          |
| Pipe       | stdout is not a TTY          | Automatic JSON output          |

### Piping with jq

```bash
scholarinboxcli collection list | jq '.'
scholarinboxcli trending --category "Machine Learning" --days 7 | jq '.digest_df[] | .title'
```

---

## Dependencies

- `typer>=0.9.0` — CLI framework
- `httpx>=0.25.0` — HTTP client
- `rich>=13.0.0` — Terminal output formatting

## Configuration

- **Config file**: `~/.config/scholarinboxcli/config.json`
- **API base URL**: Default is the Scholar Inbox API; override with `SCHOLAR_INBOX_API_BASE` env var
