import csv
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed


def get_status_with_retry(url, retries=3):
    """
    Sends a GET request to the specified URL and retrieves its HTTP status code.

    Retries the request up to `retries` times in case of temporary failures,
    and uses a 'User-Agent' header to mimic a real browser to avoid blocks.

    Returns:
        Tuple: (status_code or "ERROR", url)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
            return (response.status_code, url)
        except requests.RequestException as e:
            print(f"[Retrying] {url} failed: {e}")
            time.sleep(2)
    return ("ERROR", url)


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
        urls = [row[0] for row in reader]

    results = []
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_url = {executor.submit(get_status_with_retry, url): url for url in urls}
        for future in as_completed(future_to_url):
            result = future.result()
            results.append(result)
            print(f"({result[0]}) {result[1]}")

    with open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        writer = csv.writer(out_file)
        writer.writerow(["Status Code", "URL"])
        writer.writerows([(f"({status})", url) for status, url in results])


# --- Run the script ---
input_csv_path = "Outreachy-Tasks\Task 2 - Intern.csv"
output_csv_path = "output_status.csv"
get_status_codes(input_csv_path, output_csv_path)
