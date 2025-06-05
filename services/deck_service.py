# services/deck_service.py

from core.file_read import parse_first_document
from typing import List

class DeckService:
    def __init__(self):
        self.card_pool = []

    def load_deck_from_file(self, file_path: str) -> List[str]:
        """
        从文件中加载卡池，并返回卡池列表。
        """
        file_content = read_file(file_path)
        if file_content:
            self.card_pool = parse_first_document(file_content)
            return self.card_pool
        return []

    def get_card_pool(self) -> List[str]:
        """
        获取当前卡池。
        """
        return self.card_pool

    def add_cards(self, cards: List[str]):
        """
        向卡池中添加卡片。
        """
        self.card_pool.extend(cards)

    def remove_cards(self, cards: List[str]):
        """
        从卡池中移除卡片。
        """
        for card in cards:
            if card in self.card_pool:
                self.card_pool.remove(card)

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
