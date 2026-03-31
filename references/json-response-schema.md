# scholarinboxcli — JSON Response Schema

This document describes the JSON fields returned by `scholarinboxcli --json` commands. Paper objects
share a common schema across `digest`, `trending`, `search`, `semantic`, `collection papers`, and
`bookmark list` commands.

## Common Paper Object Fields

The following fields appear in the `digest_df` array of most command responses.

### Identity and Metadata

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `paper_id`               | integer       | Internal Scholar Inbox paper ID                   |
| `title`                  | string        | Paper title                                       |
| `authors`                | string        | Comma-separated author list                       |
| `author_details`         | array\|null   | Array of `{author_id, author_name}` objects       |
| `publication_date`       | string        | Date in `YYYY-MM-DD` format                       |
| `display_venue`          | string        | Human-readable venue (e.g., `"NeurIPS 2022"`, `"ArXiv 2026 (March 28)"`) |
| `category`               | string        | Display category (e.g., `"Language"`, `"Machine Learning"`, `"Computer Vision and Graphics"`) |
| `abbreviations`          | string\|null  | Short conference abbreviation (e.g., `"NeurIPS"`, `"AAAI"`) |
| `conference`             | string\|null  | Full conference name                              |
| `conference_year`        | float\|null   | Conference year                                   |
| `conf_id`                | float\|null   | Internal conference ID                            |
| `conference_submission_type` | string\|null | Submission type                             |
| `conference_url`         | string\|null  | Conference URL                                    |

### External Identifiers

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `arxiv_id`               | string\|null  | ArXiv identifier (e.g., `"2203.02155"`)           |
| `semantic_scholar_id`    | string\|null  | Semantic Scholar paper ID                         |
| `arxives_doi`            | string\|null  | DOI for ArXiv papers                              |
| `chemrxiv_id`            | string\|null  | ChemRxiv identifier                               |

### Links and Resources

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `url`                    | string        | Direct PDF link (typically `https://arxiv.org/pdf/...`) |
| `html_link`              | string\|null  | HTML version link (e.g., `https://arxiv.org/html/...` or `https://ar5iv.org/pdf/...`) |
| `github_url`             | string\|null  | Associated GitHub repository URL                  |
| `project_link`           | string\|null  | Project page link                                 |
| `url_for_twitter`        | string\|null  | Pre-formatted share URL for Twitter               |
| `cache_file_name`        | string\|null  | Server-side cached PDF filename                   |
| `is_cached`              | boolean\|null | Whether PDF is cached on the server               |
| `is_cached_filename`     | string\|null  | Server-side cached filename                       |

### Metrics and Engagement

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `citations`              | integer\|null | Citation count (null if not yet available)         |
| `total_read`             | integer       | Number of reads on Scholar Inbox                  |
| `total_likes`            | integer       | Number of likes on Scholar Inbox                  |
| `n_positive_ratings`     | integer       | Positive ratings count                            |
| `n_negative_ratings`     | integer       | Negative ratings count                            |
| `read`                   | boolean       | Whether the current user has read this paper      |
| `bookmarked`             | integer       | Whether bookmarked (0 or 1)                       |
| `rating`                 | string\|null  | User's rating                                     |
| `user_paper_collections` | array\|null   | Collections this paper belongs to                 |

### Content

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `abstract`               | string        | Full abstract text                                |
| `affiliations`           | array\|null   | Array of author affiliation strings               |
| `keywords_metadata`      | object\|null  | Keywords object with `field`, `sub_subfield`, `keywords`, `method_shortname`, `color` |
| `teaser_figures`         | array\|null   | Teaser figure data                                |
| `first_page_image`       | object\|null  | First page preview: `{imageUrl: string}`          |
| `summaries`              | object\|null  | Additional summaries data                         |
| `inferredHighlights`     | array\|null   | Auto-detected key passages: `[{startIndex, endIndex, highlightClass}]` |
| `shortened_authors`      | string\|null  | Truncated author list for display                 |
| `ngt_id`                 | integer\|null | Internal vector search ID                         |

### Color and Visual

| Field                    | Type          | Description                                       |
|--------------------------|---------------|---------------------------------------------------|
| `color`                  | array         | RGBA color array `[R, G, B, A]` for category      |
| `pdf_download_success`   | boolean       | Whether PDF download succeeded on the server      |

## Command-Specific Response Wrappers

### digest

```json
{
  "current_digest_date": "2026-04-01",
  "conf_notification_text": "This digest contains papers from...",
  "custom_digest_range": false,
  "admin_proceedings_msg": "",
  "digest_df": [/* paper objects */]
}
```

### trending

```json
{
  "success": true,
  "digest_df": [/* paper objects with additional fields: */]
}
```

Each trending paper additionally has `digest_date` (epoch ms) and `category`.

### search

```json
{
  "digest_df": [/* paper objects */],
  "abstract_highlighting_starts_ends": [[7, 15, 16, 22, ...]],
  "authors_highlighting_starts_ends": [[], [], []]
}
```

- `abstract_highlighting_starts_ends`: array per paper — flat list of alternating start/end index pairs
  for highlighting matched keywords in the abstract text
- `authors_highlighting_starts_ends`: same format for author name highlighting
- Each paper also has `has_ranking` (boolean) and `ranking_score` (float)

### semantic

Same as search response, plus each paper object includes:

| Field              | Type    | Description                                  |
|--------------------|---------|----------------------------------------------|
| `similarity`       | integer | 0-100 similarity score                      |
| `similarity_color` | array   | RGBA color array for similarity visualization |
| `distances`        | float   | Raw embedding distance from query            |

### collection list

```json
{
  "success": true,
  "collections": [
    {
      "id": 166105,
      "name": "Collection Name",
      "uuid": "58042854-43ea-4cef-95e2-6178dc3acd69",
      "permission": "owner",
      "selected": false,
      "color": "#969696"
    }
  ]
}
```

### bookmark list

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
      "papers": [/* paper objects */]
    }
  ]
}
```

### conference list

```json
{
  "conferences": [
    {
      "conference_id": 1,
      "short_title": "CVPR 2023",
      "full_title": "The IEEE/CVF Conference on Computer Vision and Pattern Recognition 2023",
      "conference_url": "cvpr/2023",
      "start_date": "18-06-2023",
      "end_date": "22-06-2023"
    }
  ]
}
```

### auth status

```json
{
  "is_admin": false,
  "is_logged_in": true,
  "name": "User Name",
  "onboarding_status": "finished_fast_track",
  "profile_picture": null,
  "sha_key": "abcdef123456...",
  "user_id": 45859
}
```

## Category Name Mapping

The `category` field in responses uses display names (not ArXiv codes):

| Display Name                     | Likely ArXiv Areas               |
|----------------------------------|----------------------------------|
| `Language`                       | cs.CL, cs.AI                     |
| `Machine Learning`               | cs.LG, stat.ML                   |
| `Computer Vision and Graphics`   | cs.CV, cs.GR                     |
| `Artificial Intelligence`        | cs.AI                            |
| `Robotics`                       | cs.RO                            |
| `Sound and Audio Processing`     | eess.AS, cs.SD                   |
| `Interdisciplinary`              | Various                          |
