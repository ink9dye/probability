# core/handlers/unified_handler.py

from .deck_handler import DeckHandler
from .condition_handler import ConditionHandler
from .ydk_handler import YDKHandler

# 注册所有 handler 类型
_handler_map = {
    "deck": DeckHandler(),
    "condition": ConditionHandler(),
    "ydk": YDKHandler(),
}

def get_handler(handler_type: str):
    if handler_type not in _handler_map:
        raise ValueError(f"不支持的处理器类型: {handler_type}")
    return _handler_map[handler_type]

def load_file(file_path: str, handler_type: str,is_path: bool = True):
    handler = get_handler(handler_type)
    return handler.load(file_path, is_path=is_path)

def save_file(file_path: str, handler_type: str, data, titles: list[str] = None):
    handler = get_handler(handler_type)
    return handler.save(file_path, data, titles)
