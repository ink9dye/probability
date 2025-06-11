# core/engine/probability_engine.py

import random
from typing import List, Tuple, Optional

from core.entity.composite_condition import CompositeCondition
from core.entity.card import Card
from services.local_db_service import LocalCardDB
from services.file_service import clean_card_name
from core.repositories.strategy_repository import get_builtin_strategies, apply_all_strategies, Strategy


def check_conditions(cards: List[Card], condition: CompositeCondition) -> bool:
    return condition.is_satisfied(cards)


def _build_card_map(card_pool: List[str]) -> dict:
    """
    构建卡名到字段的映射表
    """
    db = LocalCardDB()
    name_to_fields = {}
    for cid, data in db.id_attr_map.items():
        card_name = data.get("name")
        if card_name:
            name_to_fields[card_name] = data.get("field", [])
    return name_to_fields


def _create_card_objects(name_to_fields: dict) -> dict:
    """
    创建 Card 实例映射
    """
    card_map = {}
    for name, fields in name_to_fields.items():
        clean_name = clean_card_name(name)
        card_map[clean_name] = Card(name=clean_name, fields=fields)
    return card_map


def _apply_strategies(hand_names: List[str], card_pool: List[str], strategies: List[Strategy]) -> List[str]:
    """
    应用所有启用的策略
    """
    return apply_all_strategies(hand_names, card_pool, strategies)


def _match_condition(hand_cards: List[Card], conditions: List[CompositeCondition]) -> Optional[int]:
    """
    匹配第一个满足条件的规则
    """
    for i, cond in enumerate(conditions):
        if check_conditions(hand_cards, cond):
            return i
    return None


def simulate_draws(
        card_pool: List[str],
        conditions: List[CompositeCondition],
        titles: List[str],
        draw_size: int,
        num_draws: int,
        snapshot_interval: int,
        strategies: Optional[List[Strategy]] = None
) -> Tuple[List[Optional[int]], List[Tuple[int, List[str], Optional[CompositeCondition]]]]:
    """
    执行抽卡模拟并统计结果。
    """

    matched_indices: List[Optional[int]] = []
    snapshots = []

    # 初始化卡牌映射
    name_to_fields = _build_card_map()
    card_map = _create_card_objects(name_to_fields)

    # 开始模拟
    for draw_num in range(1, num_draws + 1):
        hand_names = random.sample(card_pool, draw_size)
        active_strategies = strategies if strategies is not None else get_builtin_strategies()

        # 策略应用
        hand_names = _apply_strategies(hand_names, card_pool, active_strategies)

        # 卡牌转为对象
        hand_cards = [card_map[name] for name in hand_names]

        # 条件匹配
        matched_index = _match_condition(hand_cards, conditions)
        matched_indices.append(matched_index)

        # 快照记录
        if draw_num % snapshot_interval == 0:
            snapshots.append((
                draw_num,
                hand_names,
                conditions[matched_index] if matched_index is not None else None
            ))

    return matched_indices, snapshots


def summarize_results(matched_indices: List[Optional[int]], titles: List[str], total_conditions: int,
                      conditions: List[CompositeCondition]):
    counts = [0] * total_conditions
    for idx in matched_indices:
        if idx is not None:
            counts[idx] += 1

    total_draws = len(matched_indices)
    total_hits = 0
    print("\n分组优先级命中统计：")

    cumulative = 0
    printed_titles = set()

    for i, count in enumerate(counts):
        title = titles[i]
        prob = count / total_draws
        total_hits += count
        print(f"{title}: {'，'.join(str(c) for c in conditions[i].get_sub_conditions())} 的概率为 {prob:.2%}")

        cumulative += count
        is_last_of_title = (i == len(titles) - 1) or (titles[i + 1] != title)
        if is_last_of_title:
            print(f"直到{title} 的累计概率为: {cumulative / total_draws:.2%}")
            printed_titles.add(title)
            cumulative = 0

    print(f"所有情况的总概率为: {total_hits / total_draws:.2%}")
