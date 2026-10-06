import csv
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_records
from processing.deduplication import deduplicate_records
from processing.validation import validate_records
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

FINAL_DATASET_PATH = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_PATH = OUTPUT_DIR / "summary_report.json"
LOG_PATH = LOG_DIR / "scraper.log"


def setup_logging():
    """Configure application logging."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | %(levelname)s | "
            "%(name)s | %(message)s"
        ),
        handlers=[
            logging.FileHandler(
                LOG_PATH,
                encoding="utf-8",
            ),
            logging.StreamHandler(),
        ],
        force=True,
    )


def scrape_source(scraper, source_name):
    """Run a scraper without stopping the complete pipeline."""

    logger = logging.getLogger("pipeline")

    start_time = time.perf_counter()

    try:
        records = scraper.scrape()

        elapsed = time.perf_counter() - start_time

        logger.info(
            "%s scraping completed: %d records in %.2f seconds",
            source_name,
            len(records),
            elapsed,
        )

        return records, elapsed

    except Exception:
        elapsed = time.perf_counter() - start_time

        logger.exception(
            "%s scraper failed after %.2f seconds",
            source_name,
            elapsed,
        )

        return [], elapsed


def process_source(records, source_name):
    """Clean, validate, and deduplicate one source."""

    logger = logging.getLogger("pipeline")

    collected_count = len(records)

    cleaned_records = clean_records(records)

    cleaned_count = len(cleaned_records)

    valid_records, rejected_records = validate_records(
        cleaned_records
    )

    rejected_count = len(rejected_records)

    unique_records, duplicate_count = deduplicate_records(
        valid_records
    )

    logger.info(
        "%s processing: collected=%d cleaned=%d "
        "rejected=%d duplicates=%d final=%d",
        source_name,
        collected_count,
        cleaned_count,
        rejected_count,
        duplicate_count,
        len(unique_records),
    )

    return unique_records, {
        "collected": collected_count,
        "after_cleaning": cleaned_count,
        "rejected": rejected_count,
        "duplicates_removed": duplicate_count,
        "final": len(unique_records),
    }


def write_csv(records):
    """Write consolidated records to CSV."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "source",
        "source_url",
        "name_or_title",
        "category",
        "price",
        "rating",
        "author",
        "tags",
        "description",
        "scraped_at",
    ]

    with FINAL_DATASET_PATH.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
        )

        writer.writeheader()

        for record in records:
            row = dict(record)

            if isinstance(row.get("tags"), list):
                row["tags"] = ", ".join(row["tags"])

            writer.writerow(
                {
                    field: row.get(field)
                    for field in fieldnames
                }
            )


def write_summary(summary):
    """Write summary metrics to JSON."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with SUMMARY_PATH.open(
        "w",
        encoding="utf-8",
    ) as json_file:

        json.dump(
            summary,
            json_file,
            indent=4,
        )


def main():
    """Run the complete scraping and processing pipeline."""

    setup_logging()

    logger = logging.getLogger("pipeline")

    pipeline_start = time.perf_counter()

    execution_started_at = datetime.now(
        timezone.utc
    ).isoformat()

    logger.info("Starting scraping pipeline")

    scrapers = [
        (
            "Books to Scrape",
            BooksScraper(),
        ),
        (
            "Quotes to Scrape",
            QuotesScraper(),
        ),
    ]

    all_records = []
    source_summary = {}

    for source_name, scraper in scrapers:
        raw_records, scrape_time = scrape_source(
            scraper,
            source_name,
        )

        processed_records, metrics = process_source(
            raw_records,
            source_name,
        )

        metrics["scrape_time_seconds"] = round(
            scrape_time,
            2,
        )

        source_summary[source_name] = metrics

        all_records.extend(processed_records)

    # Final cross-source deduplication.
    final_records, cross_source_duplicates = (
        deduplicate_records(all_records)
    )

    final_count = len(final_records)

    total_collected = sum(
        item["collected"]
        for item in source_summary.values()
    )

    total_cleaned = sum(
        item["after_cleaning"]
        for item in source_summary.values()
    )

    total_rejected = sum(
        item["rejected"]
        for item in source_summary.values()
    )

    total_source_duplicates = sum(
        item["duplicates_removed"]
        for item in source_summary.values()
    )

    pipeline_time = time.perf_counter() - pipeline_start

    summary = {
        "execution_started_at": execution_started_at,
        "execution_finished_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "execution_time_seconds": round(
            pipeline_time,
            2,
        ),
        "sources": source_summary,
        "totals": {
            "records_collected": total_collected,
            "records_after_cleaning": total_cleaned,
            "records_rejected": total_rejected,
            "duplicates_removed": (
                total_source_duplicates
                + cross_source_duplicates
            ),
            "cross_source_duplicates": (
                cross_source_duplicates
            ),
            "final_records": final_count,
        },
    }

    write_csv(final_records)
    write_summary(summary)

    logger.info(
        "Final dataset written to %s",
        FINAL_DATASET_PATH,
    )

    logger.info(
        "Summary written to %s",
        SUMMARY_PATH,
    )

    logger.info(
        "Pipeline completed successfully: %d final records",
        final_count,
    )


if __name__ == "__main__":
    main()
