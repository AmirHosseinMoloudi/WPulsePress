# WordPress Health Monitor

*A simple, robust, and CDN-friendly Python application to monitor the health and reachability of your WordPress website.*

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)![License](https://img.shields.io/badge/license-MIT-green.svg)![Status](https://img.shields.io/badge/status-active-brightgreen.svg)

This tool periodically checks a target WordPress site to ensure it's not only online but also serving proper WordPress content. It's designed to be lightweight, easy to use, and informative, providing clear alerts on failure.

---

## Key Features

-   **Multi-Level Health Checks:** Goes beyond a simple ping. It verifies:
    1.  **HTTP Status:** Ensures the site returns a successful status code (2xx/3xx).
    2.  **WordPress Signature:** Confirms the presence of `"wp-content"` in the page source, a strong indicator that the WordPress backend is functioning correctly.
-   **CDN-Friendly:** Uses special HTTP headers (`Cache-Control: no-cache`) to politely ask CDNs and caching layers to provide a fresh version of the page, ensuring the check reflects the real-time status of your origin server.
-   **High-Visibility Alerts:**
    -   **Console:** A large, colored, attention-grabbing warning is printed directly to the terminal for all operating systems.
    -   **Windows GUI:** If run on Windows, a native, non-blocking GUI pop-up window appears for an unmissable alert.
-   **Structured Logging:** All checks (successful or failed) are recorded with timestamps in a clean log file (`website_health.log`) for auditing and diagnostics.
-   **User-Friendly:** Simple interactive setup. Just run the script and answer two questions.
-   **Graceful Shutdown:** Safely stop the monitor at any time by pressing `Ctrl+C` without generating errors.

---

## What It Looks Like

**Normal Operation:**
```
INFO - SUCCESS: https://wordpress.org is healthy. Status: 200. WordPress signature found.
```

**Failure Detected (Console):**
```
*****************************************************************
*                                                               *
*                  !!! WEBSITE ALERT !!!                        *
*                                                               *
*****************************************************************
  Unhealthy Status Detected for: https://my-broken-site.com
  Reason: Website returned a non-successful status code: 503
*****************************************************************
```

**Failure Detected (Windows GUI Alert):**

```
 _________________________________________
|                                         |
| [X]      !!! WEBSITE ALERT !!!          |
|_________________________________________|
|                                         |
|             HEALTH ALERT                |
|                                         |
|    Website:                             |
|    https://my-broken-site.com           |
|                                         |
|    Reason:                              |
|    Connection Error: Could not connect  |
|_________________________________________|

```

---

## Getting Started (For Beginners)

This guide will get you running in just a few minutes.

### 1. Prerequisites

You only need **Python 3** installed on your system. If you don't have it, you can download it from the official website: [python.org](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH".

### 2. Installation

1.  **Download the Script:** Save the final application code from the previous step as a file named `website_health_monitor.py`.

2.  **Open a Terminal:**
    -   **Windows:** Open the Start Menu, type `cmd` or `powershell`, and press Enter.
    -   **macOS:** Open Finder, go to Applications -> Utilities, and open `Terminal`.
    -   **Linux:** Usually `Ctrl+Alt+T` or find `Terminal` in your applications menu.

3.  **Install Dependencies:** Python packages are installed using a tool called `pip`, which comes with Python. In your terminal, run the following single command. This will download and install all the required libraries automatically.

    ```bash
    pip install httpx schedule colorama
    ```

### 3. How to Run

1.  **Navigate to the Script:** In your terminal, use the `cd` (change directory) command to go to the folder where you saved `website_health_monitor.py`.
    ```bash
    # Example: If you saved it on your Desktop
    cd Desktop
    ```

2.  **Run the Application:** Start the script by typing `python` followed by the filename.
    ```bash
    python website_health_monitor.py
    ```

3.  **Answer the Prompts:**
    -   `Enter the WordPress website URL to monitor:` Type or paste the full URL of the site you want to watch (e.g., `https://example.com`).
    -   `Enter the monitoring interval in seconds:` Type how often you want to check the site. `60` is a good starting point.

That's it! The monitor is now running. You will see a "SUCCESS" message for every good check and a big warning for every failure. To stop it, just press `Ctrl+C`.

---

## Technical Deep Dive (For Power Users)

### Architecture & Design

The application is built on a modular, single-threaded (with a non-blocking GUI thread) architecture using robust, modern Python libraries.

-   **`httpx`:** A modern, high-performance asynchronous-capable HTTP client. Used here for its simple synchronous API, robustness, and header control.
-   **`schedule`:** A lightweight and human-friendly library for job scheduling. It forms the core of the monitoring loop.
-   **`colorama`:** Provides cross-platform colored terminal text, essential for the high-visibility console alerts.
-   **`logging`:** Python's built-in logging module is configured for structured output to both the console and a persistent file (`website_health.log`).
-   **`tkinter` / `threading`:** On Windows, a `tkinter` GUI alert is launched in a separate `threading.Thread` to prevent the main monitoring loop from being blocked by the UI window. The thread is set as a daemon so it doesn't prevent the main application from exiting.

### Health Check Logic Explained

The `check_website_health()` function is the heart of the application. It performs its checks in a specific, logical order.

1.  **CDN-Friendly HTTP Request:** The request is not a simple `get()`. It includes specific headers to ensure the data is fresh:
    -   `"User-Agent": "WordPress-Health-Checker/2.0"`: Identifies our script so system administrators can easily filter it in logs.
    -   `"Cache-Control": "no-cache"` & `"Pragma": "no-cache"`: These are standard directives that instruct most CDNs (like Cloudflare) and reverse proxies (like Varnish) to revalidate their cached version with the origin server before responding. This prevents us from getting a "healthy" signal from a cached page while the real server is actually down.

2.  **HTTP Status Code Validation:** The response status code is checked to be in the `200 <= status_code < 400` range. This correctly classifies all `2xx` (Success) and `3xx` (Redirection) codes as "reachable." It correctly flags `4xx` (Client Error) and `5xx` (Server Error) codes as failures.

3.  **WordPress Signature Check:** If the status is okay, we perform a crucial final check. Instead of just looking for a `<body>` tag, we check if the string `"wp-content"` exists anywhere in the response text (`response.text`). This is a far more reliable indicator for a WordPress site because:
    -   Almost every WordPress theme and plugin loads assets (CSS, JS, images) from the `/wp-content/` directory.
    -   A generic "Under Construction" or server error page might return a 200 status with a valid `<body>`, but it will almost never contain a link to `/wp-content/`. This check effectively filters out such "soft failures."

### Customization & Extension

The code is clean and easy to modify.

-   **Change Request Timeout:** In `check_website_health`, modify the `timeout=15` parameter in the `httpx.get()` call.
-   **Modify Headers:** Add or change headers in the `headers` dictionary within `check_website_health`.
-   **Customize GUI Alert:** In the `_show_tkinter_alert` function, you can change the alert duration by modifying `root.after(7000, ...)`, or alter the colors, fonts, and window size using standard `tkinter` methods.
-   **Change Log File:** Modify the `filename` in `logging.FileHandler("website_health.log")`.

### Testing Strategy

To ensure reliability, a comprehensive test suite should be created using a framework like `pytest` and Python's built-in `unittest.mock`.

-   **Mock `httpx.get`:** The core of testing involves mocking `httpx.get` to simulate various scenarios without making real network requests. You can make it return different status codes, response text, or even raise exceptions like `httpx.Timeout`.
-   **Mock `sys.platform`:** To test the GUI alert logic, patch `sys.platform` to be `"win32"` or `"linux"` to verify that the `threading.Thread` for the `tkinter` window is (or is not) created under the correct conditions.
-   **Capture `print` and `logging` Output:** Use `capsys` or `caplog` fixtures in `pytest` to assert that the correct messages are printed to the console and logged to the file.

---

### Troubleshooting

-   **`ModuleNotFoundError`:** If you see this, it means a required library is missing. Run `pip install httpx schedule colorama` again.
-   **Connection Errors in Log:** If you consistently see connection errors, verify:
    1.  The URL is correct (including `https://`).
    2.  Your internet connection is active.
    3.  The target website is not blocking your IP address.
-   **GUI Window Doesn't Appear (On Windows):**
    1.  Ensure you have a standard Python installation, as `tkinter` is usually included. A minimal or embedded Python distribution might lack it.
    2.  Check the console for any `tkinter` related error messages.

---

### License

This project is licensed under the **MIT License**. You are free to use, modify, and distribute it for any purpose.