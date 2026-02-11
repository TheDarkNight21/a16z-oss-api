#!/usr/bin/env python3
"""a16z OSS API - Static JSON API for Andreessen Horowitz investments."""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from src.build.build_dataset import build


def main():
    summary = build()
    print(f"\nDone. {summary['roster_parsed_count']} companies built.")


if __name__ == "__main__":
    main()
