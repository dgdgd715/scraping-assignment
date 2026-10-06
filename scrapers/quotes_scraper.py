from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper


class QuotesScraper(BaseScraper):
    """Scraper for Quotes to Scrape."""

    BASE_URL = "https://quotes.toscrape.com/"
    START_URL = BASE_URL

    def scrape(self):
        """Scrape all available quote pages."""

        records = []
        current_url = self.START_URL

        while current_url:
            response = self.fetch(current_url)

            if response is None:
                self.logger.error(
                    "Skipping page because it could not be fetched: %s",
                    current_url,
                )
                current_url = None
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            quotes = soup.select("div.quote")

            self.logger.info(
                "Found %d quotes on %s",
                len(quotes),
                current_url,
            )

            for quote in quotes:
                record = self._parse_quote(quote, current_url)

                if record:
                    records.append(record)

            next_link = soup.select_one("li.next a")

            if next_link and next_link.get("href"):
                current_url = urljoin(current_url, next_link["href"])
            else:
                current_url = None

        self.logger.info(
            "Quotes scraping completed. Total records: %d",
            len(records),
        )

        return records

    def _parse_quote(self, quote, page_url):
        """Parse one quote record."""

        try:
            text_element = quote.select_one("span.text")
            author_element = quote.select_one("small.author")
            tags_elements = quote.select("div.tags a.tag")

            if not text_element:
                self.logger.warning(
                    "Skipping quote because text is missing: %s",
                    page_url,
                )
                return None

            quote_text = text_element.get_text(" ", strip=True)

            author = (
                author_element.get_text(" ", strip=True)
                if author_element
                else None
            )

            tags = [
                tag.get_text(" ", strip=True)
                for tag in tags_elements
            ]

            author_link = None
            if author_element:
                author_link_element = quote.select_one(
                    "span a[href]"
                )

                if author_link_element:
                    author_link = urljoin(
                        page_url,
                        author_link_element.get("href"),
                    )

            return {
                "source": "Quotes to Scrape",
                "source_url": page_url,
                "name_or_title": quote_text,
                "category": None,
                "price": None,
                "rating": None,
                "author": author,
                "tags": tags,
                "description": author_link,
                "scraped_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception:
            self.logger.exception(
                "Unexpected error while parsing a quote from %s",
                page_url,
            )
            return None
