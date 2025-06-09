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
    """
    加载并解析卡组列表，支持普通文本格式与 YDK 格式。

    参数:
    - source: str 或 PathLike
        表示卡组内容来源，可以是一个文件路径，也可以是原始文本字符串。
    - is_ydk: bool, 默认 False
        指定是否以 YDK 格式解析。
    - is_path: bool, 默认 True
        如果为 True，source 被视为文件路径；否则，source 被视为已加载的文本字符串。

    返回值:
    - list[str]
        返回一个卡牌名称列表，卡牌名根据数量进行展开。
    """

    # 读取文本内容，可能是从文件中读取，也可能是直接使用字符串
    text = read_text(source, is_path)

    # 如果是 YDK 格式，使用专用解析器解析主卡组部分
    if is_ydk:
        main, _, _ = parse_ydk_text(text)  # 只返回主卡组
        return main

    # 否则，使用普通文本格式解析
    return parse_deck_text(text)

def load_conditions(source: Union[str, os.PathLike], is_path=True):
    """
    加载条件组与注释标题（返回 tuple: List[List[Condition]], List[str]）
    注意：本模块不依赖 entity 层，返回值结构文档化而非类型标注
    """
    text = read_text(source, is_path)
    return parse_condition_text(text)
