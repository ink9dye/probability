# core/repository/unified_repository.py

from typing import Union, List, Any, Tuple, Dict
from pathlib import Path

from core.entity.strategy import Strategy, apply_all_strategies
from core.entity.condition import Condition
from core.entity.composite_condition import CompositeCondition


class UnifiedRepository:
    """
    统一数据访问类：封装对各类数据的加载与保存操作。
    支持多种数据类型（卡组、条件、策略等）和多种文件格式（TXT/YDK/JSON）。
    """

    def __init__(self):
        self._loaders = {
            "deck": self._load_deck,
            "condition": self._load_condition,
            "strategy": self._load_strategy,
        }

        self._savers = {
            "deck": self._save_deck,
            "condition": self._save_condition,
            "strategy": self._save_strategy,
        }

    def load(self, file_path: Union[str, Path], data_type: str) -> Any:
        """
        加载指定类型的对象数据
        :param file_path: 文件路径
        :param data_type: 类型（deck/condition/strategy）
        :return: 解析后的数据对象
        """
        loader = self._loaders.get(data_type)
        if not loader:
            raise ValueError(f"不支持的数据类型: {data_type}")
        return loader(file_path)

    def save(self, file_path: Union[str, Path], data_type: str, data: Any, titles: List[str] = None):
        """
        保存指定类型的数据
        :param file_path: 文件路径
        :param data_type: 类型（deck/condition/strategy）
        :param data: 数据内容
        :param titles: 标题行（用于条件等有标题的类型）
        """
        saver = self._savers.get(data_type)
        if not saver:
            raise ValueError(f"不支持的数据类型: {data_type}")
        saver(file_path, data, titles)

    # ===== 内部实现解析方法 =====

    def _load_deck(self, file_path: Union[str, Path]) -> List[str]:
        from .deck_parser import parse_deck_text
        with open(file_path, 'r', encoding='utf-8') as f:
            return parse_deck_text(f.read())

    def _load_condition(self, file_path: Union[str, Path]) -> Tuple[List[CompositeCondition], List[str]]:
        from .condition_parser import parse_condition_text
        with open(file_path, 'r', encoding='utf-8') as f:
            return parse_condition_text(f.read())

    def _load_strategy(self, file_path: Union[str, Path]) -> List[Strategy]:
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        registry = self._build_strategy_function_registry()
        return [Strategy.from_dict(data, registry) for data in data_list]

    def _save_deck(self, file_path: Union[str, Path], data: List[str], titles: List[str] = None):
        from .deck_writer import write_deck
        write_deck(file_path, data)

    def _save_condition(self, file_path: Union[str, Path], data: Any, titles: List[str] = None):
        from .condition_writer import write_conditions
        write_conditions(file_path, data, titles)

    def _save_strategy(self, file_path: Union[str, Path], data: List[Strategy], titles: List[str] = None):
        serialized = [strategy.to_dict() for strategy in data]
        from utils.file_utils import write_to_file
        write_to_file(json.dumps(serialized, ensure_ascii=False, indent=2), file_path)

    def _build_strategy_function_registry(self) -> Dict[str, Callable]:
        """
        构建函数注册表，用于反序列化时还原策略函数
        """
        from core.engine.strategy_rules import (
            golden_manhu_condition_factory,
            golden_manhu_action_factory,
            golden_qianhu_condition_factory,
            golden_qianhu_action_factory,
            dark_draw_condition_factory,
            dark_draw_action_factory,
        )
        return {
            'golden_manhu_condition_factory': golden_manhu_condition_factory(),
            'golden_manhu_action_factory': golden_manhu_action_factory(2),
            'golden_qianhu_condition_factory': golden_qianhu_condition_factory(),
            'golden_qianhu_action_factory': golden_qianhu_action_factory(["博士", "苏"], 6),
            'dark_draw_condition_factory': dark_draw_condition_factory(["暗抽", "暗"], 2),
            'dark_draw_action_factory': dark_draw_action_factory(2),
        }
