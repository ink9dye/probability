# core/repository/condition_repository.py
from typing import List, Dict, Set, Optional, Union, Tuple
from .unified_repository import UnifiedRepository
from core.entity.composite_condition import CompositeCondition


class ConditionRepository:
    """
    条件数据访问接口
    """

    def __init__(self):
        self.repo = UnifiedRepository()

    def load_conditions(self, file_path: str) -> Tuple[List[CompositeCondition], List[str]]:
        conditions, titles = self.repo.load(file_path, 'condition')
        return conditions, titles

    def save_conditions(self, file_path: str, conditions: List[CompositeCondition], titles: List[str] = None):
        self.repo.save(file_path, 'condition', conditions, titles)
