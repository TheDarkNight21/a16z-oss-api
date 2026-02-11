#!/usr/bin/env python3
"""Test script for Phase 0 deliverables."""

import json
import os


def test_docs_exist():
    required_docs = [
        "docs/data-contract.md",
        "docs/field-list.md",
        "docs/coverage-notes.md",
    ]
    for doc in required_docs:
        if not os.path.exists(doc):
            print(f"MISSING: {doc}")
            return False
        print(f"FOUND: {doc}")
    return True


def test_schema_exists():
    schema_file = "schema/company.schema.json"
    if not os.path.exists(schema_file):
        print(f"MISSING: {schema_file}")
        return False
    print(f"FOUND: {schema_file}")
    with open(schema_file) as f:
        schema = json.load(f)
    if not schema.get("properties"):
        print(f"EMPTY or malformed schema: {schema_file}")
        return False
    print(f"VALID: {schema_file} ({len(schema['properties'])} properties)")
    return True


def test_src_structure():
    required_dirs = [
        "src/extract",
        "src/parse",
        "src/normalize",
        "src/build",
        "src/validate",
    ]
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            print(f"MISSING: {dir_path}")
            return False
        print(f"FOUND: {dir_path}")
    return True


def main():
    print("=== Testing Phase 0 Deliverables ===")
    tests = [test_docs_exist, test_schema_exists, test_src_structure]
    all_passed = True
    for test in tests:
        print(f"\n--- {test.__name__} ---")
        if not test():
            all_passed = False
    print(f"\n=== {'PASS' if all_passed else 'FAIL'} ===")
    return 0 if all_passed else 1


if __name__ == "__main__":
    exit(main())
