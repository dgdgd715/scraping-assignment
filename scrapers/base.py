import logging
import time

import requests


class BaseScraper:
    """Base class containing common HTTP and logging functionality."""

    def __init__(self, timeout=10, max_retries=3, retry_delay=1):
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36"
                )
            }
        )

        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch(self, url):
        """Fetch a URL with retries and basic error handling."""

        for attempt in range(1, self.max_retries + 1):
            try:
                self.logger.info(
                    "Fetching %s (attempt %d/%d)",
                    url,
                    attempt,
                    self.max_retries,
                )

                response = self.session.get(
                    url,
                    timeout=self.timeout,
                )

                response.raise_for_status()

                self.logger.info(
                    "Successfully fetched %s (status=%s)",
                    url,
                    response.status_code,
                )

                return response

            except requests.RequestException as exc:
                self.logger.warning(
                    "Request failed for %s: %s",
                    url,
                    exc,
                )

                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)

            except Exception:
                self.logger.exception(
                    "Unexpected error while fetching %s",
                    url,
                )
                break

        self.logger.error(
            "Failed to fetch %s after %d attempts",
            url,
            self.max_retries,
        )

        return None
