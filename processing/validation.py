from urllib.parse import urlparse


VALID_SOURCES = {
    "Books to Scrape",
    "Quotes to Scrape",
}


def is_valid_url(value):
    """Return True when value looks like a valid HTTP/HTTPS URL."""

    if not isinstance(value, str) or not value.strip():
        return False

    try:
        parsed = urlparse(value)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except ValueError:
        return False


def validate_record(record):
    """
    Validate one cleaned standardized record.

    Returns:
        tuple[bool, list[str]]:
            Whether the record is valid and any validation errors.
    """

    errors = []

    if not isinstance(record, dict):
        return False, ["Record must be a dictionary"]

    source = record.get("source")

    if source not in VALID_SOURCES:
        errors.append("Invalid or missing source")

    source_url = record.get("source_url")

    if not is_valid_url(source_url):
        errors.append("Invalid or missing source_url")

    title = record.get("name_or_title")

    if not isinstance(title, str) or not title.strip():
        errors.append("Missing name_or_title")

    price = record.get("price")

    if price is not None:
        if not isinstance(price, (int, float)):
            errors.append("Price must be numeric")
        elif price < 0:
            errors.append("Price cannot be negative")

    rating = record.get("rating")

    if rating is not None:
        if not isinstance(rating, (int, float)):
            errors.append("Rating must be numeric")
        elif not 1 <= rating <= 5:
            errors.append("Rating must be between 1 and 5")

    tags = record.get("tags")

    if tags is not None and not isinstance(tags, list):
        errors.append("Tags must be a list")

    return len(errors) == 0, errors


def validate_records(records):
    """
    Validate multiple records.

    Returns:
        tuple[list[dict], list[dict]]:
            valid records and rejected records.
    """

    valid_records = []
    rejected_records = []

    for record in records:
        is_valid, errors = validate_record(record)

        if is_valid:
            valid_records.append(record)
        else:
            rejected_records.append(
                {
                    "record": record,
                    "errors": errors,
                }
            )

    return valid_records, rejected_records
