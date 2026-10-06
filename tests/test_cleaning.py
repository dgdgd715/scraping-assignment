from processing.cleaning import (
    clean_price,
    clean_rating,
    clean_text,
)


def test_clean_price():
    assert clean_price("Â£51.77") == 51.77
    assert clean_price("£10.50") == 10.50
    assert clean_price(None) is None


def test_clean_text():
    assert clean_text("  Example   Book  ") == "Example Book"
    assert clean_text(None) is None


def test_clean_rating():
    assert clean_rating("Five") == 5
    assert clean_rating("Three") == 3
    assert clean_rating(4) == 4
    assert clean_rating(8) is None
