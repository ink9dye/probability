# services/parser_service.py
from parsers.unified_loader import load_deck as parse_deck
from parsers.unified_loader import load_conditions as parse_conditions
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

