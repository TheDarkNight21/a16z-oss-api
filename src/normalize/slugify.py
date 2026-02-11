"""Slugification utilities for stable ID generation."""

import re


def slugify(text: str) -> str:
    """Convert text to a URL-safe slug.

    Rules from CLAUDE.md:
    - Lowercase, trim, replace spaces with hyphens
    - Remove punctuation, collapse repeated hyphens
    """
    text = text.lower().strip()
    # Replace spaces and non-alphanumeric chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)
    # Collapse repeated hyphens
    text = re.sub(r'-{2,}', '-', text)
    # Strip leading/trailing hyphens
    text = text.strip('-')
    return text


def make_id(slug: str) -> str:
    """Generate a stable a16z ID from a slug."""
    return f"a16z:{slug}"
