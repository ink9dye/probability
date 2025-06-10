# services/parser_service.py
from core.parsers.unified_loader import parse_deck, parse_conditions, parse_ydk,clean_card_name


from typing import Union
import os


def load_deck(source: Union[str, os.PathLike], is_ydk: bool = False, is_path: bool = True) -> list[str]:
    """
    加载并解析卡组文件或文本内容。
    支持 YDK 或 TXT 构筑格式。
    """
    return parse_deck(source=source, is_ydk=is_ydk, is_path=is_path)


def load_conditions(source: Union[str, os.PathLike], is_path: bool = True):
    """
    加载并解析条件文件。
    返回 (conditions, titles)
    """
    return parse_conditions(source=source, is_path=is_path)

def load_ydk(source: Union[str, os.PathLike], is_path=True) -> tuple[list[str], list[str], list[str]]:
    """
    加载 YDK 格式的主/额外/副卡组（ID 列表）
    """
    return parse_ydk(source=source, is_path=is_path)

def clean_card_name(name: str) -> str:
    """
    清理卡牌名称中的中文引号、空格、单双引号等。
    示例："“K9案件”" → "K9案件"
    """
    return clean_card_name(name=name)