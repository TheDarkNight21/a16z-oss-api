"""Merge portfolio enrichment data into the canonical investment list companies.

Matching strategy:
1. Exact slug match (primary).
2. Quarantine unmatched portfolio companies for review.
"""

from src.normalize.slugify import slugify


def merge_enrichment(
    roster: list[dict],
    portfolio: list[dict],
) -> tuple[list[dict], list[dict], dict]:
    """Merge portfolio data into roster companies.

    Args:
        roster: Canonical investment list companies (normalized).
        portfolio: Portfolio enrichment data from extract/portfolio.py.

    Returns:
        (enriched_companies, quarantined_portfolio, stats)
    """
    # Build lookup from slug -> roster company
    roster_by_slug: dict[str, dict] = {}
    for company in roster:
        roster_by_slug[company["slug"]] = company

    matched = 0
    unmatched_portfolio = []

    for p in portfolio:
        slug = p.get("slug", "")
        if not slug:
            continue

        if slug in roster_by_slug:
            _apply_enrichment(roster_by_slug[slug], p)
            matched += 1
        else:
            unmatched_portfolio.append(p)

    stats = {
        "roster_count": len(roster),
        "portfolio_count": len(portfolio),
        "matched": matched,
        "unmatched_portfolio": len(unmatched_portfolio),
        "match_rate": round(100 * matched / len(portfolio), 1) if portfolio else 0.0,
    }

    return list(roster_by_slug.values()), unmatched_portfolio, stats


def _apply_enrichment(company: dict, portfolio: dict) -> None:
    """Apply portfolio enrichment fields to a canonical company record.

    Portfolio data is additive only — it never overwrites existing
    non-null fields from the investment list.
    """
    # Enrich description
    if not company.get("description") and portfolio.get("description"):
        company["description"] = portfolio["description"]

    # Enrich website
    if not company.get("website") and portfolio.get("website"):
        company["website"] = portfolio["website"]

    # Enrich status (only if currently unknown)
    if company.get("status") in (None, "unknown") and portfolio.get("status"):
        company["status"] = portfolio["status"]

    # Enrich sectors (merge, don't overwrite)
    if portfolio.get("sectors"):
        existing = set(company.get("sectors", []))
        for sector in portfolio["sectors"]:
            if sector not in existing:
                company.setdefault("sectors", []).append(sector)
                existing.add(sector)

    # Enrich stages (merge, don't overwrite)
    if portfolio.get("stages"):
        existing = set(company.get("stages", []))
        for stage in portfolio["stages"]:
            if stage not in existing:
                company.setdefault("stages", []).append(stage)
                existing.add(stage)

    # Enrich a16z_company_id
    if not company.get("a16z_company_id") and portfolio.get("a16z_company_id"):
        company["a16z_company_id"] = portfolio["a16z_company_id"]

    # Mark portfolio evidence
    company.setdefault("source_evidence", {})["in_portfolio"] = True
    company.setdefault("source_urls", {})["portfolio"] = portfolio.get(
        "source_urls", {}
    ).get("portfolio")
