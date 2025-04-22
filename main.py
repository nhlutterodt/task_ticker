'''
main.py - Task Ticker Entry Point
Author: Neils Haldane-Lutterodt
'''

import tkinter as tk
from ui.app import TaskTickerApp
import logging
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    root = tk.Tk()
    app = TaskTickerApp(root)
    app = TaskTickerApp(root)
    root.mainloop()
    logging.info("Application closed.")
    logging.info("Exiting Task Ticker...")      
