import unicodedata
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from urllib.parse import urljoin

# Helper function to normalize names for matching
def normalize_name(name):
    # Remove spaces and normalize full-width characters
    return unicodedata.normalize("NFKC", name).replace(" ", "").replace("　", "")

# Determine the project root directory based on this file's location
# This assumes common_scraper_utils.py is in scripts/scraping/
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

def save_data_to_json(data, filename, data_dir_name="data"):
    """Saves data to a JSON file in a subdirectory of the project root."""
    # data_dir is now relative to PROJECT_ROOT
    data_dir = PROJECT_ROOT / data_dir_name
    data_dir.mkdir(parents=True, exist_ok=True)
    
    file_path = data_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} items to {file_path}")
