import re
from typing import Any
from urllib.parse import urlparse


RATING_MAP = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
}


def clean_text(value: Any) -> str | None:
    """Normalize whitespace and common text encoding issues."""

    if value is None:
        return None

    text = str(value)

    # Fix common UTF-8/Latin-1 mojibake.
    replacements = {
        "Â£": "£",
        "Â€": "€",
        "Â": "",
        "â€™": "'",
        "â€œ": '"',
        "â€\x9d": '"',
        "â€“": "-",
        "â€”": "-",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Normalize whitespace.
    text = re.sub(r"\s+", " ", text).strip()

    return text or None


def clean_price(value: Any) -> float | None:
    """Convert a price such as '£51.77' into a float."""

    if value is None:
        return None

    text = clean_text(value)

    if not text:
        return None

    # Remove currency symbols and other non-numeric characters.
    text = text.replace(",", "")

    match = re.search(r"-?\d+(?:\.\d+)?", text)

    if not match:
        return None

    try:
        return float(match.group())
    except ValueError:
        return None


def clean_rating(value: Any) -> int | None:
    """Normalize ratings into an integer from 1 to 5."""

    if value is None:
        return None

    if isinstance(value, bool):
        return None

    if isinstance(value, int):
        return value if 1 <= value <= 5 else None

    if isinstance(value, float):
        return int(value) if 1 <= value <= 5 else None

    text = clean_text(value)

    if not text:
        return None

    normalized = text.lower()

    if normalized in RATING_MAP:
        return RATING_MAP[normalized]

    match = re.search(r"\b([1-5])\b", normalized)

    if match:
        return int(match.group(1))

    return None


def clean_url(value: Any) -> str | None:
    """Validate and normalize an HTTP/HTTPS URL."""

    if value is None:
        return None

    url = clean_text(value)

    if not url:
        return None

    parsed = urlparse(url)

    if parsed.scheme not in {"http", "https"}:
        return None

    if not parsed.netloc:
        return None

    return url


def clean_tags(value: Any) -> list[str]:
    """Normalize tags into a list of clean strings."""

    if value is None:
        return []

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, (list, tuple, set)):
        values = value
    else:
        values = [value]

    cleaned = []

    for item in values:
        text = clean_text(item)

        if text:
            cleaned.append(text)

    return cleaned


def clean_record(record: dict) -> dict:
    """Clean one standardized scraping record."""

    cleaned = dict(record)

    cleaned["source"] = clean_text(
        cleaned.get("source")
    )

    cleaned["source_url"] = clean_url(
        cleaned.get("source_url")
    )

    cleaned["name_or_title"] = clean_text(
        cleaned.get("name_or_title")
    )

    cleaned["category"] = clean_text(
        cleaned.get("category")
    )

    cleaned["price"] = clean_price(
        cleaned.get("price")
    )

    cleaned["rating"] = clean_rating(
        cleaned.get("rating")
    )

    cleaned["author"] = clean_text(
        cleaned.get("author")
    )

    cleaned["tags"] = clean_tags(
        cleaned.get("tags")
    )

    cleaned["description"] = clean_text(
        cleaned.get("description")
    )

    cleaned["scraped_at"] = clean_text(
        cleaned.get("scraped_at")
    )

    return cleaned


def clean_records(records: list[dict]) -> list[dict]:
    """Clean a collection of records."""

    return [
        clean_record(record)
        for record in records
        if isinstance(record, dict)
    ]
