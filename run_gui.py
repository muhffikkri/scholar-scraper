"""
Entry point untuk menjalankan GUI aplikasi Google Scholar Scraper.
Double-click file ini atau jalankan dengan: python run_gui.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(__file__))

from src.gui.app import run_gui

if __name__ == "__main__":
    run_gui()
