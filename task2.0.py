import csv
import requests
import time


def get_status_with_retry(url, retries=3):
    """
    This function retrieves the HTTP status code of the URL by sending a GET request.
    If the request fails (e.g., due to network issues or server errors),
    it retries the request up to a specified number of times.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, allow_redirects=True, timeout=5)
            return response.status_code
        except requests.RequestException as e:
            print(f"Attempt failed: {e}")
            time.sleep(2)  
    return "ERROR"

def get_status_codes(input_csv, output_csv):
    """Reads URLs from Task 2 - Intern.csv, retrieves their HTTP status codes, and writes the results to output_status.csv."""
    with open(input_csv, newline='', encoding='utf-8') as file, open(output_csv, mode='w', newline='', encoding='utf-8') as out_file:
        reader = csv.reader(file)
        writer = csv.writer(out_file)
        writer.writerow(["Status Code", "URL"])  
        next(reader)  
        
        for row in reader:
            url = row[0]
            status = get_status_with_retry(url)
            writer.writerow([f"({status})", url])
            print(f"({status}) {url}")

input_csv_path = "Task 2 - Intern.csv"
output_csv_path = "output_status.csv"
get_status_codes(input_csv_path, output_csv_path)