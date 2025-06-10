# core/entity/strategy.py
from typing import List, Callable, Dict, Optional
import uuid

# 所有策略都注册在这里
STRATEGY_REGISTRY = {}

def register_strategy(name: str, strategy: 'Strategy'):
    """
    将策略注册到全局策略库中
    """
    STRATEGY_REGISTRY[name] = strategy

def get_strategy(name: str) -> Optional['Strategy']:
    """
    获取已注册的策略
    """
    return STRATEGY_REGISTRY.get(name)

def get_all_strategies() -> List['Strategy']:
    """
    获取所有已注册的策略
    """
    return list(STRATEGY_REGISTRY.values())

def apply_all_strategies(
    hand: List[str],
    pool: List[str],
    strategies: List['Strategy'] = None
) -> List[str]:
    if strategies is None:
        strategies = get_all_strategies()

    # 数值越小越优先，升序排列
    active_strategies = sorted(
        (s for s in strategies if s.enabled),
        key=lambda s: s.priority
    )

    for strategy in active_strategies:
        hand = strategy.apply(hand, pool)

    return hand

class Strategy:
    def __init__(
        self,
        name: str,
        description: str,
        condition_func: Callable[[List[str], List[str]], bool],
        action_func: Callable[[List[str], List[str]], List[str]],
        priority: int = 0,
        strategy_id: str = None,
        enabled: bool = True
    ):
        self.strategy_id = strategy_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.action_func = action_func
        self.priority = priority if priority is not None else len(get_all_strategies())
        self.enabled = enabled

    def apply(self, hand: List[str], pool: List[str]) -> List[str]:
        if self.condition_func(hand, pool):
            return self.action_func(hand, pool)
        return hand

    def to_dict(self) -> dict:
        return {
            "strategy_id": self.strategy_id,
            "name": self.name,
            "description": self.description,
            "condition": self._serialize_function(self.condition_func),
            "action": self._serialize_function(self.action_func),
            "priority": self.priority,
            "enabled": self.enabled
        }

    @staticmethod
    def _serialize_function(func: Callable) -> str:
        if hasattr(func, "__name__"):
            return func.__name__
        return str(func)

    @classmethod
    def from_dict(cls, data: dict, registry: Dict[str, Callable]) -> "Strategy":
        condition = registry.get(data["condition"])
        action = registry.get(data["action"])
        if not condition or not action:
            raise ValueError(f"无法找到对应的策略函数：{data}")
        return cls(
            strategy_id=data["strategy_id"],
            name=data["name"],
            description=data["description"],
            condition_func=condition,
            action_func=action,
            priority=data["priority"],
            enabled=data.get("enabled", True)
        )
