import csv
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

RETRY_STATUS_CODES = {429, 503}
IGNORED_ERRORS = {"ReadTimeout", "SSLError"}

def get_status_with_retry(url, retries=3):
    """
    Sends a GET request to the specified URL and retrieves its HTTP status code.
    Retries on certain HTTP codes and exceptions.

    Returns:
        Tuple: (status or 'ERROR', url, concise error type or '')
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    concise_error = ""
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
            if response.status_code in RETRY_STATUS_CODES:
                time.sleep(2)
                continue
            return (response.status_code, url, "")
        except requests.RequestException as e:
            error_type = type(e).__name__
            if error_type not in IGNORED_ERRORS:
                concise_error = error_type
            time.sleep(2)

    return ("ERROR", url, concise_error)


def get_status_codes(input_csv, output_csv, max_threads=10):
    """
    Reads URLs from a CSV file, fetches their HTTP status codes using multithreading,
    and writes the results to another CSV file.

    Args:
        input_csv (str): Path to the input CSV with URLs.
        output_csv (str): Path to write the results.
        max_threads (int): Number of threads to use for concurrent requests.
    """
    with open(input_csv, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        urls = [row[0] for row in reader if row and row[0].strip()]

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(get_status_with_retry, url): url for url in urls}
        for future in as_completed(future_to_url):
            status, url, error = future.result()
            results.append((status, url, error))
            print(f"({status}) {url}" + (f" | {error}" if error else ""))

    with open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Status Code or Error", "URL", "Error Type"])
        writer.writerows(results)


# --- Run the script ---
input_csv_path = "Task 2\Task2_Intern.csv"
output_csv_path = "output_status.csv"
get_status_codes(input_csv_path, output_csv_path)
print("Results stored in output_status.csv")
