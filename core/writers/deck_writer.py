# writers/deck_writer.py

from utils.file_utils import write_to_file


def write_deck(file_path: str, card_pool: list[str]):
    """
    将卡组列表写入 TXT 文件。
    每行格式为 "卡名,数量"
    """
    from collections import Counter
    lines = [f"{card},{count}" for card, count in Counter(card_pool).items()]
    write_to_file(lines, file_path)
