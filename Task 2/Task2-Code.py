import csv
import logging  # For logging warnings and status messages
import asyncio  # Core library for async programming
import aiohttp  # Asynchronous HTTP client
from urllib.parse import urlparse   # To validate URL format

# --- Configuration ---
CSV_FILE = "Task 2\Task2_Intern.csv"  # Input CSV file containing URLs 
CONCURRENCY_LIMIT = 10            # Max number of concurrent requests
RETRY_STATUS_CODES = {429, 503}   # Retry for these HTTP status codes (rate limit or unavailable)
MAX_RETRIES = 3                   # Retries to handle temporary issues like rate limiting, timeouts, or service unavailability.
RETRY_DELAY = 2                   # Delay between retries (in seconds)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
TIMEOUT_SECONDS = 50              # Older government sites and slower server e.g. academic journals take longer to respond

# --- Logging Setup ---
# Configure logging to show only the message (no timestamps or levels)
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- Helper: Check if URL is valid ---
def check_valid_url(url):
    """
    Check whether a URL has both a scheme (http/https) and a network location (domain).
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

# --- Retry logic for fetching a URL ---
# --- Retry logic for fetching a URL ---
async def fetch_with_retry(session, url):
    """
    Attempt to fetch the URL using retries if it fails or returns specific retr-able status codes.
    Returns a dict with URL, status code (or 'ERROR'), and error type if any.
    """
    headers = {"User-Agent": USER_AGENT}
    last_status_code = None
    last_error_type = "UnknownError"
    last_error_message = ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            # Default: verify SSL
            try:
                async with session.get(url, headers=headers, ssl=True, allow_redirects=True, timeout=TIMEOUT_SECONDS) as response:
                    last_status_code = response.status
                    # Retry for specific HTTP codes like 429 (rate-limiting) or 503 (service unavailable)
                    if response.status in RETRY_STATUS_CODES:
                        logger.warning(f"[Retrying] ({response.status}) {url} - attempt {attempt}")
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    # Log successful response
                    logger.info(f"({response.status}) {url}")
                    return {"URL": url, "Status": response.status, "Error": ""}
            except aiohttp.ClientConnectorCertificateError:
                # Fallback for SSL certificate error
                logger.warning(f"[SSL Warning] Invalid cert for {url}, retrying without SSL verification.")
                async with session.get(url, headers=headers, ssl=False, allow_redirects=True, timeout=TIMEOUT_SECONDS) as response:
                    last_status_code = response.status
                    if response.status in RETRY_STATUS_CODES:
                        logger.warning(f"[Retrying] ({response.status}) {url} - attempt {attempt}")
                        await asyncio.sleep(RETRY_DELAY)
                        continue
                    logger.info(f"({response.status}) {url}")
                    return {"URL": url, "Status": response.status, "Error": "SSL certificate verification disabled"}
        # Handle specific exceptions to identify the type of error that occurred
        except aiohttp.ClientResponseError as e:
            last_error_type = f"ClientResponseError ({e.status})"
            last_error_message = str(e)
        except aiohttp.ClientConnectorError as e:
            last_error_type = "ClientConnectorError"
            last_error_message = str(e)
        except aiohttp.ClientPayloadError as e:
            last_error_type = "ClientPayloadError"
            last_error_message = str(e)
        except asyncio.TimeoutError:
            last_error_type = "TimeoutError"
            last_error_message = "The request timed out"
        except Exception as e:
            last_error_type = type(e).__name__
            last_error_message = str(e)

        # Log retry on exception
        logger.warning(f"[Retrying] (Exception) {url} - {last_error_type}: {last_error_message}, attempt {attempt}")
        await asyncio.sleep(RETRY_DELAY)

    # If all retries failed, return with error details
    return {
        "URL": url,
        "Status": last_status_code if last_status_code else "ERROR",
        "Error": f"{last_error_type}: {last_error_message}",
    }


# --- Wrapper with semaphore control ---
async def fetch_url_with_limit(sem, session, url):
    """
    Use a semaphore to limit the number of concurrent fetches.
    """
    async with sem:
        return await fetch_with_retry(session, url)

# --- Read CSV, check validity, and fetch status ---
async def process_urls_from_csv(filename):
    """
    Read URLs from a CSV file, validate them, and asynchronously fetch their status.
    Returns a list of result dictionaries for each URL.
    """
    results = []

    # Read URLs from the CSV
    with open(filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader, None)  # Skip header
        if not header:
            raise ValueError("CSV file is missing a header")
        urls = [row[0].strip() for row in reader if row and row[0].strip()]

    valid_urls = []
    for url in urls:
        if check_valid_url(url):
            valid_urls.append(url)
        else:
            # Handle invalid or empty URLs
            error = "Invalid URL format" if url else "Empty URL"
            logger.warning(f"[Invalid] {url} - {error}")
            print(f"[Invalid] {url} - {error}")
            results.append({"URL": url, "Status": "Invalid", "Error": error})

    # Set up concurrency limit
    sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url_with_limit(sem, session, url) for url in valid_urls]
        responses = await asyncio.gather(*tasks)
        results.extend(responses)

    return results

# --- Write final results to output CSV ---
def write_to_csv_file(url_results, filename="result_logs.csv"):
    """
    Write the results (status, URL, error) to a new CSV file.
    """
    with open(filename, "w", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Status Code or Error", "URL", "Error"])  # Header row
        for row in url_results:
            writer.writerow([row["Status"], row["URL"], row["Error"]])

# --- Main Entry Point ---
if __name__ == "__main__":
    # Run the async processing and write results to CSV
    url_results = asyncio.run(process_urls_from_csv(CSV_FILE))
    write_to_csv_file(url_results)
    print(f"\n Total {len(url_results)} URLs checked and results stored in result_logs.csv")
