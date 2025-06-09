# services/simulation_service.py
from engine.probability_engine import simulate_draws, summarize_results
from engine.strategy_rules import apply_all_strategies
from typing import List, Tuple
from entity.condition import Condition
from entity.composite_condition import CompositeCondition
import io
import sys

def run_simulation(card_pool, conditions, draw_size, num_draws, snapshot_interval, titles):
    """
    主模拟接口（service 层）：
    - 运行模拟抽卡；
    - 返回总成功概率 和 分组命中率描述字符串。

    返回:
    - float: 总命中率
    - str: 分组命中率详情（带换行字符串）
    """
    matched_indices, snapshots = simulate_draws(
        card_pool=card_pool,
        conditions=conditions,
        titles=titles,
        draw_size=draw_size,
        num_draws=num_draws,
        snapshot_interval=snapshot_interval
    )

    # 计算详细输出
    buf = io.StringIO()
    sys_stdout = sys.stdout
    sys.stdout = buf
    try:
        summarize_results(matched_indices, titles, len(conditions), conditions)
    finally:
        sys.stdout = sys_stdout  # 确保恢复 stdout

    summary_text = buf.getvalue()
    total_matches = sum(1 for idx in matched_indices if idx is not None)
    probability = total_matches / num_draws

    return probability, summary_text


def summarize_results(
    matched_indices: List[int | None],
    titles: List[str],
    total_conditions: int,
    conditions: List[CompositeCondition]
) -> str:
    counts = [0] * total_conditions
    for idx in matched_indices:
        if idx is not None:
            counts[idx] += 1

    total_draws = len(matched_indices)
    total_hits = 0
    cumulative = 0
    printed_titles = set()
    lines = ["\n分组优先级命中统计："]

    for i, count in enumerate(counts):
        title = titles[i]
        prob = count / total_draws
        total_hits += count
        summary = "，".join(str(c) for c in conditions[i].get_sub_conditions())
        lines.append(f"情况{i+1} {title}: {summary} 的概率为 {prob:.2%}")

        cumulative += count
        is_last = (i == len(titles) - 1) or (titles[i + 1] != title)
        if is_last:
            lines.append(f"直到{title} 的累计概率为: {cumulative / total_draws:.2%}")
            cumulative = 0

    lines.append(f"所有情况的总概率为: {total_hits / total_draws:.2%}")
    return "\n".join(lines)

def report_snapshots(snapshots: List[Tuple[int, List[str], List[Condition] | None]], conditions: List[List[Condition]]):
    for draw_num, cards, matched_condition in snapshots:
        if matched_condition:
            idx = conditions.index(matched_condition) + 1
            print(f"第 {draw_num} 抽: {cards} ⇒ 满足条件 {idx}")
        else:
            print(f"第 {draw_num} 抽: {cards} ⇒ 无匹配")
