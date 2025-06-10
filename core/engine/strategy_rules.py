# core/engine/strategy_rules.py
from typing import List, Callable
import random

# ========= 抽卡逻辑 =========
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


# ========= 条件 & 动作工厂函数 =========
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


# ========= 模块导出 =========
__all__ = [
    "golden_manhu_condition_factory",
    "golden_manhu_action_factory",
    "golden_qianhu_condition_factory",
    "golden_qianhu_action_factory",
    "dark_draw_condition_factory",
    "dark_draw_action_factory",
    "draw_more"
]
