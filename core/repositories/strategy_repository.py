# core/repositories/strategy_repository.py
from typing import List
from core.engine import strategy_rules


class Strategy:
    def __init__(
        self,
        name: str,
        description: str,
        condition_func,
        action_func,
        enabled: bool = True
    ):
        self.name = name
        self.description = description
        self.condition_func = condition_func
        self.action_func = action_func
        self.enabled = enabled

    def apply(self, hand: List[str], pool: List[str]) -> List[str]:
        if self.enabled and self.condition_func(hand, pool):
            return self.action_func(hand, pool)
        return hand


def apply_all_strategies(
    hand: List[str],
    pool: List[str],
    strategies: List[Strategy]
) -> List[str]:
    """
    执行启用状态的策略，不再按优先级排序。
    """
    for strategy in strategies:
        if strategy.enabled:
            hand = strategy.apply(hand, pool)
    return hand



def get_builtin_strategies() -> List[Strategy]:
    """
    内置策略定义（仅三种）。
    """
    return [
        Strategy(
            name="金满壶",
            description="手牌中包含'金满壶'则抽1或2张卡",
            condition_func=strategy_rules.golden_manhu_condition_factory("金满壶"),
            action_func=strategy_rules.golden_manhu_action_factory(2),
            enabled=True
        ),
        Strategy(
            name="金谦壶",
            description="手牌中包含'金谦壶'则按关键字抽取卡",
            condition_func=strategy_rules.golden_qianhu_condition_factory("金谦壶"),
            action_func=strategy_rules.golden_qianhu_action_factory(["手坑"], 6),
            enabled=True
        ),
        Strategy(
            name="类暗抽",
            description="有特定字段卡时抽二",
            condition_func=strategy_rules.dark_draw_condition_factory(["暗抽", "暗"], 2),
            action_func=strategy_rules.dark_draw_action_factory(2),
            enabled=True
        )
    ]
