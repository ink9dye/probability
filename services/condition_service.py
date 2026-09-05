from pathlib import Path
from typing import Union

from domain.conditions.dong_bu import DongBuExclusionRule
from infrastructure.card_db import get_card_db
from infrastructure.file_storage import read_text
from parsers.start_txt import parse_start


def load_conditions_from_source(
    source: Union[str, Path], *, is_path: bool = True
) -> tuple[
    list[list[tuple[str, str, int]]],
    list[int],
    tuple[tuple[str, ...], ...],
    tuple[tuple[str, ...], ...],
    list[str],
    tuple[tuple[str, str], ...],
    tuple[DongBuExclusionRule, ...],
]:
    text = read_text(source) if is_path else str(source)
    if not text:
        return [], [], (), (), [], (), ()
    return parse_start(text)


def validate_condition_keywords(expression: str) -> list[str]:
    """
    对照本地库检查条件中的关键词（用于 GUI 提示，不阻断模拟）。
    返回未能匹配的警告信息列表。
    """
    db = get_card_db()
    warnings: list[str] = []
    for keyword in expression.replace("＋", "+").split("+"):
        keyword = keyword.strip()
        if not keyword or keyword.endswith("-种类"):
            continue
        in_name = any(keyword in name for name in db.get_all_cards().values())
        if not in_name and keyword not in db.get_all_keywords():
            warnings.append(f"关键词「{keyword}」不在本地库卡名/字段中")
    return warnings
