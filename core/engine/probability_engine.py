# core/engine/probability_engine.py

import random
from typing import List, Tuple, Optional  # ✅ 添加 Optional 导入

from core.entity.composite_condition import CompositeCondition
from core.entity.card import Card
from services.local_db_service import LocalCardDB
from services.parser_service import clean_card_name
from core.entity.strategy import apply_all_strategies


def check_conditions(cards: List[Card], condition: CompositeCondition) -> bool:
    return condition.is_satisfied(cards)


def simulate_draws(
        card_pool: List[str],
        conditions: List[CompositeCondition],
        titles: List[str],
        draw_size: int,
        num_draws: int,
        snapshot_interval: int,
        strategies: Optional[List['Strategy']] = None  # ✅ 使用 Optional 表示可选参数
) -> Tuple[List[int | None], List[Tuple[int, List[str], CompositeCondition | None]]]:
    matched_indices: List[int | None] = []
    snapshots = []

    db = LocalCardDB()
    name_to_fields = {v: db.id_field_map[k] for k, v in db.id_name_map.items()}
    card_map = {}
    for name, fields in name_to_fields.items():
        clean_name = clean_card_name(name)
        card_map[clean_name] = Card(name=clean_name, fields=fields)

    for draw_num in range(1, num_draws + 1):
        hand_names = random.sample(card_pool, draw_size)

        # ✅ 如果传入了自定义策略，则使用它们；否则使用全局注册的策略
        if strategies is not None:
            for strategy in sorted(strategies, key=lambda s: s.priority, reverse=True):
                hand_names = strategy.apply(hand_names, card_pool)
        else:
            hand_names = apply_all_strategies(hand_names, card_pool)

        hand_cards = [card_map[name] for name in hand_names]

        matched_index = None
        for i, cond in enumerate(conditions):
            if check_conditions(hand_cards, cond):
                matched_index = i
                break

        matched_indices.append(matched_index)

        if draw_num % snapshot_interval == 0:
            snapshots.append((draw_num, hand_names, conditions[matched_index] if matched_index is not None else None))

    return matched_indices, snapshots


def summarize_results(matched_indices: List[int | None], titles: List[str], total_conditions: int, conditions: List[CompositeCondition]):
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
