# CLAUDE.md
# Purpose: Make Claude Code an execution-only agent.
# Prompt creation happens in Codex CLI. Claude runs Codex, then executes the resulting plan.

## Operating Mode
You are an execution agent, not a planner.
- Do not rewrite requirements.
- Do not invent missing details.
- If required info is missing, ask ONE targeted question, then stop.
- Make the smallest change that achieves the objective.
- Prefer edits that are easy to review (small diffs, clear commits).
- Never broaden scope without explicit instruction.

## Primary Workflow
We use Codex CLI as the prompt and plan generator.

When the user wants work done, they will provide either:
1) A Codex instruction to generate a Work Packet, or
2) A Work Packet directly.

Your job:
- If a Work Packet is provided, execute it exactly.
- If a Work Packet is NOT provided, run Codex to produce one, then execute it.

## Codex Invocation Rules
If the user message contains one of these triggers, you MUST run Codex:
- `CODEX: ...`
- `MAKE_PACKET: ...`
- `PLAN_WITH_CODEX: ...`

### How to run Codex
Run this command in the repo root (adjust only if user specifies a different path):
- `codex`

Then paste the trigger content into Codex as the prompt.

### What to ask Codex for
In Codex, always request a "Work Packet" that is:
- explicit
- patch-driven where possible
- includes verification steps

Use this exact template in Codex:

Work Packet Template:
- Objective:
- Constraints:
- Repo Context Needed:
- Files in Scope:
- Commands to Run (exact):
- Edits to Make (unified diff or exact search/replace):
- Verification:
- Rollback Plan:
- Expected Output Format:

### Minimal Repo Context to feed Codex
Before opening Codex, gather only what is needed:
- list repo structure: `ls`
- identify relevant files: `find . -maxdepth 3 -type f | head -n 200` (or narrower)
- open relevant files: `sed -n '1,200p' path/to/file`
- read package scripts: `cat package.json` or `pyproject.toml` or `requirements.txt` if applicable
- identify test runner: `npm test`, `pytest`, etc.

Do NOT dump huge files into Codex.
Prefer:
- file paths
- short excerpts
- error messages
- relevant configs

If there is an error, always capture:
- command
- full stderr/stdout

## Execution Rules After Codex Returns a Work Packet
You MUST follow the Work Packet exactly.

### Allowed Actions
- Run terminal commands specified in the Work Packet
- Edit/create files in the repo as specified
- Run ONE additional diagnostic command if something fails (examples: `ls`, `pwd`, `git status`, `cat <file>`, `python -m pytest -q`)
Anything else requires asking permission.

### Disallowed Actions
- Refactoring not requested
- Dependency upgrades unless required for the fix
- Large formatting changes
- Renaming/restructuring without explicit instructions

## Output Format (Always)
Return results in this exact structure:

1) Summary
- What the Work Packet intended
- What you actually did

2) Changes
- Files changed (list)
- Key diffs or description (brief)

3) Commands Run
- Each command and the result (success/failure)

4) Verification
- Tests run, lint, build, manual checks
- Results and any failures

5) Follow-ups
- Only if required
- If blocked, ask ONE targeted question

## Error Handling
If a step fails:
- Stop immediately
- Report:
  - the failing command
  - the full error output
  - what you think caused it (1-2 sentences)
  - the smallest next fix to try
Then ask ONE targeted question if needed.

## Git Hygiene (if repo uses git)
- Check status before and after: `git status`
- Prefer small commits if user asked for commits.
- Do not push unless explicitly instructed.

## Examples

### Example 1: User wants Codex to generate a Work Packet
User: `MAKE_PACKET: Build the a16z static API MVP: parse investment list, generate companies/all.json, publish via GH Pages.`

You:
1. Collect minimal context (repo structure, relevant files, any errors).
2. Run `codex`
3. Paste the request and context into Codex using the template.
4. When Codex outputs a Work Packet, execute it exactly.

### Example 2: User provides a Work Packet
User pastes a Work Packet.

You:
- Execute it exactly, no Codex needed unless the packet is ambiguous.

---

# a16z Static API (YC OSS style) – Claude Agent Plan (Path A)

## Goal
Build a static JSON “API” for a16z’s publicly disclosed investments, similar to yc-oss/api, served via GitHub Pages.

Primary sources (public only):
- Investment List (A–Z): https://a16z.com/investment-list/
- Portfolio browser (for enrichment/classification if extractable): https://a16z.com/portfolio/

This project treats the Investment List as the canonical disclosed roster. The portfolio browser is enrichment and may be incomplete or structurally dynamic.

## Non goals
- No private or paid sources (Crunchbase, PitchBook, etc.).
- No live backend, no database required for serving.
- No claims of completeness beyond what a16z publicly discloses.
- No inference of confidential relationships or undisclosed investments.

## Compliance and Safety
- Check and comply with a16z robots and Terms of Use before crawling.
- Use a clear User Agent string and contact email in UA if appropriate.
- Rate limit requests (start at 1 request per second).
- Avoid aggressive parallelization.
- Fail safely: do not publish partial builds.
- Respect explicit coverage limitations stated on the investment list page (unannounced and non disclosable investments excluded).

---

## Phase 0 – Guardrails and Feasibility
### Tasks
1. Verify crawling is permitted by robots and terms for:
   - Roster page: https://a16z.com/investment-list/
   - Portfolio page: https://a16z.com/portfolio/
2. Define refresh cadence: daily.
3. Draft a Data Contract:
   - Source URLs
   - Field list (public only)
   - Update cadence
   - Coverage limitations and disclaimers
   - Attribution and responsible use notes

### Deliverables
- docs/data-contract.md
- docs/field-list.md
- docs/coverage-notes.md

---

## Phase 1 – Define API Contract and Normalization
### Endpoints (static files)
- /meta.json
- /companies/all.json
- /companies/{slug}.json
- /sectors/{sectorId}.json
- /stages/{stageId}.json
- /statuses/{statusId}.json
- /sources/investment-list.json
- /sources/portfolio.json (only if extractable)

### Canonical Company Schema (minimum viable)
- id: string (stable, e.g. "a16z:{slug}")
- a16z_company_id: string | null (if discoverable from portfolio data)
- name: string
- slug: string
- description: string | null (portfolio card or source snippet if available)
- website: string | null (portfolio card if available)
- status: string | null (enum)
- sectors: string[] (normalized ids)
- stages: string[] (normalized ids)
- source_urls: object
  - investment_list: string
  - portfolio: string | null
- source_evidence: object
  - in_investment_list: boolean
  - in_portfolio: boolean
- first_seen_iso: string
- last_seen_iso: string

### Normalization Rules
- Slugify ids: lowercase, trim, replace spaces with hyphens, remove punctuation, collapse repeated hyphens.
- Stable IDs: id = "a16z:{slug}".
- Sector normalization:
  - Normalize portfolio sector labels to ids.
  - Preserve raw label in a parallel field if needed (e.g. sectors_raw).
- Stage normalization:
  - Normalize portfolio stage labels to controlled ids.
  - Controlled set example: seed, venture, growth, late, public, unknown (final set must match observed labels).
- Status normalization:
  - If portfolio provides an explicit “Active” vs “Exits” split, map to active, exited.
  - Otherwise set unknown.
- Roster and enrichment precedence:
  - Investment list is the canonical roster.
  - Portfolio is enrichment only.
  - Never assume portfolio completeness.

### Deliverables
- schema/company.schema.json
- docs/endpoints.md
- src/normalize/*

---

## Phase 2 – Thin Vertical Slice (Proof of Concept)
### Tasks
1. Implement investment list fetch and parse:
   - Pull first N companies (start with 200 or one letter section) from the roster page.
   - Extract: company name and the roster section letter if available.
   - Produce a stable slug and id for each.
2. Implement portfolio extraction (best effort):
   - Preferred: discover a public JSON feed used by the portfolio page and ingest it.
   - Fallback: Playwright headless render the portfolio page and extract company cards and filter memberships.
   - Extract: name, description, website if visible, plus sector/stage/status membership if represented in UI filters.
3. Merge enrichment into canonical roster:
   - Exact normalized name match first.
   - If ambiguous, quarantine to a review file instead of guessing.
4. Generate static outputs:
   - companies/all.json (slice)
   - companies/{slug}.json per company
   - sectors/{sectorId}.json for at least one extracted sector if available
   - stages/{stageId}.json for at least one extracted stage if available
   - meta.json
5. Publish via GitHub Pages from docs/ or public/.

### Deliverables
- Working GH Pages demo where JSON is accessible via browser/curl
- docs/run-report.md for the slice:
  - roster count parsed
  - portfolio match rate
  - coverage rates for website/description/sector/stage/status

---

## Phase 3 – Production Extractor and Hardening
### Extractor Requirements
- Single entry discovery from the investment list page (primary roster).
- Portfolio enrichment extractor supports:
  - Mode 1: JSON endpoint ingestion (if discovered)
  - Mode 2: Playwright DOM extraction (fallback)
- Rate limit 1 rps with jitter for HTTP fetches.
- Retries with exponential backoff on 429 and transient 5xx.
- Local caching within run to avoid duplicate requests.

### Change Detection
- Store content hash per source URL across runs.
- If unchanged, reuse prior parsed outputs.

### Parser Hardening
- Modular extractors/parsers:
  - src/extract/investmentList.ts
  - src/extract/portfolio.ts
  - src/parse/investmentList.ts
  - src/parse/portfolio.ts
- Logging of extraction completeness per field:
  - percent of companies with website
  - percent with description
  - percent with sector or stage
  - percent with status
- Snapshot tests for known pages to detect layout changes (investment list and portfolio).

### Deliverables
- Test suite for parsing/extraction
- Run report summarizing extraction completeness
- Quarantine report for unmatched/ambiguous company names

---

## Phase 4 – Full Dataset Build + Index Generation
### Tasks
1. Parse full disclosed roster from investment list.
2. Extract portfolio enrichment and merge where possible.
3. Validate every record against schema.
4. Build derived indexes:
   - sectors/{sectorId}.json
   - stages/{stageId}.json
   - statuses/{statusId}.json
5. Generate top level lists:
   - companies/all.json
   - companies/active.json (only if status is reliably extracted)
   - companies/exited.json (only if status is reliably extracted)

### Deliverables
- Full dataset published as static JSON
- Index endpoints populated and validated

---

## Phase 5 – Automation and Safe Publishing
### GitHub Actions
- Daily scheduled workflow + manual dispatch.
- Workflow steps:
  1. Install deps
  2. Run extractors and build into a temp build dir
  3. Validate JSON, schema, and sanity check counts
  4. Atomically replace published directory
  5. Commit outputs (or push to Pages branch)

### Safety
- Do not publish if validation fails.
- Keep last known good build.

### meta.json Requirements
- last_updated_iso
- schema_version
- total_companies
- counts_by_status
- counts_by_sector
- counts_by_stage
- source_entry_urls:
  - investment_list
  - portfolio
- coverage_disclaimer: string (summarize the investment list exclusions)
- extraction_metrics:
  - roster_parsed_count
  - portfolio_match_rate
  - pct_with_website
  - pct_with_description
  - pct_with_sector
  - pct_with_stage
  - pct_with_status

### Deliverables
- .github/workflows/refresh.yml
- docs/meta.json published

---

## Phase 6 – QA and Maintenance
### QA Rules
- Every company must have name, slug, and in_investment_list = true.
- Sector, stage, status may be empty or null; emit warnings and track coverage metrics.
- Every sectorId, stageId, statusId must resolve to an index file.
- Never silently drop companies; if removed from roster, record in a changes report.

### Monitoring
- Detect extraction breaks by:
  - sudden drop in roster count
  - sudden drop in portfolio match rate
  - failed snapshot tests
  - sudden drop in coverage metrics

### Versioning Policy
- Never remove fields without major schema bump.
- Add fields in backward compatible way when possible.

---

## Repo Structure (Recommended)
- src/
  - extract/
  - parse/
  - normalize/
  - build/
  - validate/
- docs/ (published output for GH Pages)
  - meta.json
  - companies/
  - sectors/
  - stages/
  - statuses/
  - sources/
- schema/
- .github/workflows/

---

## Definition of Done
- Daily GH Action produces updated JSON files and publishes to GH Pages.
- /companies/all.json + /companies/{slug}.json resolve correctly.
- Index endpoints (sectors, stages, statuses) are valid and consistent with canonical company records.
- meta.json reflects current counts, last update, and includes coverage disclaimer plus extraction metrics.
- Any portfolio enrichment is strictly additive and never required for core roster correctness.
