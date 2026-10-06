import re
from typing import Any


def normalize_for_comparison(value: Any) -> str:
    """Normalize a value for duplicate comparison."""

    if value is None:
        return ""

    text = str(value).strip().lower()

    # Treat different whitespace as equivalent.
    text = re.sub(r"\s+", " ", text)

    # Remove common punctuation differences.
    text = re.sub(r"[^\w\s]", "", text)

    return text


def create_duplicate_key(record: dict) -> tuple:
    """
    Create a stable key used to identify duplicate records.

    Books are identified using source, title, and author/category.
    Quotes are identified using source, quote text, and author.
    """

    source = normalize_for_comparison(record.get("source"))
    title = normalize_for_comparison(record.get("name_or_title"))
    author = normalize_for_comparison(record.get("author"))
    category = normalize_for_comparison(record.get("category"))

    if source == "books to scrape":
        return (
            source,
            title,
            author,
            category,
        )

    if source == "quotes to scrape":
        return (
            source,
            title,
            author,
        )

    # Generic fallback for an unknown source.
    return (
        source,
        title,
        author,
        category,
    )


def deduplicate_records(records: list[dict]) -> tuple[list[dict], int]:
    """
    Remove duplicate records while preserving the first occurrence.

    Returns:
        tuple[list[dict], int]:
            Unique records and number of duplicates removed.
    """

    unique_records = []
    seen_keys = set()
    duplicate_count = 0

    for record in records:
        key = create_duplicate_key(record)

        if key in seen_keys:
            duplicate_count += 1
            continue

        seen_keys.add(key)
        unique_records.append(record)

    return unique_records, duplicate_count
