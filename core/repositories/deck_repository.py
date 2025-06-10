# core/repository/deck_repository.py
from typing import List, Dict, Set, Optional, Union, Tuple
from .unified_repository import UnifiedRepository


class DeckRepository:
    """
    卡牌数据访问接口
    """

    def __init__(self):
        self.repo = UnifiedRepository()

    def load_card_pool(self, file_path: str) -> List[str]:
        """
        加载 TXT 卡池文件，返回展开后的卡名列表
        """
        return self.repo.load(file_path, 'deck')

    def save_card_pool(self, file_path: str, card_pool: List[str]):
        """
        将卡池保存为 TXT 文件
        """
        self.repo.save(file_path, 'deck', card_pool)
