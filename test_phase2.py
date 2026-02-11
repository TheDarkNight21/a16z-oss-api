#!/usr/bin/env python3
"""Test script for Phase 2 deliverables."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def test_extract_module():
    try:
        from src.extract.investment_list import InvestmentListExtractor
        print("PASS: InvestmentListExtractor imported")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_parse_module():
    try:
        from src.parse.investment_list import InvestmentListParser
        print("PASS: InvestmentListParser imported")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_normalize_module():
    try:
        from src.normalize.slugify import slugify, make_id
        from src.normalize.company import normalize_company

        assert slugify("Hello World") == "hello-world"
        assert slugify("  Test--Name!! ") == "test-name"
        assert make_id("test") == "a16z:test"

        c = normalize_company({"name": "Test Co"})
        assert c["id"] == "a16z:test-co"
        assert c["slug"] == "test-co"
        assert c["source_evidence"]["in_investment_list"] is True

        print("PASS: normalize modules work correctly")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_basic_parse():
    try:
        from src.parse.investment_list import InvestmentListParser

        parser = InvestmentListParser()
        raw = [{"name": "Test Company", "slug": "test-company", "id": "a16z:test-company"}]
        parsed = parser.parse_companies(raw)
        meta = parser.generate_meta(parsed)

        assert len(parsed) == 1
        assert parsed[0]["id"] == "a16z:test-company"
        assert "total_companies" in meta
        assert meta["total_companies"] == 1

        print(f"PASS: parsing and meta generation work")
        return True
    except Exception as e:
        print(f"FAIL: {e}")
        return False


def test_output_files():
    required = [
        "docs/meta.json",
        "docs/companies/all.json",
        "docs/sources/investment-list.json",
        "docs/sources/portfolio.json",
    ]
    for path in required:
        if not os.path.exists(path):
            print(f"MISSING: {path}")
            return False
        print(f"FOUND: {path}")

    # Validate meta.json has expected fields
    meta = json.load(open("docs/meta.json"))
    assert meta["total_companies"] > 0, "meta.json has 0 companies"
    print(f"PASS: meta.json reports {meta['total_companies']} companies")

    # Validate all.json is non-empty
    companies = json.load(open("docs/companies/all.json"))
    assert len(companies) > 0, "all.json is empty"
    print(f"PASS: all.json has {len(companies)} companies")

    return True


def test_schema_validation():
    try:
        import jsonschema
    except ImportError:
        print("SKIP: jsonschema not installed")
        return True

    schema = json.load(open("schema/company.schema.json"))
    companies = json.load(open("docs/companies/all.json"))

    errors = 0
    for c in companies[:50]:  # Validate first 50
        try:
            jsonschema.validate(c, schema)
        except jsonschema.ValidationError as e:
            print(f"FAIL: {c['name']}: {e.message}")
            errors += 1
    if errors:
        print(f"FAIL: {errors}/50 companies failed schema validation")
        return False
    print(f"PASS: first 50 companies pass schema validation")
    return True


def main():
    print("=== Testing Phase 2 Deliverables ===")
    tests = [
        test_extract_module,
        test_parse_module,
        test_normalize_module,
        test_basic_parse,
        test_output_files,
        test_schema_validation,
    ]
    all_passed = True
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        if not test():
            all_passed = False
    print(f"\n=== {'PASS' if all_passed else 'FAIL'} ===")
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
