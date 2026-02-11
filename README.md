# a16z OSS API

Static JSON API for Andreessen Horowitz's publicly disclosed investments. Data is sourced by parsing the public investment list at `https://a16z.com/investment-list/` and enriching with portfolio data from `https://a16z.com/portfolio/`. The build outputs live in `docs/` for GitHub Pages hosting.

## Metadata

Current dataset metadata (from `docs/meta.json`):

- API endpoint: `https://thedarknight21.github.io/a16z-oss-api/meta.json`
- Last updated (ISO): `2026-02-11T03:37:53Z`
- Schema version: `1.0.0`
- Total companies: `1130`
- Portfolio match rate: `80.2%`
- Counts by status:
  - active: `487`
  - exited: `147`
  - unknown: `496`
- Counts by sector:
  - enterprise: `196`
  - seed: `137`
  - consumer: `134`
  - ai: `106`
  - growth: `103`
  - crypto: `99`
  - bio-health: `77`
  - infra: `76`
  - fintech: `76`
  - american-dynamism: `52`
  - games: `40`
  - clf: `37`
- Counts by stage:
  - venture: `405`
  - seed: `252`
  - growth: `183`

## APIs

All endpoints serve static JSON files via GitHub Pages.

Base URL: `https://thedarknight21.github.io/a16z-oss-api/`

- `GET /meta.json`
- `GET /companies/all.json`
- `GET /companies/{slug}.json`
- `GET /sectors/{sectorId}.json`
- `GET /stages/{stageId}.json` (seed, venture, growth)
- `GET /statuses/{statusId}.json` (active, exited, unknown)
- `GET /sources/investment-list.json`
- `GET /sources/portfolio.json`

## Schema

Company records follow `schema/company.schema.json`.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Stable identifier in the form `a16z:{slug}`. |
| `a16z_company_id` | string or null | a16z's internal company ID from the portfolio page. |
| `name` | string | Company name as listed on the investment list. |
| `slug` | string | URL-safe slug derived from the company name. |
| `description` | string or null | Short description from the portfolio page. |
| `website` | string (uri) or null | Company website URL. |
| `status` | string or null | Investment status: `active`, `exited`, or `unknown`. |
| `sectors` | array of string | Normalized sector IDs (e.g. `enterprise`, `ai`, `crypto`). |
| `stages` | array of string | Investment stage IDs: `seed`, `venture`, `growth`. |
| `source_urls` | object | URLs from which this record was sourced. |
| `source_urls.investment_list` | string | URL to the a16z investment list page. |
| `source_urls.portfolio` | string or null | URL to the portfolio page, if matched. |
| `source_evidence` | object | Evidence of inclusion in each source. |
| `source_evidence.in_investment_list` | boolean | Always `true` for canonical roster entries. |
| `source_evidence.in_portfolio` | boolean | Whether the company was found in portfolio data. |
| `first_seen_iso` | string | ISO 8601 timestamp when first discovered. |
| `last_seen_iso` | string | ISO 8601 timestamp when last seen. |

## Usage

### Via HTTP (no clone needed)

The API is live at `https://thedarknight21.github.io/a16z-oss-api/`. Fetch any endpoint directly:

```bash
# Get all companies
curl https://thedarknight21.github.io/a16z-oss-api/companies/all.json

# Get a single company
curl https://thedarknight21.github.io/a16z-oss-api/companies/openai.json

# Get metadata
curl https://thedarknight21.github.io/a16z-oss-api/meta.json

# Filter by sector, stage, or status
curl https://thedarknight21.github.io/a16z-oss-api/sectors/ai.json
curl https://thedarknight21.github.io/a16z-oss-api/stages/venture.json
curl https://thedarknight21.github.io/a16z-oss-api/statuses/active.json
```

### Local (clone the repo)

```bash
git clone https://github.com/TheDarkNight21/a16z-oss-api.git
cd a16z-oss-api
```

All data is in `docs/` -- no build step needed:

```bash
# Read locally with jq
cat docs/companies/all.json | jq '.[0]'
cat docs/companies/stripe.json | jq '.name, .website, .sectors'

# Use in Python
python -c "import json; data = json.load(open('docs/companies/all.json')); print(len(data), 'companies')"
```

To rebuild the dataset from scratch:

```bash
pip install -r requirements.txt
python main.py
```

## How It Works

1. **Investment list extractor** parses the canonical roster from `a16z.com/investment-list/` (static HTML with `<li>` entries).
2. **Portfolio extractor** pulls enrichment data from `a16z.com/portfolio/` (inline JSON embedded in the page).
3. **Merger** matches portfolio companies to roster entries by slug (80.2% match rate). Unmatched entries are quarantined.
4. **Build** generates normalized static JSON files in `docs/`.
5. **GitHub Pages** serves the `docs/` output as a static API.
6. **Daily GitHub Actions workflow** refreshes the data automatically.

## Data Sources

- **Investment List** (primary roster): `https://a16z.com/investment-list/`
- **Portfolio** (enrichment): `https://a16z.com/portfolio/`

Only publicly disclosed investments are included. Unannounced and non-disclosable investments are excluded per a16z's stated policy.

## License / Attribution

This project aggregates publicly available information from Andreessen Horowitz's investment disclosures. Source: `https://a16z.com/investment-list/`
