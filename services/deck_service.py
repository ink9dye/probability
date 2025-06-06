# services/deck_service.py
from parsers.unified_loader import load_deck
from typing import Union
import os

def get_deck(source: Union[str, os.PathLike], is_ydk: bool = False, is_path: bool = True) -> list[str]:
    """
    加载卡池列表（文本或路径），自动判断 YDK 模式或文本格式。
    """
    return load_deck(source, is_ydk=is_ydk, is_path=is_path)
