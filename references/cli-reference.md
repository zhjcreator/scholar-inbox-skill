# CLI Reference

## Command Syntax

### Authentication

```bash
scholarinboxcli auth login --url "https://..."
scholarinboxcli auth status
scholarinboxcli auth logout
```

### Digest

```bash
scholarinboxcli digest [--date MM-DD-YYYY] [--json]
```

### Trending

```bash
scholarinboxcli trending
    [--category "Machine Learning"]
    [--days 30]
    [--sort hype|citations]
    [--asc|--desc]
    [--json]
```

### Search

```bash
scholarinboxcli search "query" [--limit N] [--offset N] [--json]
scholarinboxcli semantic "query" [--file path] [--limit N] [--json]
```

### Rate Papers *(fork only)*

```bash
scholarinboxcli rate PAPER_ID {1|-1|0}
```

- `1` = upvote, `-1` = downvote, `0` = remove rating

### Bookmarks

```bash
scholarinboxcli bookmark list [--json]
scholarinboxcli bookmark add PAPER_ID
scholarinboxcli bookmark remove PAPER_ID
```

### Collections

```bash
scholarinboxcli collection list [--expanded] [--json]
scholarinboxcli collection create "Name"
scholarinboxcli collection papers "Name|id" [--json]
scholarinboxcli collection add "Name|id" PAPER_ID
scholarinboxcli collection remove "Name|id" PAPER_ID
scholarinboxcli collection rename "Old" "New"
scholarinboxcli collection delete "Name|id"
scholarinboxcli collection similar "Name|id" [...] [--sort year|title] [--asc|--desc] [--json]
```

### Conferences

```bash
scholarinboxcli conference list [--json]
scholarinboxcli conference explore [--json]
```

### Interactions

```bash
scholarinboxcli interactions [--type up|down|all|read] [--json]
```
