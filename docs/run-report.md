# Run Report

## Build Date
2026-02-11

## Sources
- Investment List: https://a16z.com/investment-list/ (canonical roster)
- Portfolio: https://a16z.com/portfolio/ (enrichment via inline JSON)

## Extraction Summary

| Metric | Value |
|--------|-------|
| Roster entries parsed | 1,130 |
| Portfolio entries extracted | 808 |
| Portfolio matched to roster | 648 (80.2%) |
| Quarantined (unmatched) | 160 |
| Companies normalized | 1,130 |

## Output Files

| Path | Count |
|------|-------|
| docs/companies/all.json | 1 (1,130 records) |
| docs/companies/{slug}.json | 1,130 |
| docs/sectors/{id}.json | 12 |
| docs/stages/{id}.json | 3 |
| docs/statuses/{id}.json | 3 |
| docs/sources/*.json | 3 (incl. quarantine) |
| docs/meta.json | 1 |

## Coverage Rates

| Field | Coverage |
|-------|----------|
| name | 100% |
| slug | 100% |
| id | 100% |
| website | 56.1% |
| description | 50.4% |
| sectors | 57.3% |
| stages | 52.0% |
| status (known) | 56.1% |

## Status Breakdown

| Status | Count |
|--------|-------|
| Active | 487 |
| Exited | 147 |
| Unknown | 496 |

## Sectors (from portfolio categories)

| Sector | Companies |
|--------|-----------|
| Enterprise | 196 |
| Seed (fund) | 137 |
| Consumer | 134 |
| AI | 106 |
| Growth (fund) | 103 |
| Crypto | 99 |
| Bio + Health | 77 |
| Infra | 76 |
| Fintech | 76 |
| American Dynamism | 52 |
| Games | 40 |
| CLF | 37 |

## Stages (investment stage)

| Stage | Companies |
|-------|-----------|
| Venture | 405 |
| Seed | 252 |
| Growth | 183 |

## Schema Validation
All 1,130 company records validate against `schema/company.schema.json`.

## Portfolio Match Strategy
- Primary: exact slug match after normalizing both roster and portfolio names.
- 160 portfolio companies did not match any roster entry and were quarantined.
- Common mismatch causes: name suffixes (Inc., .ai, Gaming), abbreviations, and naming variations.

## Notes
- The investment list page is static HTML with `<li>` elements inside `<ul class="list">` sections.
- The portfolio page embeds all data as HTML-entity-encoded JSON in a `data-json` attribute on `<div class="portfolio-app">`.
- Portfolio data is strictly additive (enrichment only). The investment list remains the canonical roster.
- robots.txt returns 404 (no restrictions defined).
