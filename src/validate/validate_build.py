"""Post-build validation: ensure the generated dataset is correct and consistent."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

DOCS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "schema", "company.schema.json")

MIN_COMPANIES = 500  # Sanity check: a16z should have at least this many


def _load(path):
    with open(path) as f:
        return json.load(f)


def validate() -> tuple[bool, list[str]]:
    """Run all validation checks. Returns (passed, list of error messages)."""
    errors = []

    # 1. meta.json exists and is valid
    meta_path = os.path.join(DOCS_DIR, "meta.json")
    if not os.path.exists(meta_path):
        errors.append("meta.json missing")
        return False, errors
    meta = _load(meta_path)

    total = meta.get("total_companies", 0)
    if total < MIN_COMPANIES:
        errors.append(f"total_companies={total} is below minimum {MIN_COMPANIES}")

    # 2. all.json exists and has correct count
    all_path = os.path.join(DOCS_DIR, "companies", "all.json")
    if not os.path.exists(all_path):
        errors.append("companies/all.json missing")
        return False, errors
    companies = _load(all_path)

    if len(companies) != total:
        errors.append(f"all.json has {len(companies)} but meta says {total}")

    # 3. Every company has required fields
    for c in companies:
        if not c.get("name"):
            errors.append(f"Company missing name: {c.get('id', '?')}")
        if not c.get("slug"):
            errors.append(f"Company missing slug: {c.get('name', '?')}")
        if not c.get("id"):
            errors.append(f"Company missing id: {c.get('name', '?')}")
        evidence = c.get("source_evidence", {})
        if not evidence.get("in_investment_list"):
            errors.append(f"Company {c.get('name')} missing in_investment_list=true")

    # 4. Schema validation (sample of 100)
    try:
        import jsonschema
        schema = _load(SCHEMA_PATH)
        for c in companies[:100]:
            try:
                jsonschema.validate(c, schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Schema fail: {c['name']}: {e.message[:80]}")
    except ImportError:
        pass  # jsonschema not available, skip

    # 5. Individual slug files exist for all companies
    missing_slugs = 0
    for c in companies:
        slug_path = os.path.join(DOCS_DIR, "companies", f"{c['slug']}.json")
        if not os.path.exists(slug_path):
            missing_slugs += 1
    if missing_slugs:
        errors.append(f"{missing_slugs} individual company files missing")

    # 6. Index consistency: every sector/stage/status referenced by companies has an index file
    all_sectors = set()
    all_stages = set()
    all_statuses = set()
    for c in companies:
        for s in c.get("sectors", []):
            all_sectors.add(s)
        for s in c.get("stages", []):
            all_stages.add(s)
        status = c.get("status")
        if status:
            all_statuses.add(status)

    for s in all_sectors:
        if not os.path.exists(os.path.join(DOCS_DIR, "sectors", f"{s}.json")):
            errors.append(f"Missing sector index: {s}")
    for s in all_stages:
        if not os.path.exists(os.path.join(DOCS_DIR, "stages", f"{s}.json")):
            errors.append(f"Missing stage index: {s}")
    for s in all_statuses:
        if not os.path.exists(os.path.join(DOCS_DIR, "statuses", f"{s}.json")):
            errors.append(f"Missing status index: {s}")

    passed = len(errors) == 0
    return passed, errors


def main():
    print("=== Validating Build Output ===")
    passed, errors = validate()
    if errors:
        for e in errors:
            print(f"  ERROR: {e}")
    if passed:
        print("\nVALIDATION PASSED")
        return 0
    else:
        print(f"\nVALIDATION FAILED ({len(errors)} errors)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
