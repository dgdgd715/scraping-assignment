from processing.deduplication import (
    create_duplicate_key,
    deduplicate_records,
)


def test_duplicate_books_are_detected():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Example Book",
            "author": None,
            "category": "Poetry",
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "  EXAMPLE BOOK  ",
            "author": None,
            "category": "Poetry",
        },
    ]

    unique, duplicate_count = deduplicate_records(records)

    assert len(unique) == 1
    assert duplicate_count == 1


def test_duplicate_quotes_are_detected():
    records = [
        {
            "source": "Quotes to Scrape",
            "name_or_title": "The world as we have created it",
            "author": "Albert Einstein",
        },
        {
            "source": "Quotes to Scrape",
            "name_or_title": " THE WORLD AS WE HAVE CREATED IT ",
            "author": " Albert Einstein ",
        },
    ]

    unique, duplicate_count = deduplicate_records(records)

    assert len(unique) == 1
    assert duplicate_count == 1


def test_different_sources_are_not_duplicates():
    book = {
        "source": "Books to Scrape",
        "name_or_title": "Example",
        "author": None,
        "category": "Poetry",
    }

    quote = {
        "source": "Quotes to Scrape",
        "name_or_title": "Example",
        "author": None,
    }

    assert create_duplicate_key(book) != create_duplicate_key(quote)


def test_unique_records_are_preserved():
    records = [
        {
            "source": "Books to Scrape",
            "name_or_title": "Book One",
            "author": None,
            "category": "Poetry",
        },
        {
            "source": "Books to Scrape",
            "name_or_title": "Book Two",
            "author": None,
            "category": "Travel",
        },
    ]

    unique, duplicate_count = deduplicate_records(records)

    assert len(unique) == 2
    assert duplicate_count == 0
