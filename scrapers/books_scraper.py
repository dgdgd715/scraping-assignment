from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class BooksScraper(BaseScraper):
    """Scraper for Books to Scrape."""

    BASE_URL = "https://books.toscrape.com/"

    def scrape(self):
        records = []
        current_url = self.BASE_URL

        while current_url:
            response = self.fetch(current_url)

            if response is None:
                self.logger.error(
                    "Skipping page: %s",
                    current_url,
                )
                break

            soup = BeautifulSoup(
                response.text,
                "html.parser",
            )

            books = soup.select("article.product_pod")

            for book in books:
                record = self._parse_book(
                    book,
                    current_url,
                )

                if record:
                    records.append(record)

            next_link = soup.select_one(
                "li.next a"
            )

            if next_link and next_link.get("href"):
                current_url = urljoin(
                    current_url,
                    next_link["href"],
                )
            else:
                current_url = None

        self.logger.info(
            "Books scraping completed: %d records",
            len(records),
        )

        return records

    def _parse_book(self, book, page_url):
        """Parse a book from a listing page."""

        try:
            title_element = book.select_one(
                "h3 a"
            )

            price_element = book.select_one(
                "p.price_color"
            )

            availability_element = book.select_one(
                "p.instock.availability"
            )

            rating_element = book.select_one(
                "p.star-rating"
            )

            if not title_element:
                return None

            title = (
                title_element.get("title")
                or title_element.get_text(
                    " ",
                    strip=True,
                )
            )

            relative_url = title_element.get(
                "href"
            )

            product_url = (
                urljoin(page_url, relative_url)
                if relative_url
                else None
            )

            price = (
                price_element.get_text(
                    " ",
                    strip=True,
                )
                if price_element
                else None
            )

            availability = (
                availability_element.get_text(
                    " ",
                    strip=True,
                )
                if availability_element
                else None
            )

            rating = self._parse_rating(
                rating_element
            )

            # Category is available from the listing
            # page's breadcrumb context only indirectly,
            # so leave it empty rather than inventing it.
            return {
                "source": "Books to Scrape",
                "source_url": product_url,
                "name_or_title": title,
                "category": None,
                "price": price,
                "rating": rating,
                "author": None,
                "tags": None,
                "description": availability,
                "scraped_at": datetime.now(
                    timezone.utc
                ).isoformat(),
            }

        except Exception:
            self.logger.exception(
                "Error parsing book"
            )
            return None

    @staticmethod
    def _parse_rating(rating_element):
        if not rating_element:
            return None

        rating_map = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }

        classes = rating_element.get(
            "class",
            [],
        )

        for class_name, rating in rating_map.items():
            if class_name in classes:
                return rating

        return None
