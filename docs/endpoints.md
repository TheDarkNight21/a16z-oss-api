# API Endpoints

## Static JSON Endpoints

### Meta Information
- `/meta.json` - Dataset metadata including counts, timestamps, and coverage metrics

### Company Data
- `/companies/all.json` - All companies in the investment roster
- `/companies/{slug}.json` - Individual company details by slug

### Index Endpoints
- `/sectors/{sectorId}.json` - Sector information by ID
- `/stages/{stageId}.json` - Stage information by ID
- `/statuses/{statusId}.json` - Status information by ID

### Source Data
- `/sources/investment-list.json` - Raw investment list data (if needed)
- `/sources/portfolio.json` - Raw portfolio data (if extractable)

## Endpoint Details

### /meta.json
Contains dataset metadata including:
- last_updated_iso: ISO timestamp of last update
- schema_version: Current schema version
- total_companies: Total number of companies in the roster
- counts_by_status: Company count by status category
- counts_by_sector: Company count by sector
- counts_by_stage: Company count by stage
- source_entry_urls: URLs to primary data sources
- coverage_disclaimer: Summary of investment list exclusions
- extraction_metrics: Extraction completeness metrics

### /companies/all.json
Contains array of all company records in the investment roster with:
- id: Stable identifier in format "a16z:{slug}"
- name: Official company name
- slug: Stable identifier derived from company name
- description: Portfolio description if available
- website: Company website URL if available
- status: Investment status (active, exited, unknown)
- sectors: Normalized sector IDs
- stages: Normalized stage IDs
- source_urls: URLs to investment list and portfolio entries
- source_evidence: Evidence of inclusion in sources
- first_seen_iso: ISO timestamp when first discovered
- last_seen_iso: ISO timestamp when last seen

### /companies/{slug}.json
Individual company record with same fields as `/companies/all.json` but for a specific company identified by slug.

### /sectors/{sectorId}.json
Sector information by ID, including:
- id: Sector identifier
- name: Human-readable sector name
- companies: Array of company IDs in this sector

### /stages/{stageId}.json
Stage information by ID, including:
- id: Stage identifier
- name: Human-readable stage name
- companies: Array of company IDs at this stage

### /statuses/{statusId}.json
Status information by ID, including:
- id: Status identifier
- name: Human-readable status name
- companies: Array of company IDs with this status

### /sources/investment-list.json
Raw data from the investment list page (if needed for debugging or advanced use cases)

### /sources/portfolio.json
Raw data from the portfolio page (if extractable)