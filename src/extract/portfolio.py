"""Portfolio extractor - fetches a16z.com/portfolio/ and extracts inline JSON data.

The portfolio page embeds all company data as HTML-entity-encoded JSON in a
<div class="portfolio-app" data-json="..."> attribute. This module extracts
and normalizes that data.
"""

import json
import random
import re
import time
from html import unescape
from typing import Any

import requests

from src.normalize.slugify import slugify

PORTFOLIO_URL = "https://a16z.com/portfolio/"
USER_AGENT = "a16z-oss-api/1.0 (https://github.com/a16z-oss/api)"
REQUEST_DELAY_MIN = 0.8
REQUEST_DELAY_MAX = 1.5

# Map raw stage labels to our controlled vocabulary
STAGE_MAP = {
    "seed": "seed",
    "venture": "venture",
    "growth": "growth",
    "late": "late",
    "ipo": "public",
    "m&a": "exited",
    "spac": "public",
}

# Map raw status labels to our controlled vocabulary
STATUS_MAP = {
    "active": "active",
    "exits": "exited",
}


def _normalize_stage(raw: str) -> str:
    """Normalize a raw stage label to our controlled vocabulary."""
    return STAGE_MAP.get(raw.lower().strip(), "unknown")


def _normalize_status(raw: str) -> str | None:
    """Normalize a raw status label."""
    raw = raw.lower().strip()
    return STATUS_MAP.get(raw)


def _split_semicolons(value: str) -> list[str]:
    """Split a semicolon-delimited string into trimmed parts."""
    return [p.strip() for p in value.split(";") if p.strip()]


class PortfolioExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_page(self, url: str) -> str:
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    def extract_data(self, html: str) -> dict[str, Any]:
        """Extract the full portfolio data blob from the page HTML.

        Returns dict with keys: companies, categories, stages, statuses, etc.
        """
        match = re.search(r'<div class="portfolio-app" data-json="([^"]+)"', html)
        if not match:
            raise ValueError("Could not find portfolio-app data-json attribute")

        raw = match.group(1)
        decoded = unescape(raw)
        return json.loads(decoded)

    def normalize_company(self, raw: dict[str, Any]) -> dict[str, Any]:
        """Normalize a single raw portfolio company into enrichment data.

        Returns a dict with fields ready to merge into the canonical schema.
        """
        name = (raw.get("a16z_company_name") or raw.get("post_title") or "").strip()
        if not name:
            return {}

        # Status: prefer website_current_status
        raw_status = (raw.get("website_current_status") or "").strip()
        # Handle "Exits;Active" edge case - take first
        if ";" in raw_status:
            raw_status = raw_status.split(";")[0].strip()
        status = _normalize_status(raw_status)

        # Stages: from website_stage_at_investment (semicolon-separated)
        raw_stages = raw.get("website_stage_at_investment") or ""
        stages = []
        for part in _split_semicolons(raw_stages):
            normalized = _normalize_stage(part)
            if normalized and normalized not in stages:
                stages.append(normalized)

        # Sectors: from website_categories (semicolon-separated)
        raw_cats = raw.get("website_categories") or ""
        sectors = []
        for part in _split_semicolons(raw_cats):
            sector_slug = slugify(part)
            if sector_slug and sector_slug not in sectors:
                sectors.append(sector_slug)

        # Sectors raw labels (for display names)
        sectors_raw = _split_semicolons(raw_cats)

        return {
            "name": name,
            "slug": slugify(name),
            "a16z_company_id": str(raw.get("ID", "")),
            "description": (raw.get("website_description") or "").strip() or None,
            "website": (raw.get("company_url") or "").strip() or None,
            "status": status,
            "sectors": sectors,
            "sectors_raw": sectors_raw,
            "stages": stages,
            "logo_url": (raw.get("logo") or "").strip() or None,
            "founders": (raw.get("founders_list") or "").strip() or None,
            "source_urls": {
                "portfolio": PORTFOLIO_URL,
            },
        }

    def get_companies(self) -> tuple[list[dict], dict]:
        """Fetch and parse portfolio page.

        Returns:
            (list of normalized portfolio companies, raw taxonomy metadata)
        """
        html = self.fetch_page(PORTFOLIO_URL)
        data = self.extract_data(html)

        companies = []
        for raw in data.get("companies", []):
            normalized = self.normalize_company(raw)
            if normalized and normalized.get("name"):
                companies.append(normalized)

        taxonomy = {
            "categories": data.get("categories", []),
            "stages": data.get("stages", []),
            "statuses": data.get("statuses", []),
        }

        return companies, taxonomy


if __name__ == "__main__":
    extractor = PortfolioExtractor()
    companies, taxonomy = extractor.get_companies()
    print(f"Extracted {len(companies)} portfolio companies")
    print(f"Categories: {taxonomy['categories']}")
    print(f"Stages: {taxonomy['stages']}")
    print(f"Statuses: {taxonomy['statuses']}")
    for c in companies[:5]:
        print(f"  - {c['name']}: status={c['status']}, sectors={c['sectors']}, stages={c['stages']}")
