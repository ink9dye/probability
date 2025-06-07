# services/ydk_service.py
from parsers.ydk_parser import parse_ydk_text
from services.local_db_service import LocalCardDB
from config.settings import API_BASE
from utils.file_utils import write_to_file
from concurrent.futures import ThreadPoolExecutor
import requests
import re
from typing import Dict, List

db = LocalCardDB()


def extract_field(types: str) -> str:
    """从 YGO 卡牌类型字符串中提取字段标签。"""
    if not types or '[' not in types:
        return ""
    try:
        main_part = types.split('\n', 1)[0].strip()
        category_str = main_part.split(']', 1)[0].strip('[')
        categories = [c.strip() for c in category_str.split('|') if c.strip()]
        extra_str = main_part.split(']', 1)[1].strip()
        extra_parts = [part.strip() for part in re.split(r'[\\/\s、，；]', extra_str) if part.strip() and len(part.strip()) <= 3]
        combined = []
        for word in categories + extra_parts:
            if word and word not in combined:
                combined.append(word)
        return '、'.join(combined)
    except Exception:
        return ""


def process_raw_data(card_id: str, data: dict) -> Dict:
    text_section = data.get("text", {})
    name = text_section.get("name", "")
    types = text_section.get("types", "")
    field_parts = extract_field(types).split('、')
    if name:
        field_parts.append(name)

    card_data = data.get("data", {})
    level = card_data.get("level")
    if level and 1 <= level <= 13:
        chinese_digits = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三"]
        chinese_level = chinese_digits[level - 1]
        field_parts.append(f"{chinese_level}星")
        field_parts.append(f"{level}星")

    unique_field_parts = []
    for part in field_parts:
        if part not in unique_field_parts:
            unique_field_parts.append(part)

    return {
        "id": card_id,
        "name": name,
        "field": '、'.join(unique_field_parts)
    }


def fetch_card(card_id: str):
    try:
        resp = requests.get(f"{API_BASE}{card_id}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return process_raw_data(card_id, data)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return process_raw_data(card_id, data[0])
    except Exception:
        pass
    return None


def batch_fetch_missing(ids: List[str]):
    missing = [cid for cid in ids if cid not in db.existing_ids]
    if not missing:
        return
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_card, missing)
        new_cards = [c for c in results if c]
        if new_cards:
            db.save_new_cards(new_cards)


def load_ydk_file(file_path: str) -> List[str]:
    with open(file_path, 'r', encoding='utf-8') as f:
        ydk_content = f.read()
    main_ids, _, _ = parse_ydk_text(ydk_content)
    batch_fetch_missing(main_ids)
    unique_ids = sorted(set(main_ids), key=int)
    return [db.get_card_name(cid) for cid in unique_ids]


def export_to_txt(main_ids: List[str], extra_ids: List[str], side_ids: List[str], output_file: str = None):
    from collections import defaultdict
    combined_ids = main_ids if main_ids else (extra_ids + side_ids)
    batch_fetch_missing(combined_ids)
    name_counter = defaultdict(int)
    for cid in combined_ids:
        name = db.get_card_name(cid).replace('“', '').replace('”', '')
        name_counter[name] += 1
    lines = ["#main"] + [f"{name}，{count}" for name, count in sorted(name_counter.items())]
    result_path = write_to_file(lines, output_file or "我的构筑.txt", "构筑")
    print(f"✅ 构筑文件已保存至：{result_path}")

if __name__ == "__main__":
    # 测试用卡牌 ID
    card_id = "11317977"  # 月光黑羊

    print(f"[INFO] 开始获取卡牌 {card_id} 数据...")
    # 第一步：调用 fetch_card 获取并处理数据
    result = fetch_card(card_id)

    if result:
        print("[RESULT] fetch_card 返回的数据结构如下：")
        print(result)
    else:
        print("\n[ERROR] fetch_card 返回 None，请检查网络或 API 是否正常。")