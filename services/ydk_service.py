import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Dict, List

import requests

from app.settings import API_BASE
from infrastructure.card_db import get_card_db
from infrastructure.file_storage import read_text
from parsers.ydk_parser import parse_ydk_text

_db = get_card_db()


def extract_field(types: str) -> str:
    if not types or "[" not in types:
        return ""
    try:
        main_part = types.split("\n", 1)[0].strip()
        category_str = main_part.split("]", 1)[0].strip("[")
        categories = [c.strip() for c in category_str.split("|") if c.strip()]
        extra_str = main_part.split("]", 1)[1].strip()
        extra_parts = [
            p.strip()
            for p in re.split(r"[\\/\s、，；]", extra_str)
            if p.strip() and len(p.strip()) <= 3
        ]
        combined: list[str] = []
        for word in categories + extra_parts:
            if word and word not in combined:
                combined.append(word)
        return "、".join(combined)
    except Exception:
        return ""


def process_raw_data(card_id: str, data: dict) -> Dict:
    text_section = data.get("text", {})
    name = text_section.get("name", "")
    types = text_section.get("types", "")
    field_parts = [x for x in extract_field(types).split("、") if x]
    if name:
        field_parts.append(name)

    card_data = data.get("data", {})
    level = card_data.get("level")
    if level and 1 <= level <= 13:
        digits = ["一", "二", "三", "四", "五", "六", "七", "八", "九", "十", "十一", "十二", "十三"]
        field_parts.append(f"{digits[level - 1]}星")
        field_parts.append(f"{level}星")

    unique: list[str] = []
    for part in field_parts:
        if part not in unique:
            unique.append(part)

    return {"id": card_id, "name": name, "field": "、".join(unique)}


def fetch_card(card_id: str) -> dict | None:
    try:
        resp = requests.get(f"{API_BASE}{card_id}", timeout=10)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if isinstance(data, dict):
            return process_raw_data(card_id, data)
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return process_raw_data(card_id, data[0])
    except Exception:
        pass
    return None


def batch_fetch_missing(ids: List[str]) -> int:
    missing = [cid for cid in ids if cid not in _db.existing_ids]
    if not missing:
        return 0
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_card, missing)
        new_cards = [c for c in results if c]
    if new_cards:
        return _db.save_new_cards(new_cards)
    return 0


def parse_ydk_file(path: str | Path) -> tuple[list[str], list[str], list[str]]:
    content = read_text(path)
    if not content:
        return [], [], []
    return parse_ydk_text(content)


def load_ydk_pool(
    path: str | Path,
    *,
    sections: tuple[str, ...] = ("main",),
) -> list[str]:
    """
    从 YDK 加载卡池（卡名列表，按 main 区张数展开）。
    会先补全本地数据库中缺失的卡。
    """
    main_ids, extra_ids, side_ids = parse_ydk_file(path)
    section_map = {"main": main_ids, "extra": extra_ids, "side": side_ids}
    ids: list[str] = []
    for sec in sections:
        ids.extend(section_map.get(sec, []))
    batch_fetch_missing(ids)
    return [ _db.get_card_name(cid) for cid in ids ]


def export_ydk_to_deck_txt(
    path: str | Path,
    output_file: str | Path | None = None,
    *,
    use_main_only: bool = True,
) -> Path:
    """YDK → 中文版构筑 txt（卡名，张数），供本项目的标签构筑流程继续编辑。"""
    main_ids, extra_ids, side_ids = parse_ydk_file(path)
    combined = main_ids if use_main_only else main_ids + extra_ids + side_ids
    batch_fetch_missing(combined)

    name_counter: dict[str, int] = defaultdict(int)
    for cid in combined:
        name = _db.get_card_name(cid).replace(""", "").replace(""", "")
        name_counter[name] += 1

    lines = ["#main"] + [f"{name}，{count}" for name, count in sorted(name_counter.items())]
    out = Path(output_file or Path(path).with_suffix(".txt"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out
