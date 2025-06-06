# probability_engine.py
import random
from collections import Counter, defaultdict
from typing import List, Tuple
from engine.strategy_rules import apply_all_strategies
from entity.condition import Condition

def check_conditions(drawn: List[str], conditions: List[Condition]) -> bool:
    counter = Counter(drawn)
    for cond in conditions:
        matched_count = sum(v for name, v in counter.items() if cond.card_name in name)
        if not cond.is_satisfied(matched_count):
            return False
    return True

def simulate_draws(card_pool: List[str],
                   conditions: List[List[Condition]],
                   titles: List[str],
                   draw_size: int = 5,
                   num_draws: int = 100000,
                   snapshot_interval: int = 20000
                   ) -> Tuple[List[int | None], List[Tuple[int, List[str], List[Condition] | None]]]:
    matched_indices: List[int | None] = []
    snapshots = []

    for draw_num in range(1, num_draws + 1):
        hand = random.sample(card_pool, draw_size)
        hand = apply_all_strategies(hand, card_pool)

        matched_index = None
        for i, conds in enumerate(conditions):
            if check_conditions(hand, conds):
                matched_index = i
                break
        matched_indices.append(matched_index)

        if draw_num % snapshot_interval == 0:
            snapshots.append((draw_num, hand, conditions[matched_index] if matched_index is not None else None))

    return matched_indices, snapshots

def summarize_results(matched_indices: List[int | None], titles: List[str], total_conditions: int, conditions: List[List[Condition]]):
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
        print(f"{title}: {'，'.join(str(c) for c in conditions[i])} 的概率为 {prob:.2%}")

        cumulative += count
        is_last_of_title = (i == len(titles) - 1) or (titles[i + 1] != title)
        if is_last_of_title:
            print(f"直到{title} 的累计概率为: {cumulative / total_draws:.2%}")
            printed_titles.add(title)
            cumulative = 0

    print(f"所有情况的总概率为: {total_hits / total_draws:.2%}")
