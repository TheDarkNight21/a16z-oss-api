# Run Report – Phase 2 Thin Vertical Slice

## Build Date
2026-02-11T03:18:27Z

## Source
- Investment List: https://a16z.com/investment-list/
- Portfolio: Not yet implemented (enrichment phase)

## Extraction Summary

| Metric | Value |
|--------|-------|
| Roster entries parsed | 1,130 |
| Companies normalized | 1,130 |
| Normalization errors | 0 |
| Duplicate slugs deduplicated | 0 |

## Output Files

| Path | Count |
|------|-------|
| docs/companies/all.json | 1 (1,130 records) |
| docs/companies/{slug}.json | 1,130 |
| docs/sectors/{id}.json | 0 (no portfolio enrichment yet) |
| docs/stages/{id}.json | 0 (no portfolio enrichment yet) |
| docs/statuses/{id}.json | 1 (unknown) |
| docs/sources/*.json | 2 |
| docs/meta.json | 1 |

## Coverage Rates

| Field | Coverage |
|-------|----------|
| name | 100% |
| slug | 100% |
| id | 100% |
| website | 0% (requires portfolio enrichment) |
| description | 0% (requires portfolio enrichment) |
| sectors | 0% (requires portfolio enrichment) |
| stages | 0% (requires portfolio enrichment) |
| status | 0% known (all "unknown"; requires portfolio enrichment) |

## Portfolio Match Rate
0% – portfolio extraction not yet implemented.

## Schema Validation
All 1,130 company records validate against `schema/company.schema.json`.

## Notes
- The investment list page contains 1,130 publicly disclosed investments.
- Company names are extracted from `<li>` elements inside `<ul class="list">` within `<div class="list-row">` sections.
- All enrichment fields (website, description, sectors, stages, status) are null/empty since only the investment list is parsed in this phase.
- Portfolio enrichment (Phase 3+) will improve coverage for these fields.
- robots.txt returns 404 (no restrictions defined).
