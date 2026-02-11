#!/usr/bin/env python3
"""
Demo build script - generates static JSON files for Phase 2
"""

import os
import sys
import json
import time
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_demo_data():
    """Create demo data for our thin vertical slice"""

    # Create sample companies (simulating what we'd get from parsing)
    sample_companies = [
        {
            "name": "OpenAI",
            "slug": "openai",
            "id": "a16z:openai",
            "description": "Artificial intelligence research and deployment",
            "website": "https://www.openai.com",
            "status": "active",
            "sectors": ["artificial-intelligence"],
            "stages": ["venture"],
            "source_urls": {
                "investment_list": "https://a16z.com/investment-list/",
                "portfolio": "https://a16z.com/portfolio/"
            },
            "source_evidence": {
                "in_investment_list": True,
                "in_portfolio": True
            },
            "first_seen_iso": "2023-01-01T00:00:00Z",
            "last_seen_iso": "2023-01-01T00:00:00Z"
        },
        {
            "name": "Stripe",
            "slug": "stripe",
            "id": "a16z:stripe",
            "description": "Online payment processing",
            "website": "https://stripe.com",
            "status": "active",
            "sectors": ["fintech"],
            "stages": ["venture"],
            "source_urls": {
                "investment_list": "https://a16z.com/investment-list/",
                "portfolio": "https://a16z.com/portfolio/"
            },
            "source_evidence": {
                "in_investment_list": True,
                "in_portfolio": True
            },
            "first_seen_iso": "2023-01-01T00:00:00Z",
            "last_seen_iso": "2023-01-01T00:00:00Z"
        },
        {
            "name": "Rust",
            "slug": "rust",
            "id": "a16z:rust",
            "description": "Systems programming language",
            "website": "https://www.rust-lang.org",
            "status": "active",
            "sectors": ["software-development"],
            "stages": ["seed"],
            "source_urls": {
                "investment_list": "https://a16z.com/investment-list/",
                "portfolio": "https://a16z.com/portfolio/"
            },
            "source_evidence": {
                "in_investment_list": True,
                "in_portfolio": True
            },
            "first_seen_iso": "2023-01-01T00:00:00Z",
            "last_seen_iso": "2023-01-01T00:00:00Z"
        }
    ]

    return sample_companies

def build_static_files():
    """Build all static JSON files for demo"""

    # Create output directory
    os.makedirs('docs', exist_ok=True)
    os.makedirs('docs/companies', exist_ok=True)
    os.makedirs('docs/sectors', exist_ok=True)
    os.makedirs('docs/stages', exist_ok=True)
    os.makedirs('docs/statuses', exist_ok=True)
    os.makedirs('docs/sources', exist_ok=True)

    # Create sample data
    companies = create_demo_data()

    # Parse companies (normalize) - simulate the parsing process
    parsed_companies = []
    for company in companies:
        # Simple normalization (in a real app we'd use the parser class)
        normalized = company.copy()
        normalized['first_seen_iso'] = "2023-01-01T00:00:00Z"
        normalized['last_seen_iso'] = "2023-01-01T00:00:00Z"

        # Add default values for missing fields
        if 'description' not in normalized:
            normalized['description'] = None
        if 'website' not in normalized:
            normalized['website'] = None
        if 'status' not in normalized:
            normalized['status'] = 'unknown'
        if 'sectors' not in normalized:
            normalized['sectors'] = []
        if 'stages' not in normalized:
            normalized['stages'] = []

        parsed_companies.append(normalized)

    # Generate meta
    status_counts = {}
    sector_counts = {}
    stage_counts = {}

    for company in parsed_companies:
        # Status counts
        status = company.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1

        # Sector counts (simplified)
        sectors = company.get('sectors', [])
        for sector in sectors:
            sector_counts[sector] = sector_counts.get(sector, 0) + 1

        # Stage counts (simplified)
        company_stages = company.get('stages', [])
        for stage in company_stages:
            stage_counts[stage] = stage_counts.get(stage, 0) + 1

    meta = {
        "last_updated_iso": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
        "schema_version": "1.0.0",
        "total_companies": len(parsed_companies),
        "counts_by_status": status_counts,
        "counts_by_sector": sector_counts,
        "counts_by_stage": stage_counts,
        "source_entry_urls": {
            "investment_list": "https://a16z.com/investment-list/",
            "portfolio": "https://a16z.com/portfolio/"
        },
        "coverage_disclaimer": "This dataset includes publicly disclosed investments from a16z's investment list. Some companies may be missing from portfolio data.",
        "extraction_metrics": {
            "roster_parsed_count": len(parsed_companies),
            "portfolio_match_rate": 0.0,
            "pct_with_website": 100.0,
            "pct_with_description": 100.0,
            "pct_with_sector": 100.0,
            "pct_with_stage": 100.0,
            "pct_with_status": 100.0
        }
    }

    # Write all files
    print("Writing static JSON files...")

    # 1. Meta file
    with open('docs/meta.json', 'w') as f:
        json.dump(meta, f, indent=2)
    print("✅ docs/meta.json created")

    # 2. All companies
    with open('docs/companies/all.json', 'w') as f:
        json.dump(parsed_companies, f, indent=2)
    print("✅ docs/companies/all.json created")

    # 3. Individual company files
    for company in parsed_companies:
        filename = f"docs/companies/{company['slug']}.json"
        with open(filename, 'w') as f:
            json.dump(company, f, indent=2)
        print(f"✅ docs/companies/{company['slug']}.json created")

    # 4. Index files (simplified)
    sectors = {}
    stages = {}
    statuses = {}

    for company in parsed_companies:
        # Sectors
        for sector in company.get('sectors', []):
            if sector not in sectors:
                sectors[sector] = {'id': sector, 'name': sector.replace('-', ' ').title(), 'companies': []}
            sectors[sector]['companies'].append(company['id'])

        # Stages
        for stage in company.get('stages', []):
            if stage not in stages:
                stages[stage] = {'id': stage, 'name': stage.replace('-', ' ').title(), 'companies': []}
            stages[stage]['companies'].append(company['id'])

        # Statuses
        status = company.get('status', 'unknown')
        if status not in statuses:
            statuses[status] = {'id': status, 'name': status.replace('-', ' ').title(), 'companies': []}
        statuses[status]['companies'].append(company['id'])

    # Write sector files
    for sector_id, sector_data in sectors.items():
        with open(f'docs/sectors/{sector_id}.json', 'w') as f:
            json.dump(sector_data, f, indent=2)
        print(f"✅ docs/sectors/{sector_id}.json created")

    # Write stage files
    for stage_id, stage_data in stages.items():
        with open(f'docs/stages/{stage_id}.json', 'w') as f:
            json.dump(stage_data, f, indent=2)
        print(f"✅ docs/stages/{stage_id}.json created")

    # Write status files
    for status_id, status_data in statuses.items():
        with open(f'docs/statuses/{status_id}.json', 'w') as f:
            json.dump(status_data, f, indent=2)
        print(f"✅ docs/statuses/{status_id}.json created")

    # Write source files (simplified)
    with open('docs/sources/investment-list.json', 'w') as f:
        json.dump({"url": "https://a16z.com/investment-list/"}, f, indent=2)
    print("✅ docs/sources/investment-list.json created")

    with open('docs/sources/portfolio.json', 'w') as f:
        json.dump({"url": "https://a16z.com/portfolio/"}, f, indent=2)
    print("✅ docs/sources/portfolio.json created")

    print("\n🎉 Demo build completed successfully!")
    return True

def main():
    """Main build function"""
    print("Starting demo build...")
    try:
        build_static_files()
        print("\n✅ Demo build finished!")
        return 0
    except Exception as e:
        print(f"❌ Error during build: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())