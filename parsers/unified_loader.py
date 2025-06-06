from .condition_parser import parse_condition_text
from .deck_parser import parse_deck_text
from .ydk_parser import parse_ydk_text
from typing import Union
import os

def read_text(source: Union[str, os.PathLike], is_path=True) -> str:
    if is_path:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    return source

def load_deck(source: Union[str, os.PathLike], is_ydk=False, is_path=True) -> list[str]:
    text = read_text(source, is_path)
    if is_ydk:
        main, _, _ = parse_ydk_text(text)
        return main
    return parse_deck_text(text)

def load_conditions(source: Union[str, os.PathLike], is_path=True):
    """
    加载条件组与注释标题（返回 tuple: List[List[Condition]], List[str]）
    注意：本模块不依赖 entity 层，返回值结构文档化而非类型标注
    """
    text = read_text(source, is_path)
    return parse_condition_text(text)
