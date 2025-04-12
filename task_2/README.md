# URL Status Checker

This project an efficient and scalable **asynchronous URL status checker** built in Python. It reads a list of URLs from a CSV file, performs concurrent HTTP GET requests using `aiohttp`, and writes the response statuses to an output CSV. The tool is optimized to handle large URL batches, implement retry logic for failures (like 429 & 503), and gracefully manage errors — all while maintaining a configurable concurrency limit.

---

## 📜 Table of Contents

- [📘 Project Description](#-project-description)
- [✨ Features](#-features)
- [🧰 Prerequisites](#-prerequisites)
- [⚙️ Setup](#️-setup)
- [📦 Dependencies](#-dependencies)
- [🚀 How It Works](#-how-it-works)
- [📁 File Structure](#-file-structure)
- [📄 Input Format](#-input-format)
- [✅ Output Format](#-output-format)
- [🧪 Error Handling](#-error-handling)
- [🔧 Configuration Options](#-configuration-options)
- [🚀 How Async Concurrency Works in This Project](#-how-async-concurrency-works-in-this-project)
- [⚙️ Multithreading with ThreadPoolExecutor](-multithreading-with-threadpoolexecutor)
---

## 📘 Project Description

This project is a high-performance asynchronous status checker that efficiently validates the availability of URLs using concurrent HTTP GET requests.

### What it does:

- Reads URLs from an input CSV file (`Task 2 - Intern.csv`)
- Validates URL structure
- Makes concurrent HTTP requests using Python’s `asyncio` and `aiohttp`
- Implements retry logic for common server errors (e.g., 429 and 503)
- Logs HTTP status codes or categorizes request failures (timeouts, connection errors, invalid URLs)
- Writes the result to a structured output CSV file (`result_logs.csv`)
- Limits the number of concurrent requests using a semaphore to prevent overwhelming the target servers

This tool is ideal for tasks involving bulk URL health checks, uptime monitoring, or crawling initial availability diagnostics.

---

## ✨ Features

- ⚡ Asynchronous & non-blocking HTTP requests with `aiohttp`
- 🧠 Built-in retry mechanism for server errors and timeouts
- 🚥 Concurrency control via `asyncio.Semaphore`
- 📉 CSV output with detailed error descriptions
- 🧹 Skips invalid/malformed URLs gracefully
- 🔒 Customizable configuration (retry attempts, concurrency limit, etc.)
- 💼 Lightweight with minimal external dependencies

---

## 🧰 Prerequisites

- Python 3.8 or higher
- `pip` installed
- A CSV file with a list of URLs to test (`Task 2 - Intern.csv`)

---

## ⚙️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Annosha/Outreachy-Tasks.git
cd Outreachy-Tasks
```

### 2. Create a Virtual Environment (Optional but Recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the code

---
For asyncio code:

```bash
python3 asyncio_code.py
```

and for multithreading code:

```bash
python3 multithreading_code.py
```

---

## 📦 Dependencies

- `aiohttp`: For async HTTP requests
- Standard Python libraries: `csv`, `asyncio`, `logging`, `urllib.parse`

`requirements.txt`:

```bash
aiohttp>=3.8.0
```

## 🧠 What This Code Does

- **Reads a list of URLs** from an input CSV file (`input_urls.csv`)
- **Validates URLs** to ensure proper formatting
- **Performs asynchronous HTTP requests** using `aiohttp` with retries for failures
- **Handles rate-limiting (429) and service unavailability (503)** with retry logic
- **Logs status codes or error types** for each URL
- **Limits concurrency** to avoid overwhelming network resources
- **Retry Logic** Automatically retries failed requests (due to rate-limiting or temporary outages).
- **Writes results** (URL, status, error type) to a new file `output_asyncio.csv` and `output_multithreading.csv`

---

## 📁 File Structure

```bash
├── .gitignore 
├── README.md 
├── task_1 
│ └── task1_code.html           # Task 1 script
├── task_2
 │ ├── README.md                # Script description
 │ ├── asyncio_code.py          # async script
 │ ├── input_urls.csv           # input urls
 │ ├── multithreading_code.py   # multithreading script
 │ ├── output_asyncio.csv       # Output with status results
 │ ├── output_multithreading.csv # Output with status results
 │ └── requirements.txt
```

## 📄 Input Format

CSV file: `input_urls.csv`

```bash
URL
https://example.com
https://www.google.com
https://invalid-url
```

## ✅ Output Format

CSV file: `output_asyncio.csv`

```bash
Status Code or Error,URL,Error
200,https://www.google.com,
ERROR,https://nonexistent.domain,ClientConnectorError
Invalid,htp:/example,Invalid URL format
```

## 🧪 Error Handling

| Error Type                | Description                          | Action Taken                   |
|--------------------------|--------------------------------------|--------------------------------|
| 429 Too Many Requests    | Server rate-limited the request      | Retry with delay               |
| 503 Service Unavailable  | Temporary unavailability             | Retry with delay               |
| TimeoutError             | Connection timed out                 | Retry with delay               |
| Invalid URL              | Malformed or unsupported URL scheme  | Skip and log as "Invalid"      |
| Connection Errors        | DNS/Connection issues                | Categorized and logged         |
| Unknown Exceptions       | All others                           | Caught and labeled as "ERROR"  |

## 🔧 Configuration Options

You can edit these constants in `asyncio_code.py`:

```bash
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds
RETRY_STATUS_CODES = [429, 503]
CONCURRENCY_LIMIT = 10
```

## 🚀 How Async Concurrency Works in This Project

This script leverages Python’s **`asyncio`** and **`aiohttp`** libraries to make concurrent HTTP requests.

### 🔄 Why Use `asyncio`?

Traditional HTTP requests (with `requests` module) are blocking — meaning one request must complete before the next starts. With `asyncio`, your script can **send and await multiple requests at once**, improving performance dramatically, especially with large URL lists.

### 📊 Breakdown of Concurrency Flow

- `asyncio.Semaphore(CONCURRENCY_LIMIT)`: Prevents exceeding the specified limit (e.g., 10 concurrent requests).
- `aiohttp.ClientSession()`: Maintains connection pooling and reduces request overhead.
- `asyncio.gather(...)`: Collects all asynchronous tasks and runs them concurrently.
- `fetch_with_retry(...)`: Contains retry logic with exponential backoff for handling errors gracefully (like 429 rate limits).
- Each task is wrapped with a semaphore lock via `fetch_url_with_limit(...)` to enforce concurrency control.

This structure ensures high throughput while being respectful of server limits.

---
### ⚙️ Multithreading with ThreadPoolExecutor

For simple and effective parallel processing of HTTP requests using requests, multithreading offers an easy, compatible, and practical solution. While asyncio is great for large-scale async tasks, it introduces complexity and requires non-blocking libraries—which may not be ideal in all situations.

Here is the link to the code where I implemented multithreading: [Multithreading](multithreading_code.py)
