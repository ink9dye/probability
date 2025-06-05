# services/condition_service.py

from core.file_read import parse_second_document, get_comment_lines
from typing import List, Tuple
from collections import Counter


class ConditionService:
    def __init__(self):
        self.conditions_list = []

    def load_conditions_from_file(self, file_path: str) -> List[List[Tuple[str, str, int]]]:
        """
        从文件中加载条件，并返回条件列表。
        """
        file_content = read_file(file_path)
        if file_content:
            self.conditions_list = parse_second_document(file_content)
            return self.conditions_list
        return []

    def check_conditions(self, drawn_cards: List[str], conditions: List[Tuple[str, str, int]]) -> bool:
        """
        检查抽取的卡片是否满足给定的条件。
        """
        card_counts = Counter(drawn_cards)

        for card_name, operator, value in conditions:
            count = card_counts.get(card_name, 0)
            if operator == "大于等于" and count < value:
                return False
            elif operator == "大于" and count <= value:
                return False
            elif operator == "等于" and count != value:
                return False
            elif operator == "小于" and count >= value:
                return False
            elif operator == "小于等于" and count > value:
                return False

        return True

    def get_comment_lines(self, file_path: str) -> List[str]:
        """
        使用 core/file_read.py 中的 get_comment_lines 函数读取注释行
        """
        return get_comment_lines(file_path)


def read_file(file_path: str) -> str:
    """
    读取文件内容。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return ""
