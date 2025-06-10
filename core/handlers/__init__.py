# core/handlers/__init__.py

from .deck_handler import DeckHandler
from .condition_handler import ConditionHandler
from .ydk_handler import YDKHandler
from .strategy_handler import load_strategies_from_file, save_strategies_to_file


class StrategyHandler:
    """
    封装 strategy 的加载与保存操作，使其适配统一接口。
    """
    def load(self, file_path: str, is_path: bool = True):
        if not is_path:
            raise ValueError("StrategyHandler 不支持从非路径数据加载")
        return load_strategies_from_file(file_path)

    def save(self, file_path: str, data, titles: list[str] = None):
        return save_strategies_to_file(data, file_path)


# 注册所有 handler 类型
_handler_map = {
    "deck": DeckHandler(),
    "condition": ConditionHandler(),
    "ydk": YDKHandler(),
    "strategy": StrategyHandler(),  # 新增策略处理器
}


def get_handler(handler_type: str):
    """
    获取指定类型的处理器实例。
    """
    if handler_type not in _handler_map:
        raise ValueError(f"不支持的处理器类型: {handler_type}")
    return _handler_map[handler_type]


def load_file(file_path: str, handler_type: str, is_path: bool = True):
    """
    统一入口：加载文件。
    """
    handler = get_handler(handler_type)
    return handler.load(file_path, is_path)


def save_file(file_path: str, handler_type: str, data, titles: list[str] = None):
    """
    统一入口：保存文件。
    """
    handler = get_handler(handler_type)
    return handler.save(file_path, data, titles)
