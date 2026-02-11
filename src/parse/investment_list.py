"""Investment list parser - normalizes raw extracted company data."""

import json
from datetime import datetime, timezone
from typing import Any

from src.normalize.company import normalize_company


class InvestmentListParser:
    def __init__(self):
        pass

    def parse_companies(self, raw_companies: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize a list of raw company dicts into canonical schema form."""
        parsed = []
        errors = []
        for raw in raw_companies:
            try:
                company = normalize_company(raw)
                parsed.append(company)
            except Exception as e:
                errors.append({"name": raw.get("name", "unknown"), "error": str(e)})
        if errors:
            print(f"WARNING: {len(errors)} companies failed normalization:")
            for err in errors[:5]:
                print(f"  - {err['name']}: {err['error']}")
        return parsed

    def generate_meta(self, companies: list[dict[str, Any]]) -> dict[str, Any]:
        """Generate meta.json content from a list of normalized companies."""
        status_counts: dict[str, int] = {}
        sector_counts: dict[str, int] = {}
        stage_counts: dict[str, int] = {}
        total = len(companies)

        n_website = 0
        n_description = 0
        n_sector = 0
        n_stage = 0
        n_status = 0

        for c in companies:
            status = c.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
            if status and status != "unknown":
                n_status += 1

            for sector in c.get("sectors", []):
                sector_counts[sector] = sector_counts.get(sector, 0) + 1
            if c.get("sectors"):
                n_sector += 1

            for stage in c.get("stages", []):
                stage_counts[stage] = stage_counts.get(stage, 0) + 1
            if c.get("stages"):
                n_stage += 1

            if c.get("website"):
                n_website += 1
            if c.get("description"):
                n_description += 1

        pct = lambda n: round(100 * n / total, 1) if total else 0.0

        return {
            "last_updated_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "schema_version": "1.0.0",
            "total_companies": total,
            "counts_by_status": status_counts,
            "counts_by_sector": sector_counts,
            "counts_by_stage": stage_counts,
            "source_entry_urls": {
                "investment_list": "https://a16z.com/investment-list/",
                "portfolio": "https://a16z.com/portfolio/",
            },
            "coverage_disclaimer": (
                "This dataset includes only publicly disclosed investments from "
                "a16z's investment list. Investments that are not publicly announced "
                "or not disclosable are excluded."
            ),
            "extraction_metrics": {
                "roster_parsed_count": total,
                "portfolio_match_rate": 0.0,
                "pct_with_website": pct(n_website),
                "pct_with_description": pct(n_description),
                "pct_with_sector": pct(n_sector),
                "pct_with_stage": pct(n_stage),
                "pct_with_status": pct(n_status),
            },
        }
