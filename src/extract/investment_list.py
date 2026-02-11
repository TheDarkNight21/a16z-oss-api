"""Investment list extractor - fetches and parses a16z.com/investment-list/."""

import random
import time

import requests
from bs4 import BeautifulSoup

from src.normalize.slugify import slugify, make_id

INVESTMENT_LIST_URL = "https://a16z.com/investment-list/"
REQUEST_DELAY_MIN = 0.8
REQUEST_DELAY_MAX = 1.5
USER_AGENT = "a16z-oss-api/1.0 (https://github.com/a16z-oss/api)"


class InvestmentListExtractor:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})

    def fetch_page(self, url: str) -> str:
        delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
        time.sleep(delay)
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.text

    def extract_companies(self, html: str) -> list[dict]:
        """Parse HTML and return list of raw company dicts.

        The page structure:
            <div class="list-row">
                <h4>...</h4>
                <div class="row">
                    <div class="col-xs-6 col-sm-3">
                        <h6>#-A</h6>
                        <ul class="list">
                            <li>CompanyName</li>
                            ...
        """
        soup = BeautifulSoup(html, "html.parser")
        now_iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        companies = []
        seen_slugs: set[str] = set()

        # Find all <ul class="list"> inside list-row sections
        for ul in soup.select("div.list-row ul.list"):
            # Determine the letter group from the preceding <h6>
            letter_group = None
            prev = ul.find_previous_sibling("h6") or ul.find_previous("h6")
            if prev:
                letter_group = prev.get_text(strip=True)

            for li in ul.find_all("li"):
                name = li.get_text(strip=True)
                if not name:
                    continue

                slug = slugify(name)
                if not slug:
                    continue

                # Deduplicate by slug
                if slug in seen_slugs:
                    continue
                seen_slugs.add(slug)

                companies.append(
                    {
                        "name": name,
                        "slug": slug,
                        "id": make_id(slug),
                        "letter_group": letter_group,
                        "source_urls": {
                            "investment_list": INVESTMENT_LIST_URL,
                            "portfolio": None,
                        },
                        "source_evidence": {
                            "in_investment_list": True,
                            "in_portfolio": False,
                        },
                        "first_seen_iso": now_iso,
                        "last_seen_iso": now_iso,
                    }
                )

        return companies

    def get_companies(self, max_companies: int | None = None) -> list[dict]:
        """Fetch and parse the investment list. Returns raw company dicts."""
        html = self.fetch_page(INVESTMENT_LIST_URL)
        companies = self.extract_companies(html)
        if max_companies is not None:
            companies = companies[:max_companies]
        return companies


if __name__ == "__main__":
    extractor = InvestmentListExtractor()
    companies = extractor.get_companies()
    print(f"Extracted {len(companies)} companies")
    for c in companies[:10]:
        print(f"  - {c['name']} ({c['slug']})")
