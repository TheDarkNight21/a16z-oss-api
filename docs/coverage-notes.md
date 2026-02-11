# Coverage Notes

## Data Sources

### Investment List (Primary)
- URL: https://a16z.com/investment-list/
- Purpose: Canonical roster of all publicly disclosed investments
- Coverage: Complete list of announced investments
- Limitations: Only public disclosures, no private or unannounced investments

### Portfolio Browser (Enrichment)
- URL: https://a16z.com/portfolio/
- Purpose: Additional information about companies in the portfolio
- Coverage: May be incomplete or structurally dynamic
- Limitations: Not all companies may be present, data may change over time

## Field Coverage

### Required Fields (Always Present)
- name: Extracted from investment list
- slug: Generated from name
- id: Generated from slug
- source_urls.investment_list: Direct URL to investment list entry
- source_evidence.in_investment_list: Always true for canonical records
- first_seen_iso: Timestamp when first discovered
- last_seen_iso: Timestamp when last seen

### Enrichment Fields (Optional)
- description: Extracted from portfolio cards where available
- website: Extracted from portfolio cards where available
- status: Inferred from portfolio data or set to "unknown"
- sectors: Extracted from portfolio filters where available
- stages: Extracted from portfolio filters where available

## Data Quality Considerations

### Completeness
- Investment list provides the complete canonical roster
- Portfolio data is enrichment only, not required for core correctness
- Some companies may be missing from portfolio data

### Accuracy
- All data is sourced from publicly available information
- No inference of confidential or undisclosed relationships
- No claims of completeness beyond what is publicly disclosed

### Consistency
- Data normalization rules apply consistently across all records
- Sector, stage, and status values are normalized to controlled vocabularies
- All IDs follow stable naming conventions

## Exclusions

### Unannounced Investments
- Any investment not publicly announced on a16z.com
- Private or confidential relationships

### Non-Disclosable Content
- Information that is not meant for public disclosure
- Proprietary or sensitive data

## Update Cadence

This dataset is updated daily to reflect changes in the a16z investment list and portfolio data.

## Disclaimer

The data provided here represents publicly available information from Andreessen Horowitz's investment disclosures. This is not an official endorsement of any companies, products, or services. The information is provided "as is" without warranty of any kind.