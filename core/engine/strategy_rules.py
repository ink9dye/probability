# engine/strategy_rules.py
from typing import List
import random

def apply_all_strategies(hand: List[str], pool: List[str]) -> List[str]:
    hand = handle_pot(hand, pool)
    hand = zizou(hand, pool)
    hand = anchou(hand, pool)
    return hand

def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
    remaining = [c for c in pool if c not in exclude]
    return random.sample(remaining, min(len(remaining), count))

def handle_pot(hand: List[str], pool: List[str]) -> List[str]:
    if any("金满壶" in card for card in hand):
        new_cards = draw_more(pool, hand, 2)
        new_cards = [c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards]
        hand.extend(new_cards)
    elif any("金谦壶" in card for card in hand):
        priority = ["赌魂", "螺禅", "博士", "苏", "手坑"]
        new_cards = draw_more(pool, hand, 6)
        chosen = None
        for p in priority:
            for c in new_cards:
                if p in c:
                    chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                    break
            if chosen:
                break
        if not chosen and new_cards:
            chosen = new_cards[0]
            if "手坑" in chosen:
                chosen = chosen.replace("手坑", "手后坑")
            else:
                chosen = "后置" + chosen
        if chosen:
            hand.append(chosen)
    elif any("强贪" in card for card in hand):
        reduced = [c for c in pool if c not in hand][10:]
        if reduced:
            hand.append("后置" + reduced[0])
    return hand

def zizou(hand: List[str], pool: List[str]) -> List[str]:
    if sum(1 for c in hand if "主音" in c) >= 1 and sum(1 for c in hand if "自奏" in c) >= 2:
        hand.extend(draw_more(pool, hand, 2))
    return hand

def anchou(hand: List[str], pool: List[str]) -> List[str]:
    if sum(1 for c in hand if "暗抽" in c) >= 1 and sum(1 for c in hand if "暗" in c) >= 2:
        hand.extend(draw_more(pool, hand, 2))
    return hand
