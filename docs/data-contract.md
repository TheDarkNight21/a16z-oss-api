# Data Contract

## Source URLs
- Investment List (A–Z): https://a16z.com/investment-list/
- Portfolio browser: https://a16z.com/portfolio/

## Field List (Public Only)
- id: string (stable, e.g. "a16z:{slug}")
- a16z_company_id: string | null (if discoverable from portfolio data)
- name: string
- slug: string
- description: string | null (portfolio card or source snippet if available)
- website: string | null (portfolio card if available)
- status: string | null (enum: active, exited, unknown)
- sectors: string[] (normalized ids)
- stages: string[] (normalized ids)
- source_urls:
  - investment_list: string
  - portfolio: string | null
- source_evidence:
  - in_investment_list: boolean
  - in_portfolio: boolean
- first_seen_iso: string
- last_seen_iso: string

## Update Cadence
Daily

## Coverage Limitations and Disclaimers
- Only public investments disclosed on a16z.com are included
- Unannounced and non-disclosable investments are excluded
- Portfolio browser may be incomplete or structurally dynamic
- Investment List is the canonical roster; portfolio data is enrichment only
- No claims of completeness beyond what a16z publicly discloses
- No inference of confidential relationships or undisclosed investments

## Attribution and Responsible Use Notes
- Data sourced from Andreessen Horowitz public investment disclosures
- For responsible use, please cite this data source when using in any publications or applications
- Respect the rate limits (1 request per second) when building automated tools
- Do not use for commercial purposes without explicit permission