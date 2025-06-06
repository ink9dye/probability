# services/ydk_service.py

from parsers.ydk_parser import parse_ydk_text
from services.local_db_service import LocalCardDB
from config.settings import API_BASE, CSV_FILE, CSV_HEADERS
from utils.file_utils import write_to_file
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
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
    """
    加载并解析 YDK 文件，仅保留 main 区域，并按 ID 升序排序。
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        ydk_content = f.read()

    main_ids, _, _ = parse_ydk_text(ydk_content)
    all_ids = main_ids  # 不再包含 extra/side

    batch_fetch_missing(all_ids)

    # 去重 + 按数字升序排列
    unique_ids = sorted(set(all_ids), key=int)

    return [db.get_card_name(cid) for cid in unique_ids]


def export_to_txt(main_ids: list[str], extra_ids: list[str], side_ids: list[str],
                  output_file: str = None):
    from collections import defaultdict

    if not main_ids:
        combined_ids = extra_ids + side_ids
        print("⚠️ main 部分为空，将 extra/side 合并为主卡组")
    else:
        combined_ids = main_ids

    batch_fetch_missing(combined_ids)

    name_counter = defaultdict(int)
    for cid in combined_ids:
        name = db.get_card_name(cid).replace('“', '').replace('”', '')
        name_counter[name] += 1

    lines = ["#main"] + [f"{name}，{count}" for name, count in sorted(name_counter.items())]

    # 使用统一的文件写入工具
    result_path = write_to_file(lines, output_file or "我的构筑.txt", "构筑")

    print(f"✅ 构筑文件已保存至：{result_path}")


