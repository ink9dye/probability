# config/settings.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

API_BASE = "https://ygocdb.com/api/v0/card/"
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "local_cards.csv")
CSV_HEADERS = ["id", "name", "field"]
