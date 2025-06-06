# services/ydk_service.py
from parsers.ydk_parser import parse_ydk_text
from services.local_db_service import LocalCardDB
from concurrent.futures import ThreadPoolExecutor
from config.settings import API_BASE, CSV_FILE, CSV_HEADERS
import requests
import time
import os

db = LocalCardDB()

def fetch_card(card_id: str):
    try:
        resp = requests.get(f"{API_BASE}{card_id}", timeout=5)

        if resp.status_code == 200:
            data = resp.json()
            return {
                "id": card_id,
                "name": data.get("text", {}).get("name", ""),
            }
    except Exception as e:
        print(f"Error fetching {card_id}: {e}")
    return None

def batch_fetch_missing(ids: list[str]):
    missing = [cid for cid in ids if cid not in db.existing_ids]
    if not missing:
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_card, missing)
        new_cards = [c for c in results if c]
        if new_cards:
            db.save_new_cards(new_cards)

def load_ydk_file(file_path: str) -> list[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        ydk_content = f.read()
    main_ids, extra_ids, _ = parse_ydk_text(ydk_content)
    all_ids = main_ids + extra_ids  # 可选：是否包含 side？
    batch_fetch_missing(all_ids)
    return [db.get_card_name(cid) for cid in all_ids]

def export_to_txt(main_ids: list[str], extra_ids: list[str], side_ids: list[str],
                  output_file: str = "output.txt"):
    from collections import defaultdict

    name_counter = defaultdict(int)
    for cid in main_ids + extra_ids + side_ids:
        name = db.get_card_name(cid)
        name_counter[name] += 1

    lines = ["#main"]
    for name, count in sorted(name_counter.items()):
        lines.append(f"{name}，{count}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"✅ 已导出构筑到 {output_file}")
