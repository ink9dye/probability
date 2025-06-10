# services/writer_service.py
from config.settings import DECK_DIR, CONDITION_DIR
from core.writers.unified_writer import write_data
import os
from utils.file_utils import resolve_path

def save_data(file_path: str, data_type: str, data, titles: list[str] = None):
    """
    保存数据到文件
    :param file_path: 文件路径
    :param data_type: 数据类型 ('deck' / 'condition')
    :param data: 数据内容
    :param titles: 标题行（可选）
    """
    return write_data(file_path, data_type, data, titles)

def export_data(file_name: str, data_type: str, data, titles: list = None, *subdirs) -> str:
    """
    统一导出入口。用于导出 deck/condition 数据。
    """
    if data_type == "deck":
        full_path = resolve_path(DECK_DIR, file_name)
    elif data_type == "condition":
        full_path = resolve_path(CONDITION_DIR, file_name)
    else:
        full_path = resolve_path(*subdirs, file_name)

    write_data(file_path=full_path, data_type=data_type, data=data, titles=titles)
    print(f"📦 已导出 {data_type} 至：{full_path}")
    return full_path
