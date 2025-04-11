# URL Status Checker

This project is an **asynchronous URL status checker** that reads URLs from a CSV file, performs concurrent HTTP GET requests to check their availability, and writes the results (including status codes and error details) to a new CSV file. It is built using Python's `asyncio` and `aiohttp` libraries to maximize performance and scalability by performing network operations concurrently.

---

## 🧠 What This Code Does

- **Reads a list of URLs** from an input CSV file (`Task 2 - Intern.csv`)
- **Validates URLs** to ensure proper formatting
- **Performs asynchronous HTTP requests** using `aiohttp` with retries for failures
- **Handles rate-limiting (429) and service unavailability (503)** with retry logic
- **Logs status codes or error types** for each URL
- **Limits concurrency** to avoid overwhelming network resources
- **Writes results** (URL, status, error type) to a new file `result_logs.csv`

---

## 🚀 How Async Concurrency Works in This Project
This script leverages Python’s **`asyncio`** and **`aiohttp`** libraries to make concurrent HTTP requests.

### 🔄 Why Use `asyncio`?

Traditional HTTP requests (with `requests` module) are blocking — meaning one request must complete before the next starts. With `asyncio`, your script can **send and await multiple requests at once**, improving performance dramatically, especially with large URL lists.

### ⚙️ Breakdown of Concurrency Flow

- `asyncio.Semaphore(CONCURRENCY_LIMIT)`: Prevents exceeding the specified limit (e.g., 10 concurrent requests).
- `aiohttp.ClientSession()`: Maintains connection pooling and reduces request overhead.
- `asyncio.gather(...)`: Collects all asynchronous tasks and runs them concurrently.
- `fetch_with_retry(...)`: Contains retry logic with exponential backoff for handling errors gracefully (like 429 rate limits).
- Each task is wrapped with a semaphore lock via `fetch_url_with_limit(...)` to enforce concurrency control.

This structure ensures high throughput while being respectful of server limits.

---

## 📦 Requirements & Dependencies

### 📄 `requirements.txt`

Create a `requirements.txt` file with the following:

`aiohttp>=3.8.0`

This is the only external dependency. Python’s built-in modules like `csv`, `asyncio`, `logging`, and `urllib.parse` do not need installation.

