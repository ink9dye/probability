# services/simulation_service.py

from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable, Union

from core.engine.strategy_rules import draw_more
from core.entity.composite_condition import CompositeCondition
from core.engine.probability_engine import simulate_draws as base_simulate_draws


@dataclass
class StrategyConfig:
    """策略配置类：运行时使用"""
    golden_manhu_enabled: bool = True
    golden_manhu_draw_count: int = 2

    golden_qianhu_enabled: bool = True
    golden_qianhu_priority_fields: List[str] = ("手坑",)
    golden_qianhu_draw_count: int = 6

    dark_draw_enabled: bool = True
    dark_draw_fields: List[str] = ("暗抽", "暗")
    dark_draw_required_count: int = 2


def simulate_with_options(
    card_pool: List[str],
    conditions: List[CompositeCondition],
    titles: List[str],
    draw_size: int,
    num_draws: int,
    snapshot_interval: int,
    strategy_config: StrategyConfig = None,
    callback: Optional[Callable[[str], None]] = None
) -> Tuple[float, str]:
    config = strategy_config or StrategyConfig()

    def apply_strategies(hand: List[str], pool: List[str]) -> List[str]:
        result = hand.copy()

        # 金满壶策略
        if config.golden_manhu_enabled and any("金满壶" in c for c in result):
            new_cards = draw_more(pool, result, config.golden_manhu_draw_count)
            result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])

        # 金谦壶策略
        if config.golden_qianhu_enabled and any("金谦壶" in c for c in result):
            new_cards = draw_more(pool, result, config.golden_qianhu_draw_count)
            chosen = None
            for p in config.golden_qianhu_priority_fields:
                for c in new_cards:
                    if p in c:
                        chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                        break
                if chosen:
                    break
            if not chosen and new_cards:
                chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else "后置" + new_cards[0]
            if chosen:
                result.append(chosen)

        # 类暗抽策略
        if config.dark_draw_enabled:
            matched_count = sum(1 for c in result if any(req in c for req in config.dark_draw_fields))
            if matched_count >= config.dark_draw_required_count:
                new_cards = draw_more(pool, result, 2)
                result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])

        return result

    # 动态注入策略函数（仅本次生效）
    from core.repositories.strategy_repository import apply_all_strategies
    original_func = apply_all_strategies
    try:
        from types import FunctionType
        import functools
        import sys

        def dynamic_apply_all_strategies(hand, pool, _):
            return apply_strategies(hand, pool)

        dynamic_apply_all_strategies.__doc__ = apply_strategies.__doc__
        dynamic_apply_all_strategies = functools.update_wrapper(dynamic_apply_all_strategies, apply_strategies)

        module = sys.modules['core.repositories.strategy_repository']
        module.apply_all_strategies = dynamic_apply_all_strategies

        # 执行模拟
        matched_indices, snapshots = base_simulate_draws(
            card_pool=card_pool,
            conditions=conditions,
            titles=titles,
            draw_size=draw_size,
            num_draws=num_draws,
            snapshot_interval=snapshot_interval,
            strategies=[]  # 禁用默认策略
        )

    finally:
        # 恢复原始策略函数
        import sys
        module = sys.modules['core.repositories.strategy_repository']
        module.apply_all_strategies = original_func

    # 回调输出
    if callback:
        for draw_num, hand_names, matched_cond in snapshots:
            if matched_cond is not None:
                try:
                    idx = conditions.index(matched_cond) + 1
                    line = f"第 {draw_num} 抽: {hand_names} ⇒ 满足条件 {idx}"
                except ValueError:
                    line = f"第 {draw_num} 抽: {hand_names} ⇒ 满足条件（未知条件）"
            else:
                line = f"第 {draw_num} 抽: {hand_names} ⇒ 无匹配"
            callback(line)

    # 结果统计
    total_matches = sum(1 for idx in matched_indices if idx is not None)
    probability = total_matches / num_draws
    summary_text = _summarize_results(matched_indices, titles, len(conditions), conditions)

    return probability, summary_text


def _summarize_results(
    matched_indices: List[Optional[int]],
    titles: List[str],
    total_conditions: int,
    conditions: List[CompositeCondition]
) -> str:
    counts = [0] * total_conditions
    for idx in matched_indices:
        if idx is not None:
            counts[idx] += 1

    total_draws = len(matched_indices)
    lines = ["\n分组优先级命中统计："]

    cumulative = 0
    printed_titles = set()

    for i, count in enumerate(counts):
        title = titles[i]
        prob = count / total_draws
        summary = "，".join(str(c) for c in conditions[i].get_sub_conditions())
        lines.append(f"{title}: {summary} 的概率为 {prob:.2%}")

        cumulative += count
        is_last = (i == len(titles) - 1) or (titles[i + 1] != title)
        if is_last:
            lines.append(f"直到{title} 的累计概率为: {cumulative / total_draws:.2%}")
            cumulative = 0

    lines.append(f"所有情况的总概率为: {sum(counts) / total_draws:.2%}")
    return "\n".join(lines)
