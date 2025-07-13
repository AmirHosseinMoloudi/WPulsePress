import httpx
import schedule
import time
import logging
import sys
import threading

# Conditional import for GUI warning on Windows
if sys.platform == "win32":
    import tkinter as tk

from colorama import init, Fore, Style

# --- Initialize Colorama for cross-platform colored output ---
init(autoreset=True)

# --- Structured Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("website_health.log"),
        logging.StreamHandler()
    ]
)

def _show_tkinter_alert(url, reason):
    """
    Creates and shows a non-blocking tkinter alert window.
    Intended to be run in a separate thread to not block the main loop.
    """
    try:
        root = tk.Tk()
        root.title("!!! WEBSITE ALERT !!!")
        root.configure(bg='darkred')
        root.attributes("-topmost", True)

        message = f"HEALTH ALERT\n\nWebsite:\n{url}\n\nReason:\n{reason}"
        label = tk.Label(root, text=message, font=("Arial", 18, "bold"), 
                         bg='darkred', fg='white', wraplength=500, justify="center")
        label.pack(pady=40, padx=40)

        root.update_idletasks()
        width, height = root.winfo_width(), root.winfo_height()
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f'{width}x{height}+{x}+{y}')
        
        root.after(7000, root.destroy)
        root.mainloop()
    except Exception as e:
        logging.error(f"Failed to create tkinter alert: {e}")

def display_huge_warning(url, reason):
    """
    Displays console warning and launches a GUI alert on Windows.
    """
    print(Fore.RED + Style.BRIGHT + """
*****************************************************************
*                                                               *
*                  !!! WEBSITE ALERT !!!                        *
*                                                               *
*****************************************************************
    """)
    print(Fore.YELLOW + f"  Unhealthy Status Detected for: {url}")
    print(Fore.YELLOW + f"  Reason: {reason}")
    print(Fore.RED + Style.BRIGHT + "*****************************************************************\n")

    if sys.platform == "win32":
        alert_thread = threading.Thread(target=_show_tkinter_alert, args=(url, reason))
        alert_thread.daemon = True
        alert_thread.start()

def check_website_health(url: str):
    """
    Checks website health using CDN-friendly headers.
    """
    # --- CDN-Friendly Headers ---
    # User-Agent: Identifies our bot.
    # Cache-Control/Pragma: Asks CDNs to revalidate with the origin server,
    # ensuring we get a fresh check, not a stale cached version.
    headers = {
        "User-Agent": "WordPress-Health-Checker/2.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    try:
        response = httpx.get(url, timeout=15, follow_redirects=True, headers=headers)

        if not (200 <= response.status_code < 400):
            reason = f"Website returned a non-successful status code: {response.status_code}"
            logging.warning(reason)
            display_huge_warning(url, reason)
            return

        if "wp-content" not in response.text:
            reason = "WordPress check failed: Signature 'wp-content' not found in page source."
            logging.warning(reason)
            display_huge_warning(url, reason)
            return

        logging.info(f"SUCCESS: {url} is healthy. Status: {response.status_code}. WordPress signature found.")

    except httpx.ConnectError:
        reason = f"Connection Error: Could not connect to {url}. Server may be down or domain incorrect."
        logging.error(reason)
        display_huge_warning(url, reason)
    except httpx.Timeout:
        reason = f"Timeout Error: The request to {url} timed out after 15 seconds."
        logging.error(reason)
        display_huge_warning(url, reason)
    except Exception as e:
        reason = f"An unexpected error occurred: {e}"
        logging.error(reason)
        display_huge_warning(url, reason)

def main():
    """
    Main function to get user input and start the monitoring schedule.
    """
    website_url = input("Enter the WordPress website URL to monitor: ")
    try:
        interval_str = input("Enter the monitoring interval in seconds (>=30 recommended): ")
        interval = int(interval_str)
        if interval <= 0:
            logging.error("Interval must be a positive number.")
            return
        if interval < 30:
            print(Fore.YELLOW + "Warning: An interval under 30 seconds is not recommended for production sites.")
    except ValueError:
        logging.error("Invalid interval. Please enter a whole number.")
        return

    logging.info(f"Starting CDN-friendly health monitoring for {website_url} every {interval} seconds.")
    if sys.platform == "win32":
        logging.info("Windows OS detected: GUI alerts will be shown on failure.")
    logging.info("Press Ctrl+C to stop the monitor.")
    
    check_website_health(website_url)
    schedule.every(interval).seconds.do(check_website_health, url=website_url)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Shutdown signal received. Stopping the website monitor.")
        print("\nMonitoring stopped.")

if __name__ == "__main__":
    main()