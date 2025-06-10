# config/settings.py
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

API_BASE = "https://ygocdb.com/api/v0/card/"
CSV_FILE = os.path.join(PROJECT_ROOT, "data", "local_cards.csv")
CSV_HEADERS = ["id", "name", "field"]


DECK_DIR = os.path.join(PROJECT_ROOT, "data", "构筑")      # 存放卡组构筑
CONDITION_DIR = os.path.join(PROJECT_ROOT, "data", "启动")  # 存放条件文件

STRATEGY_FILE = os.path.join(PROJECT_ROOT, "data", "strategies.json")