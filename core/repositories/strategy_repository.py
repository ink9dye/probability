# core/repository/strategy_repository.py
from typing import List, Dict, Set, Optional, Union

from .unified_repository import UnifiedRepository


class StrategyRepository:
    """
    策略数据访问接口
    """

    def __init__(self):
        self.repo = UnifiedRepository()

    def load_strategies(self, file_path: str) -> List['Strategy']:
        return self.repo.load(file_path, 'strategy')

    def save_strategies(self, file_path: str, strategies: List['Strategy']):
        self.repo.save(file_path, 'strategy', strategies)
