# services/deck_service.py
from parsers.unified_loader import load_deck
from typing import Union
import os


def get_deck(source: Union[str, os.PathLike], is_ydk: bool = False, is_path: bool = True) -> list[str]:
    """
    加载卡池列表（文本或路径），支持常规文本与 YDK 格式。

    这是服务层函数，封装了解析逻辑，屏蔽底层实现细节，对外提供统一调用接口。

    参数:
    - source: Union[str, os.PathLike]
        表示卡组的来源，可以是：
        - 文件路径（如 .txt 或 .ydk 文件）
        - 或者是直接传入的字符串（若 is_path=False）

    - is_ydk: bool, 默认为 False
        指示是否使用 YDK 格式解析。
        - True: 使用 YDK 格式（专为游戏王卡组设计的格式）
        - False: 使用普通文本格式解析

    - is_path: bool, 默认为 True
        指示 source 是不是一个文件路径。
        - True: 从文件路径读取文本内容
        - False: 直接将 source 视为原始文本内容

    返回值:
    - list[str]
        返回解析后的卡牌名列表，每张卡牌根据其数量在列表中重复出现。
        示例返回值: ['青眼白龙', '青眼白龙', '黑魔导', '黑魔导', '黑魔导']
    """

    # 调用底层加载函数，根据输入参数决定解析方式
    return load_deck(source, is_ydk=is_ydk, is_path=is_path)

