# services/ydk_service.py
from parsers.ydk_parser import parse_ydk_text
from config.settings import API_BASE
from utils.file_utils import write_to_file
from concurrent.futures import ThreadPoolExecutor
import requests
from collections import defaultdict
import re,os
from typing import Dict, List,Union
from parsers.ydk_parser import clean_card_name

from services.local_db_service import get_local_db

db = get_local_db()  # 使用单例模式获取唯一数据库实例


def extract_field(types: str) -> str:
    """从 YGO 卡牌类型字符串中提取字段标签，并优化族/属性表示"""
    if not types or '[' not in types:
        return ""

    try:
        main_part = types.split('\n', 1)[0].strip()
        category_str = main_part.split(']')[0].strip('[')
        categories = [c.strip() for c in category_str.split('|') if c.strip()]
        extra_str = main_part.split(']', 1)[1].strip()

        combined = []

        # 添加主类别字段（如：怪兽、效果）
        combined.extend(categories)

        # 处理“种族/属性”结构
        if '/' in extra_str:
            race, attr = [s.strip() for s in extra_str.split('/', 1)]
            if race:
                combined.append(f"{race}族")
            if attr:
                combined.append(f"{attr}属性")
        else:
            # 没有斜杠时直接添加
            parts = re.split(r'[\\/\s、，；]', extra_str)
            for part in parts:
                part = part.strip()
                if part:
                    combined.append(part)

        # 去重并返回
        unique_fields = []
        for word in combined:
            if word and word not in unique_fields:
                unique_fields.append(word)

        return '、'.join(unique_fields)
    except Exception as e:
        print(f"[ERROR] 字段提取失败: {e}")
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


def ensure_hand_traps_loaded():
    """
    确保手坑卡组已加载并添加了“手坑”字段。
    """
    hand_trap_file = "data/手坑.ydk"

    # 解析手坑文件中的卡牌 ID
    with open(hand_trap_file, 'r', encoding='utf-8') as f:
        ydk_content = f.read()
    main_ids, _, _ = parse_ydk_text(ydk_content)

    # 分类处理：已存在 / 需要下载 / 需要加字段
    need_fetch = []
    need_update = []

    for cid in main_ids:
        if cid not in db.existing_ids:
            need_fetch.append(cid)
        elif "手坑" not in db.get_card_fields(cid):
            need_update.append(cid)

    # 1. 下载缺失卡牌数据
    if need_fetch:
        print(f"🔍 发现 {len(need_fetch)} 张未记录的手坑卡牌，正在下载...")
        batch_fetch_missing(need_fetch)

    # 2. 更新字段（包括刚下载的新卡）
    all_hand_trap_ids = sorted(set(main_ids), key=int)
    for cid in all_hand_trap_ids:
        db.add_card_attribute(cid, "field", "手坑")

    print("✅ 手坑卡组已确保加载，并已添加“手坑”字段")


def fetch_card(card_id: str):
    """
    根据卡牌 ID 请求远程 API 获取数据。
    :param card_id: 卡牌 ID
    :return: 包含 id、name、field 的字典 或 None
    """
    try:
        resp = requests.get(f"{API_BASE}{card_id}", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict):
                return process_raw_data(card_id, data)
            elif isinstance(data, list) and data and isinstance(data[0], dict):
                return process_raw_data(card_id, data[0])
    except Exception as e:
        print(f"[ERROR] 获取卡牌 {card_id} 数据失败: {e}")
        return None


def batch_fetch_missing(ids: List[str]):
    """
    批量下载缺失卡牌数据，并保存进本地数据库。
    :param ids: 缺失的卡牌 ID 列表
    """
    missing = [cid for cid in ids if cid not in db.existing_ids]
    if not missing:
        return

    print(f"🔍 发现 {len(missing)} 张未记录的卡牌，正在批量下载...")

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(fetch_card, missing))

    new_cards = [c for c in results if c]
    if new_cards:
        db.save_new_cards(new_cards)


def load_ydk_file(source: Union[str, os.PathLike], is_path: bool = True, field_tag: str = None) -> List[str]:
    """
    加载并解析 YDK 数据，返回主卡组的卡牌名称列表。
    同时会自动补全缺失卡牌数据，并添加指定字段。

    参数:
        source (Union[str, PathLike]): 文件路径 或 纯文本内容
        is_path (bool): 是否是文件路径
        field_tag (str): 字段标签（如“手坑”），用于数据库更新

    返回:
        List[str]: 卡牌名称列表
    """
    try:
        ydk_content = open(source, 'r', encoding='utf-8').read() if is_path else source.strip()

        main_ids, extra_ids, side_ids = parse_ydk_text(ydk_content)

        all_ids = main_ids + extra_ids + side_ids
        batch_fetch_missing(all_ids)

        if field_tag:
            unique_ids = sorted(set(all_ids), key=int)
            for cid in unique_ids:
                db.add_card_attribute(cid, "field", field_tag)

        return [clean_card_name(db.get_card_name(cid)) for cid in main_ids]

    except Exception as e:
        print(f"[ERROR] 加载或解析 YDK 数据失败: {e}")
        return []




def export_to_txt(main_ids: List[str], extra_ids: List[str], side_ids: List[str], output_file: str = None):
    ensure_hand_traps_loaded()
    combined_ids = main_ids  # ✅ 仅导出主卡组
    batch_fetch_missing(combined_ids)

    name_counter = defaultdict(int)
    for cid in combined_ids:
        name = db.get_card_name(cid).replace('“', '').replace('”', '')
        name_counter[name] += 1

    lines = ["#main"] + [f"{name}，{count}" for name, count in sorted(name_counter.items())]

    # 使用 resolve_path 构建正确路径
    if output_file:
        result_path = write_to_file(lines, output_file, "data", "构筑")
    else:
        result_path = write_to_file(lines, "征服斗魂构筑.txt", "data", "构筑")

    print(f"✅ 构筑文件已保存至：{result_path}")
    print(f"[ydk_service] 数据库缓存大小: {len(db.id_attr_map)}")


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