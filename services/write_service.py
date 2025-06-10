# services/writer_service.py

from core.writers.unified_writer import write_data

def save_data(file_path: str, data_type: str, data, titles: list[str] = None):
    """
    保存数据到文件
    :param file_path: 文件路径
    :param data_type: 数据类型 ('deck' / 'condition')
    :param data: 数据内容
    :param titles: 标题行（可选）
    """
    return write_data(file_path, data_type, data, titles)
