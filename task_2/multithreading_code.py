import csv
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

# Status codes that are worth retrying
RETRY_STATUS_CODES = {429, 503}

# Error types you want to ignore in logging (can still return them if retries fail)
IGNORED_ERRORS = {"ReadTimeout", "SSLError"}

def get_status_with_retry(url, retries=3):
    """
    Attempts to fetch the status code of a URL with retry logic on certain failure codes and exceptions.

    Args:
        url (str): The target URL.
        retries (int): Number of retry attempts.

    Returns:
        tuple: (status or 'ERROR', url, detailed error message or empty string)
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        )
    }

    detailed_error = ""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=10, verify=False)
            if response.status_code in RETRY_STATUS_CODES:
                time.sleep(2)
                continue
            return (response.status_code, url, "")
        except requests.RequestException as e:
            error_type = type(e).__name__
            # Capture full detailed error only if not in ignored list
            if error_type not in IGNORED_ERRORS:
                detailed_error = f"{error_type}: {str(e)}"
            time.sleep(2)

    return ("ERROR", url, detailed_error)


def get_status_codes(input_csv, output_csv, max_threads=10):
    """
    Processes a list of URLs to determine their HTTP response status or errors.

    Args:
        input_csv (str): File path to input CSV containing URLs.
        output_csv (str): File path to output CSV for results.
        max_threads (int): Number of threads for concurrent processing.
    """
    # Read URLs from CSV, skipping header
    with open(input_csv, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        urls = [row[0] for row in reader if row and row[0].strip()]

    results = []

    # Fetch statuses concurrently
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(get_status_with_retry, url): url for url in urls}
        for future in as_completed(future_to_url):
            status, url, error_detail = future.result()
            results.append((status, url, error_detail))
            print(f"({status}) {url}" + (f" | {error_detail}" if error_detail else ""))

    # Save results to output CSV
    with open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Status Code or Error", "URL", "Detailed Error Message"])
        writer.writerows(results)


# --- Run the script ---
input_csv_path = "task_2/input_urls.csv"
output_csv_path = "task_2/output_multithreading.csv"

get_status_codes(input_csv_path, output_csv_path)
print("✅ Results with detailed errors stored in output_status.csv")
