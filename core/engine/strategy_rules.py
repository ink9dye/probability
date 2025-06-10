# core/engine/strategy_rules.py
from typing import List, Callable, Optional
import random

from core.entity.strategy import Strategy, register_strategy


from .factories import (
    golden_manhu_condition_factory,
    golden_manhu_action_factory,
    golden_qianhu_condition_factory,
    golden_qianhu_action_factory,
    dark_draw_condition_factory,
    dark_draw_action_factory,
)

STRATEGY_FUNCTION_REGISTRY = {
    "golden_manhu_condition_factory": golden_manhu_condition_factory(),
    "golden_manhu_action_factory": golden_manhu_action_factory(),
    "golden_qianhu_condition_factory": golden_qianhu_condition_factory(),
    "golden_qianhu_action_factory": golden_qianhu_action_factory(["赌魂", "螺禅", "博士", "苏", "手坑"], 6),
    "dark_draw_condition_factory": dark_draw_condition_factory(["暗抽", "暗"], 2),
    "dark_draw_action_factory": dark_draw_action_factory(2),
}


# 工具函数：从 pool 中排除已有的 hand，随机抽 count 张
def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
    remaining = [c for c in pool if c not in exclude]
    return random.sample(remaining, min(len(remaining), count))


# 🔹 金满壶：可配置抽卡张数
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

def create_golden_manhu_strategy(name: str = "金满壶", draw_count: int = 2) -> Strategy:
    return Strategy(
        name=name,
        description=f"抽 {draw_count} 张非手坑卡",
        condition_func=golden_manhu_condition_factory(),
        action_func=golden_manhu_action_factory(draw_count),
        priority=100,
    )


# 🔹 金谦壶：可配置抽卡张数 & 可配置优先级字段列表
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

def create_golden_qianhu_strategy(
        name: str = "金谦壶",
        required_card: str = "金谦壶",
        draw_count: int = 6,
        priority_fields: List[str] = ["赌魂", "螺禅", "博士", "苏", "手坑"]
) -> Strategy:
    return Strategy(
        name=name,
        description=f"按 [{','.join(priority_fields)}] 优先级抽一张指定卡",
        condition_func=golden_qianhu_condition_factory(required_card),
        action_func=golden_qianhu_action_factory(priority_fields, draw_count),
        priority=90,
    )




# 🔹 自定义暗抽策略：当某些卡在手中时抽n张卡（可复用）
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

# 示例：暗抽策略
dark_draw_strategy = Strategy(
    name="暗抽",
    description="有至少1张'暗抽'和2张'暗'开头的卡时抽2张",
    condition_func=dark_draw_condition_factory(["暗抽", "暗"], required_count=2),
    action_func=dark_draw_action_factory(2),
    priority=70,
)
register_strategy("暗抽", dark_draw_strategy)

# 示例：自奏圣殿策略
zizou_strategy = Strategy(
    name="自奏圣殿",
    description="有1张'主音'和2张'自奏'时抽2张卡",
    condition_func=dark_draw_condition_factory(["主音", "自奏"], required_count=2),
    action_func=dark_draw_action_factory(2),
    priority=65,
)
register_strategy("自奏圣殿", zizou_strategy)
