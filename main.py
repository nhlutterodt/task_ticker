'''
main.py - Task Ticker Entry Point
Author: Neils Haldane-Lutterodt
'''

import tkinter as tk
from ui.app import TaskTickerApp
import logging
import time
import os

# Create logs directory if not exists
os.makedirs("logs", exist_ok=True)

# Configure logging to file
logging.basicConfig(
    filename="logs/task_ticker.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    start_time = time.time()
    logging.info("Starting Task Ticker application...")

    root = tk.Tk()
    app = TaskTickerApp(root)
    root.mainloop()

    duration = time.time() - start_time
    logging.info("Application closed.")
    logging.info(f"Exiting Task Ticker... Uptime: {duration:.2f} seconds")
