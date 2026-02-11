# Field List

## Required Fields (Mandatory for all records)
- name: string - Company name from investment list
- slug: string - Stable identifier derived from company name
- id: string - Format "a16z:{slug}" for stable identification

## Core Fields (Always Present)
- source_urls:
  - investment_list: string - URL to the investment list entry
- source_evidence:
  - in_investment_list: boolean - Always true for canonical records
- first_seen_iso: string - ISO timestamp when first discovered
- last_seen_iso: string - ISO timestamp of last seen

## Enrichment Fields (Optional)
- description: string | null - Portfolio card description or snippet
- website: string | null - Company website URL
- status: string | null - Status: active, exited, unknown
- sectors: string[] - Normalized sector IDs
- stages: string[] - Normalized stage IDs

## Field Definitions

### name
- Type: string
- Description: The official company name as listed in the investment list
- Required: Yes

### slug
- Type: string
- Description: Stable identifier derived from company name using normalization rules
- Required: Yes

### id
- Type: string
- Description: Stable unique identifier in format "a16z:{slug}"
- Required: Yes

### description
- Type: string | null
- Description: Short description from portfolio card or source snippet
- Required: No

### website
- Type: string | null
- Description: Official company website URL
- Required: No

### status
- Type: string | null
- Description: Current status of investment (active, exited, unknown)
- Required: No

### sectors
- Type: string[]
- Description: List of normalized sector IDs
- Required: No

### stages
- Type: string[]
- Description: List of normalized stage IDs
- Required: No

### source_urls.investment_list
- Type: string
- Description: Direct URL to the investment list entry
- Required: Yes

### source_urls.portfolio
- Type: string | null
- Description: Direct URL to portfolio entry if available
- Required: No

### source_evidence.in_investment_list
- Type: boolean
- Description: Always true for canonical records from investment list
- Required: Yes

### source_evidence.in_portfolio
- Type: boolean
- Description: Whether the company is present in portfolio data (enrichment)
- Required: No

### first_seen_iso
- Type: string
- Description: ISO timestamp when company was first discovered in data set
- Required: Yes

### last_seen_iso
- Type: string
- Description: ISO timestamp when company was last seen in data set
- Required: Yes