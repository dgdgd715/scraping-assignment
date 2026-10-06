\# AI Usage



\## AI Tool Used



ChatGPT



\## How AI Was Used



AI assistance was used during development of this web scraping assignment for:



\- Designing the project structure

\- Planning the common data model

\- Developing scraping and pagination logic

\- Debugging scraping and processing issues

\- Designing cleaning and validation functions

\- Designing duplicate detection

\- Creating unit tests

\- Reviewing error-handling approaches

\- Improving project documentation



\## Representative Prompts



Examples of prompts used during development include:



1\. "Help me design a Python web scraping pipeline for Books to Scrape and Quotes to Scrape."



2\. "How should I implement pagination using Requests and BeautifulSoup?"



3\. "Help me create reusable cleaning, validation, and deduplication functions."



4\. "Help me create pytest tests for the cleaning, validation, and deduplication modules."



5\. "Review the scraper for error handling and missing HTML elements."



\## AI-Assisted Code



AI assistance contributed to parts of:



\- `scrapers/base.py`

\- `scrapers/books\_scraper.py`

\- `scrapers/quotes\_scraper.py`

\- `processing/cleaning.py`

\- `processing/validation.py`

\- `processing/deduplication.py`

\- `main.py`

\- Test files

\- Project documentation



The generated code was reviewed and adapted during implementation.



\## Changes After Reviewing AI Output



During development, the initial Books scraper implementation made additional requests to every individual book page. This resulted in approximately 1,000 additional HTTP requests and a long execution time.



The implementation was changed so that the Books scraper primarily uses the paginated listing pages. Fields that are not available from those pages are left empty rather than being invented.



The project was also tested incrementally rather than relying only on generated code.



\## Problems or Incomplete Suggestions Discovered



An early implementation of the Books scraper made unnecessary individual product-page requests. This was identified during execution because the complete Books scrape took approximately 13 minutes.



The scraper was simplified to reduce unnecessary requests while still collecting the required listing information and handling pagination.



The project also initially had empty test files. Unit tests were then added for cleaning, validation, and deduplication.



\## Verification



The implementation was verified by:



\- Testing connectivity to both websites

\- Running the Books scraper and confirming 1,000 records

\- Running the Quotes scraper and confirming 100 records

\- Running the complete pipeline

\- Inspecting the generated CSV

\- Inspecting the generated JSON summary

\- Checking scraper logs

\- Running the automated test suite



The final test result was:



```text

12 passed



