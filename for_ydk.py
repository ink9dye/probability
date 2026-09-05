"""
向后兼容：原 for_ydk 脚本请改用 services.ydk_service / ydk_main.py。
"""

from infrastructure.card_db import LocalCardDB, get_card_db
from parsers.ydk_parser import parse_ydk_text as parse_ydk
from services.ydk_service import (
    batch_fetch_missing,
    export_ydk_to_deck_txt,
    extract_field,
    fetch_card,
    load_ydk_pool,
    process_raw_data,
)

API_BASE = __import__("app.settings", fromlist=["API_BASE"]).API_BASE
CSV_FILE = str(__import__("app.settings", fromlist=["CSV_FILE"]).CSV_FILE)
CSV_HEADERS = __import__("app.settings", fromlist=["CSV_HEADERS"]).CSV_HEADERS

__all__ = [
    "LocalCardDB",
    "get_card_db",
    "parse_ydk",
    "batch_fetch_missing",
    "export_ydk_to_deck_txt",
    "load_ydk_pool",
    "fetch_card",
    "process_raw_data",
    "extract_field",
    "API_BASE",
    "CSV_FILE",
    "CSV_HEADERS",
]
