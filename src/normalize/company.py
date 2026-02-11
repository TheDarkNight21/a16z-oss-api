"""Company normalization: apply schema defaults and normalize fields."""

from datetime import datetime, timezone
from typing import Any

from src.normalize.slugify import slugify, make_id


def normalize_company(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize a raw company dict into canonical schema form.

    Requires at minimum: name (string).
    Generates slug and id if not present.
    Fills defaults for all optional fields.
    """
    name = raw.get("name", "").strip()
    if not name:
        raise ValueError("Company must have a non-empty name")

    slug = raw.get("slug") or slugify(name)
    company_id = raw.get("id") or make_id(slug)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return {
        "id": company_id,
        "a16z_company_id": raw.get("a16z_company_id"),
        "name": name,
        "slug": slug,
        "description": raw.get("description"),
        "website": raw.get("website"),
        "status": raw.get("status", "unknown"),
        "sectors": raw.get("sectors", []),
        "stages": raw.get("stages", []),
        "source_urls": {
            "investment_list": raw.get("source_urls", {}).get(
                "investment_list", "https://a16z.com/investment-list/"
            ),
            "portfolio": raw.get("source_urls", {}).get("portfolio"),
        },
        "source_evidence": {
            "in_investment_list": raw.get("source_evidence", {}).get(
                "in_investment_list", True
            ),
            "in_portfolio": raw.get("source_evidence", {}).get(
                "in_portfolio", False
            ),
        },
        "first_seen_iso": raw.get("first_seen_iso", now_iso),
        "last_seen_iso": raw.get("last_seen_iso", now_iso),
    }
