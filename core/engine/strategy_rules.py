# core/engine/strategy_rules.py

from typing import List, Callable
import random
from core.entity.strategy import Strategy, register_strategy


def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
    """
    从牌池中抽取未在手牌中的卡。
    :param pool: 牌池（所有可用卡）
    :param exclude: 已有手牌
    :param count: 抽取数量
    :return: 新抽到的卡列表
    """
    remaining = [c for c in pool if c not in exclude]
    return random.sample(remaining, min(len(remaining), count))


# ========== 条件 & 动作工厂函数 ==========

def golden_manhu_condition_factory(required_card: str = "金满壶") -> Callable[[List[str], List[str]], bool]:
    def condition(hand: List[str], pool: List[str]) -> bool:
        return any(required_card in card for card in hand)
    return condition


def golden_manhu_action_factory(draw_count: int = 2) -> Callable[[List[str], List[str]], List[str]]:
    def action(hand: List[str], pool: List[str]) -> List[str]:
        new_cards = draw_more(pool, hand, draw_count)
        new_cards = [c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards]
        return hand + new_cards
    return action


def golden_qianhu_condition_factory(required_card: str = "金谦壶") -> Callable[[List[str], List[str]], bool]:
    def condition(hand: List[str], pool: List[str]) -> bool:
        return any(required_card in card for card in hand)
    return condition


def golden_qianhu_action_factory(priority_fields: List[str], draw_count: int = 6) -> Callable[[List[str], List[str]], List[str]]:
    def action(hand: List[str], pool: List[str]) -> List[str]:
        new_cards = draw_more(pool, hand, draw_count)
        chosen = None
        for p in priority_fields:
            for c in new_cards:
                if p in c:
                    chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                    break
            if chosen:
                break
        if not chosen and new_cards:
            chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else "后置" + new_cards[0]
        if chosen:
            hand.append(chosen)
        return hand
    return action


def dark_draw_condition_factory(required_cards: List[str], required_count: int) -> Callable[[List[str], List[str]], bool]:
    def condition(hand: List[str], pool: List[str]) -> bool:
        return sum(1 for c in hand if any(req in c for req in required_cards)) >= required_count
    return condition


def dark_draw_action_factory(draw_count: int) -> Callable[[List[str], List[str]], List[str]]:
    def action(hand: List[str], pool: List[str]) -> List[str]:
        new_cards = draw_more(pool, hand, draw_count)
        new_cards = [c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards]
        return hand + new_cards
    return action


# ========== 命名包装函数（用于策略注册）==========

def golden_manhu_condition(hand, pool):
    return golden_manhu_condition_factory()(hand, pool)


def golden_manhu_action(hand, pool):
    return golden_manhu_action_factory(2)(hand, pool)


def golden_qianhu_condition(hand, pool):
    return golden_qianhu_condition_factory()(hand, pool)


def golden_qianhu_action(hand, pool):
    return golden_qianhu_action_factory(["赌魂", "螺禅", "博士", "苏", "手坑"], 6)(hand, pool)


def dark_draw_condition(hand, pool):
    return dark_draw_condition_factory(["暗抽", "暗"], 2)(hand, pool)


def dark_draw_action(hand, pool):
    return dark_draw_action_factory(2)(hand, pool)


# ========== 策略构造函数（工厂函数）==========

def create_golden_manhu_strategy(name: str = "金满壶", draw_count: int = 2) -> Strategy:
    return Strategy(
        name=name,
        description="",  # ✅ 描述留空
        condition_func=golden_manhu_condition,
        action_func=golden_manhu_action,
        priority=None,  # ✅ 自动分配优先级
    )


def create_golden_qianhu_strategy(
    name: str = "金谦壶",
    required_card: str = "金谦壶",
    draw_count: int = 6,
    priority_fields: List[str] = ["赌魂", "螺禅", "博士", "苏", "手坑"]
) -> Strategy:
    return Strategy(
        name=name,
        description="",  # ✅ 描述留空
        condition_func=golden_qianhu_condition,
        action_func=golden_qianhu_action,
        priority=None,  # ✅ 自动分配优先级
    )


def create_dark_draw_strategy(
    name: str = "暗抽",
    required_cards: List[str] = ["暗抽", "暗"],
    required_count: int = 2,
    draw_count: int = 2
) -> Strategy:
    return Strategy(
        name=name,
        description="",  # ✅ 描述留空
        condition_func=dark_draw_condition,
        action_func=dark_draw_action,
        priority=None,  # ✅ 自动分配优先级
    )


# ========== 函数注册表（用于序列化/反序列化）==========
STRATEGY_FUNCTION_REGISTRY = {
    "golden_manhu_condition": golden_manhu_condition,
    "golden_manhu_action": golden_manhu_action,
    "golden_qianhu_condition": golden_qianhu_condition,
    "golden_qianhu_action": golden_qianhu_action,
    "dark_draw_condition": dark_draw_condition,
    "dark_draw_action": dark_draw_action,
}


# ========== 示例策略注册（可选）==========
register_strategy("暗抽", Strategy(
    name="暗抽",
    description="",  # ✅ 描述留空
    condition_func=dark_draw_condition,
    action_func=dark_draw_action,
    priority=None,  # ✅ 自动分配优先级
))

register_strategy("自奏圣殿", Strategy(
    name="自奏圣殿",
    description="",  # ✅ 描述留空
    condition_func=dark_draw_condition_factory(["主音", "自奏"], 2),
    action_func=dark_draw_action_factory(2),
    priority=None,  # ✅ 自动分配优先级
))


# ========== 模块导出声明（避免导入错误）==========
__all__ = [
    # 策略创建函数
    "create_golden_manhu_strategy",
    "create_golden_qianhu_strategy",
    "create_dark_draw_strategy",

    # 包装函数
    "golden_manhu_condition",
    "golden_manhu_action",
    "golden_qianhu_condition",
    "golden_qianhu_action",
    "dark_draw_condition",
    "dark_draw_action",

    # 注册表
    "STRATEGY_FUNCTION_REGISTRY",
]
