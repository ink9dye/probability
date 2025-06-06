# services/simulation_service.py
from engine.probability_engine import simulate_draws, summarize_results
from engine.strategy_rules import apply_all_strategies
from typing import List, Tuple
from entity.condition import Condition

def run_simulation(card_pool: List[str], conditions: List[List[Condition]],
                   draw_size: int = 5, num_draws: int = 100000,
                   snapshot_interval: int = 20000,
                   titles: List[str] = None) -> None:
    """
    运行模拟主流程，并输出报告。
    """
    matched_indices, snapshots = simulate_draws(
        card_pool=card_pool,
        conditions=conditions,
        titles=titles,
        draw_size=draw_size,
        num_draws=num_draws,
        snapshot_interval=snapshot_interval,
    )

    report_snapshots(snapshots, conditions)
    summarize_results(matched_indices, titles or [], len(conditions), conditions)

def report_snapshots(snapshots: List[Tuple[int, List[str], List[Condition] | None]], conditions: List[List[Condition]]):
    for draw_num, cards, matched_condition in snapshots:
        if matched_condition:
            idx = conditions.index(matched_condition) + 1
            print(f"第 {draw_num} 抽: {cards} ⇒ 满足条件 {idx}")
        else:
            print(f"第 {draw_num} 抽: {cards} ⇒ 无匹配")
