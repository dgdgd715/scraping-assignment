from processing.validation import (
    is_valid_url,
    validate_record,
)


def valid_book():
    return {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/",
        "name_or_title": "Example Book",
        "category": "Poetry",
        "price": 51.77,
        "rating": 5,
        "author": None,
        "tags": [],
        "description": None,
        "scraped_at": "2026-10-06T00:00:00+00:00",
    }


def test_valid_record():
    valid, errors = validate_record(valid_book())

    assert valid is True
    assert errors == []


def test_invalid_source():
    record = valid_book()
    record["source"] = "Unknown"

    valid, errors = validate_record(record)

    assert valid is False
    assert "Invalid or missing source" in errors


def test_invalid_price():
    record = valid_book()
    record["price"] = "wrong"

    valid, errors = validate_record(record)

    assert valid is False
    assert "Price must be numeric" in errors


def test_invalid_rating():
    record = valid_book()
    record["rating"] = 8

    valid, errors = validate_record(record)

    assert valid is False
    assert "Rating must be between 1 and 5" in errors


def test_invalid_url():
    assert is_valid_url("bad-url") is False
    assert is_valid_url(
        "https://books.toscrape.com/"
    ) is True
