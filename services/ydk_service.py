# services/ydk_service.py

from parsers.ydk_parser import parse_ydk_text
from services.local_db_service import LocalCardDB
from config.settings import API_BASE, CSV_FILE, CSV_HEADERS
from utils.file_utils import write_to_file
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import requests
import os
import re
from typing import Dict, List

db = LocalCardDB()



def extract_field(types: str) -> str:
    """
    从 YGO 卡牌类型字符串中提取基础字段标签，例如：
        "[怪兽|效果] 兽战士/暗" → "怪兽、效果、兽战士、暗"
    """

    if not types or '[' not in types:
        return ""

    try:
        main_part = types.split('\n', 1)[0].strip()

        # 提取 [怪兽|效果]
        category_str = main_part.split(']', 1)[0].strip('[')
        categories = [c.strip() for c in category_str.split('|') if c.strip()]

        # 提取 ] 后面的部分，如 "兽战士/暗"
        extra_str = main_part.split(']', 1)[1].strip()
        extra_parts = []

        for part in re.split(r'[\\/\s、，；]', extra_str):
            word = part.strip()
            if word and len(word) <= 3:
                extra_parts.append(word)

        combined = []
        for word in categories + extra_parts:
            if word and word not in combined:
                combined.append(word)

        return '、'.join(combined)
    except Exception as e:
        print(f"Error extracting field from '{types}': {e}")
        return ""


def process_raw_data(card_id: str, data: dict) -> Dict:

    # print(f"卡片数据为{data}")

    text_section = data.get("text", {})
    name = text_section.get("name", "")
    types = text_section.get("types", "")

    # 提取基础字段（来自 types）
    field_parts = extract_field(types).split('、')

    # 添加卡名到字段（可选）
    if name:
        field_parts.append(name)

    card_data = data

    level = card_data.get("level")

    # 如果是怪兽卡且有 level，则添加星级字段
    if level:
        chinese_level = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十"].get(level - 1, str(level))
        field_parts.append(f"{chinese_level}星")
        field_parts.append(f"{level}星")

    # 去重并保持顺序
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

            # ✅ 打印从 API 获取到的完整原始数据
            print("\n[DEBUG]API返回信息:")
            print(data)

            return process_raw_data(card_id, data)
        else:
            print(f"[ERROR] 获取卡牌 {card_id} 失败，HTTP 状态码：{resp.status_code}")
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


if __name__ == "__main__":
    # 测试用卡牌 ID
    card_id = "11317977"  # 月光黑羊

    print(f"[INFO] 开始获取卡牌 {card_id} 数据...")

    # 第一步：调用 fetch_card 获取并处理数据
    result = fetch_card(card_id)

    if result:
        print("\n[RESULT] fetch_card 返回的数据结构如下：")
        print(result)
    else:
        print("\n[ERROR] fetch_card 返回 None，请检查网络或 API 是否正常。")
