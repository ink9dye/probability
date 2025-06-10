# # services/parser_service.py
#
# from core.handlers import load_file
# from typing import List, Dict, Set, Optional, Union,Tuple
# import os
#
#
# def load_deck(source: Union[str, os.PathLike], is_ydk: bool = False, is_path: bool = True) -> list[str]:
#     """
#     加载并解析卡组文件或文本内容。
#     支持 YDK 或 TXT 构筑格式。
#     """
#     return load_file(source, "ydk" if is_ydk else "deck")
#
#
# def load_conditions(source: Union[str, os.PathLike], is_path: bool = True):
#     """
#     加载并解析条件文件。
#     返回 (conditions, titles)
#     """
#     return load_file(source, "condition")
#
#
# def load_ydk(source: Union[str, os.PathLike], is_path=True) -> tuple[list[str], list[str], list[str]]:
#     """
#     加载 YDK 格式的主/额外/副卡组（ID 列表）
#     """
#     result = load_file(source, "ydk",is_path=is_path)
#     return result["main"], result["extra"], result["side"]
