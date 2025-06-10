# services/file_service.py

from core.handlers import load_file as handler_load
from core.handlers import save_file as handler_save
import os
from typing import List, Any,Union, Optional
from config.settings import DECK_DIR, CONDITION_DIR

def load_file(file_path: str, handler_type: str, is_path: bool = True):
    """
    加载指定类型的文件内容。
    :param file_path: 文件路径或字符串内容
    :param handler_type: 处理器类型（deck / condition / ydk）
    :param is_path: 是否为文件路径
    :return: 解析后的数据对象
    """
    return handler_load(file_path, handler_type, is_path=is_path)


def save_file(file_path: str, handler_type: str, data, titles: list[str] = None):
    """
    保存数据到指定类型的文件。
    :param file_path: 输出路径
    :param handler_type: 处理器类型（deck / condition / ydk）
    :param data: 数据对象
    :param titles: 标题行（可选）
    """
    return handler_save(file_path, handler_type, data, titles=titles)


# ✅ 便捷封装：用于 deck / condition / ydk 的快捷方法

def load_deck(source: str, is_ydk: bool = False, is_path: bool = True):
    return load_file(source, "ydk" if is_ydk else "deck", is_path=is_path)


def load_condition(source: str, is_path: bool = True):
    return load_file(source, "condition", is_path=is_path)


def load_ydk(source: str, is_path: bool = True):
    result = load_file(source, "ydk", is_path=is_path)
    return result["main"], result["extra"], result["side"]


def save_deck(file_path: str, data):
    return save_file(file_path, "deck", data)


def save_condition(file_path: str, data, titles: list[str] = None):
    return save_file(file_path, "condition", data, titles=titles)


def save_ydk(file_path: str, data):
    return save_file(file_path, "ydk", data)

def clean_card_name(name: str) -> str:
    """
    清理卡牌名称中的中文引号、空格、单双引号等。
    示例："“K9案件”" → "K9案件"
    """
    if not name:
        return name
    # 去除两边空白符
    name = name.strip()
    # 去除中文引号、英文引号、空格
    name = name.strip('“”"\' ')
    return name


def export_data(file_path: str, data_type: str, data: List[List[Any]], titles: Optional[List[str]] = None, *subdirs):
    """
    将数据导出到指定路径。

    :param file_path: 文件名或完整路径
    :param data_type: 数据类型（deck / condition / ydk 等）
    :param data: 要保存的数据列表（每项是一个列表）
    :param titles: 标题行（可选）
    :param subdirs: 子目录路径
    """
    # 获取基础目录（如 data/构筑、data/启动）
    base_dirs = {
        "deck": DECK_DIR,
        "condition": CONDITION_DIR,
        # 可以扩展其他类型目录
    }

    if data_type not in base_dirs:
        raise ValueError(f"不支持的数据类型: {data_type}")

    base_dir = base_dirs[data_type]

    # 构建完整路径
    full_path = os.path.join(base_dir, *subdirs)

    # 创建目录（如果不存在）
    os.makedirs(full_path, exist_ok=True)

    # 完整文件路径
    full_file_path = os.path.join(full_path, file_path)

    # 写入文件
    try:
        with open(full_file_path, 'w', encoding='utf-8') as f:
            if titles:
                f.write(','.join(titles) + '\n')
            for row in data:
                f.write(','.join(map(str, row)) + '\n')
        print(f"✅ 已导出至: {full_file_path}")
        return full_file_path
    except Exception as e:
        raise RuntimeError(f"导出失败: {e}")