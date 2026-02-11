"""Build the static JSON dataset from the a16z investment list + portfolio enrichment."""

import json
import os
import shutil
import sys

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.extract.investment_list import InvestmentListExtractor
from src.extract.portfolio import PortfolioExtractor
from src.parse.investment_list import InvestmentListParser
from src.build.merge import merge_enrichment

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")


def _write_json(path: str, data) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def build(max_companies: int | None = None) -> dict:
    """Run the full extraction→parse→merge→build pipeline.

    Returns a summary dict for the run report.
    """
    print("=== a16z Static API Build ===")

    # --- Step 1: Extract investment list ---
    print("\n[1/6] Extracting investment list...")
    il_extractor = InvestmentListExtractor()
    raw_companies = il_extractor.get_companies(max_companies)
    print(f"       Extracted {len(raw_companies)} raw entries")

    if not raw_companies:
        print("ERROR: No companies extracted. Aborting build.")
        sys.exit(1)

    # --- Step 2: Normalize roster ---
    print("\n[2/6] Normalizing roster companies...")
    parser = InvestmentListParser()
    companies = parser.parse_companies(raw_companies)
    print(f"       Normalized {len(companies)} companies")

    # --- Step 3: Extract portfolio enrichment ---
    print("\n[3/6] Extracting portfolio data...")
    try:
        pf_extractor = PortfolioExtractor()
        portfolio_companies, taxonomy = pf_extractor.get_companies()
        print(f"       Extracted {len(portfolio_companies)} portfolio companies")
        print(f"       Categories: {taxonomy['categories']}")
        print(f"       Stages: {taxonomy['stages']}")
        print(f"       Statuses: {taxonomy['statuses']}")
    except Exception as e:
        print(f"       WARNING: Portfolio extraction failed: {e}")
        print("       Continuing with roster data only.")
        portfolio_companies = []
        taxonomy = {}

    # --- Step 4: Merge enrichment ---
    print("\n[4/6] Merging portfolio enrichment...")
    if portfolio_companies:
        companies, quarantined, merge_stats = merge_enrichment(companies, portfolio_companies)
        print(f"       Matched: {merge_stats['matched']}/{merge_stats['portfolio_count']}")
        print(f"       Match rate: {merge_stats['match_rate']}%")
        print(f"       Quarantined: {merge_stats['unmatched_portfolio']}")
    else:
        quarantined = []
        merge_stats = {"matched": 0, "portfolio_count": 0, "match_rate": 0.0, "unmatched_portfolio": 0}

    # --- Step 5: Generate meta ---
    print("\n[5/6] Generating metadata...")
    meta = parser.generate_meta(companies)
    # Update portfolio match rate in meta
    meta["extraction_metrics"]["portfolio_match_rate"] = merge_stats["match_rate"]

    # --- Step 6: Write output files ---
    print("\n[6/6] Writing static JSON files...")

    # Clean output dirs (keep docs/ root markdown files)
    for subdir in ["companies", "sectors", "stages", "statuses", "sources"]:
        target = os.path.join(OUTPUT_DIR, subdir)
        if os.path.exists(target):
            shutil.rmtree(target)

    # meta.json
    _write_json(os.path.join(OUTPUT_DIR, "meta.json"), meta)
    print("  meta.json")

    # companies/all.json
    _write_json(os.path.join(OUTPUT_DIR, "companies", "all.json"), companies)
    print(f"  companies/all.json ({len(companies)} companies)")

    # companies/{slug}.json
    for company in companies:
        _write_json(
            os.path.join(OUTPUT_DIR, "companies", f"{company['slug']}.json"),
            company,
        )
    print(f"  companies/{{slug}}.json ({len(companies)} files)")

    # Build index maps
    sectors: dict[str, dict] = {}
    stages: dict[str, dict] = {}
    statuses: dict[str, dict] = {}

    for company in companies:
        for sector in company.get("sectors", []):
            if sector not in sectors:
                sectors[sector] = {
                    "id": sector,
                    "name": sector.replace("-", " ").title(),
                    "companies": [],
                }
            sectors[sector]["companies"].append(company["id"])

        for stage in company.get("stages", []):
            if stage not in stages:
                stages[stage] = {
                    "id": stage,
                    "name": stage.replace("-", " ").title(),
                    "companies": [],
                }
            stages[stage]["companies"].append(company["id"])

        status = company.get("status", "unknown")
        if status not in statuses:
            statuses[status] = {
                "id": status,
                "name": status.replace("-", " ").title(),
                "companies": [],
            }
        statuses[status]["companies"].append(company["id"])

    # sectors/{id}.json
    for sid, sdata in sectors.items():
        _write_json(os.path.join(OUTPUT_DIR, "sectors", f"{sid}.json"), sdata)
    print(f"  sectors/ ({len(sectors)} files)")

    # stages/{id}.json
    for sid, sdata in stages.items():
        _write_json(os.path.join(OUTPUT_DIR, "stages", f"{sid}.json"), sdata)
    print(f"  stages/ ({len(stages)} files)")

    # statuses/{id}.json
    for sid, sdata in statuses.items():
        _write_json(os.path.join(OUTPUT_DIR, "statuses", f"{sid}.json"), sdata)
    print(f"  statuses/ ({len(statuses)} files)")

    # sources/
    _write_json(
        os.path.join(OUTPUT_DIR, "sources", "investment-list.json"),
        {
            "url": "https://a16z.com/investment-list/",
            "companies_extracted": len(raw_companies),
        },
    )
    _write_json(
        os.path.join(OUTPUT_DIR, "sources", "portfolio.json"),
        {
            "url": "https://a16z.com/portfolio/",
            "companies_extracted": len(portfolio_companies),
            "matched": merge_stats["matched"],
            "match_rate": merge_stats["match_rate"],
        },
    )
    print("  sources/ (2 files)")

    # Write quarantine file if any
    if quarantined:
        _write_json(
            os.path.join(OUTPUT_DIR, "sources", "quarantine.json"),
            [{"name": q["name"], "slug": q["slug"]} for q in quarantined],
        )
        print(f"  sources/quarantine.json ({len(quarantined)} unmatched)")

    print(f"\n=== Build complete: {len(companies)} companies ===")
    return {
        "roster_parsed_count": len(companies),
        "raw_extracted": len(raw_companies),
        "portfolio_extracted": len(portfolio_companies),
        "merge_stats": merge_stats,
        "meta": meta,
        "sector_count": len(sectors),
        "stage_count": len(stages),
        "status_count": len(statuses),
        "quarantined_count": len(quarantined),
    }


if __name__ == "__main__":
    summary = build()
    print("\nExtraction Metrics:")
    print(json.dumps(summary["meta"]["extraction_metrics"], indent=2))
    print(f"\nMerge Stats:")
    print(json.dumps(summary["merge_stats"], indent=2))
