import csv
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# HTTP status codes that warrant a retry (typically due to rate-limiting or service unavailability)
RETRY_STATUS_CODES = {429, 503}

# Error types to ignore when logging (to avoid flooding with unhelpful errors)
IGNORED_ERRORS = {"ReadTimeout", "SSLError"}

def get_status_with_retry(url, retries=3):
    """
    Sends a GET request to the specified URL and returns its HTTP status code.
    Retries the request up to `retries` times in case of:
      - Retry-able status codes (e.g., 429, 503)
      - Certain network exceptions (except those in IGNORED_ERRORS)
    
    Returns:
        Tuple: (HTTP status code or "ERROR", URL, concise error type or "")
    """
    headers = {
        # Mimic a real browser to reduce chances of the request being blocked
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    concise_error = ""

    for attempt in range(retries):
        try:
            # Attempt to fetch the URL with a 5-second timeout
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)

            # Retry if response is one of the retry-able status codes
            if response.status_code in RETRY_STATUS_CODES:
                time.sleep(2)  # brief pause before retrying
                continue

            # Return the successful status code
            return (response.status_code, url, "")
        
        except requests.RequestException as e:
            # Get the specific error type (e.g., ConnectTimeout, ConnectionError, etc.)
            error_type = type(e).__name__
            
            # Only log non-ignored errors
            if error_type not in IGNORED_ERRORS:
                concise_error = error_type

            # Wait before retrying
            time.sleep(2)

    # If all attempts fail, return "ERROR" with error type (if relevant)
    return ("ERROR", url, concise_error)


def get_status_codes(input_csv, output_csv, max_threads=10):
    """
    Reads URLs from an input CSV file, fetches their HTTP status codes concurrently,
    and writes the results to an output CSV file.

    Args:
        input_csv (str): Path to the CSV file containing the list of URLs.
        output_csv (str): Path to write the output results (status code, URL, error type).
        max_threads (int): Number of threads to use for making concurrent requests.
    """
    # Load all URLs from the input CSV, skipping the header
    with open(input_csv, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # skip header row
        urls = [row[0] for row in reader if row and row[0].strip()]  # skip empty rows

    results = []

    # Use a thread pool to send requests concurrently
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        # Map each URL to a future thread task
        future_to_url = {executor.submit(get_status_with_retry, url): url for url in urls}

        # As each task completes, collect the result
        for future in as_completed(future_to_url):
            status, url, error = future.result()
            results.append((status, url, error))

            # Print the result to the console
            print(f"({status}) {url}" + (f" | {error}" if error else ""))

    # Write all results to the output CSV file
    with open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Status Code or Error", "URL", "Error Type"])
        writer.writerows(results)


input_csv_path = "Task 2\\Task2_Intern.csv"  
output_csv_path = "output_status.csv"       

get_status_codes(input_csv_path, output_csv_path)

print("Results stored in output_status.csv")
