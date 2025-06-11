"""
概率模拟引擎核心模块

提供完整的抽卡模拟流程：
1. 卡池构建
2. 策略应用
3. 条件匹配
4. 结果统计与输出
"""

import random
import logging
import os
from typing import List, Tuple, Optional, Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.entity.card import Card
from core.entity.composite_condition import CompositeCondition
from services.local_db_service import LocalCardDB
from services.file_service import clean_card_name


# ================== 配置 logging ==================
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)


# ================== 辅助函数区 ==================

def _build_name_to_fields() -> dict:
    """
    从数据库中加载卡牌名称 → 字段的映射表
    """
    db = LocalCardDB()
    name_to_fields = {}
    for cid, data in db.id_attr_map.items():
        card_name = data.get("name")
        if card_name:
            name_to_fields[card_name] = data.get("field", [])
    return name_to_fields


def _convert_names_to_cards(names: List[str], field_map: dict) -> List[Card]:
    """
    将卡名列表转换为 Card 对象列表
    """
    return [
        Card(name=clean_card_name(n), fields=field_map.get(clean_card_name(n), []))
        for n in names
    ]


def _match_condition(card_objects: List[Card], conditions: List[CompositeCondition]) -> Optional[int]:
    """
    判断当前手牌是否满足任意一个条件组，并返回其索引
    """
    for i, cond in enumerate(conditions):
        if cond.is_satisfied(card_objects):
            return i
    return None


def _take_snapshot(draw_num: int, hand_names: List[str], matched_index: Optional[int],
                   conditions: List[CompositeCondition]):
    """
    构建单次抽卡快照数据
    """
    matched_cond = conditions[matched_index] if matched_index is not None else None
    return (draw_num, hand_names, matched_cond)


def _log_snapshot(snapshot, conditions, callback: Optional[Callable[[str], None]]):
    """
    调用回调函数记录日志信息
    """
    draw_num, hand_names, matched_cond = snapshot

    if matched_cond is not None:
        try:
            idx = conditions.index(matched_cond) + 1
            line = f"第 {draw_num} 抽: {hand_names} ⇒ 满足条件 {idx}"
        except ValueError:
            line = f"第 {draw_num} 抽: {hand_names} ⇒ 满足条件（未知条件）"
    else:
        line = f"第 {draw_num} 抽: {hand_names} ⇒ 无匹配"

    logger.info(line)
    if callback:
        callback(line)


def _calculate_probability(matched_indices: List[Optional[int]], total_draws: int) -> float:
    """
    统计满足条件的总次数并计算概率
    """
    total_matches = sum(1 for idx in matched_indices if idx is not None)
    return total_matches / total_draws


def _generate_summary(matched_indices: List[Optional[int]], titles: List[str],
                      conditions: List[CompositeCondition]) -> str:
    """
    根据匹配结果生成总结报告文本
    """
    counts = [0] * len(titles)
    for idx in matched_indices:
        if idx is not None:
            counts[idx] += 1

    total_draws = len(matched_indices)
    lines = ["分组优先级命中统计："]

    cumulative = 0
    printed_titles = set()

    for i, count in enumerate(counts):
        title = titles[i]
        prob = count / total_draws
        summary = "，".join(str(c) for c in conditions[i].get_sub_conditions())
        lines.append(f"{title}: {summary} 的概率为 {prob:.2%}")

        cumulative += count
        is_last = (i == len(titles) - 1) or (titles[i + 1] != title if i < len(titles) - 1 else True)
        if is_last:
            lines.append(f"直到{title} 的累计概率为: {cumulative / total_draws:.2%}")
            cumulative = 0

    lines.append(f"所有情况的总概率为: {sum(counts) / total_draws:.2%}")
    return "\n".join(lines)


# ================== 策略实现区 ==================

def apply_strategies(hand_names: List[str], pool: List[str], strategy_config=None) -> List[str]:
    """
    根据配置对象应用所有启用的策略
    """
    result = hand_names.copy()
    if strategy_config is None:
        return result

    # 构建字段映射表
    db = LocalCardDB()
    name_to_fields = {}
    for cid, data in db.id_attr_map.items():
        card_name = data.get("name")
        if card_name:
            name_to_fields[card_name] = data.get("field", [])
    def get_fields(card_name: str):
        return [f.strip() for f in name_to_fields.get(card_name, [])]

    # 金满壶策略
    if strategy_config.golden_manhu_enabled:
        if any("强欲而金满之壶" in get_fields(c) for c in result):
            new_cards = draw_more(pool, result, strategy_config.golden_manhu_draw_count)
            result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])

    # 金谦壶策略
    if strategy_config.golden_qianhu_enabled:
        if any("金满而谦虚之壶" in get_fields(c) for c in result):
            new_cards = draw_more(pool, result, strategy_config.golden_qianhu_draw_count)
            chosen = None
            for p in strategy_config.golden_qianhu_priority_fields:
                for c in new_cards:
                    if p in get_fields(c):
                        chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                        break
                if chosen:
                    break
            if not chosen and new_cards:
                chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else "后置" + new_cards[0]
            if chosen:
                result.append(chosen)

    # 类暗抽策略
    if strategy_config.dark_draw_enabled:
        has_trigger = any(strategy_config.dark_draw_trigger_card in get_fields(c) for c in result)
        if has_trigger:
            matched_card = next((c for c in result if any(strategy_config.dark_draw_trigger_card in get_fields(c))), None)
            if matched_card and any(strategy_config.dark_draw_required_field in get_fields(matched_card)):
                new_cards = draw_more(pool, result, 2)
                result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])

    return result


def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
    """
    从卡池中抽取未被排除的卡牌
    """
    remaining = [c for c in pool if c not in exclude]
    return random.sample(remaining, min(len(remaining), count))


# ================== 并行化任务函数 ==================

def _worker_task(
    start_idx: int,
    end_idx: int,
    card_pool: List[str],
    conditions: List[CompositeCondition],
    draw_size: int,
    name_to_fields: dict,
    strategy_config=None,
    seed: int = None
) -> List[Optional[int]]:
    """
    每个线程执行的抽卡模拟任务
    """

    if seed is not None:
        random.seed(seed)

    matched_indices = []

    for draw_num in range(start_idx, end_idx + 1):
        hand_names = random.sample(card_pool, draw_size)
        hand_names = apply_strategies(hand_names, card_pool, strategy_config)

        card_objects = [
            Card(name=clean_card_name(n), fields=name_to_fields.get(clean_card_name(n), []))
            for n in hand_names
        ]

        matched_index = None
        for i, cond in enumerate(conditions):
            if cond.is_satisfied(card_objects):
                matched_index = i
                break

        matched_indices.append(matched_index)

    logger.info("线程完成 #%d - #%d 的抽卡模拟，共 %d 条结果",
                 start_idx, end_idx, len(matched_indices))
    return matched_indices

def apply_strategies_flat(
    hand_names: List[str],
    pool: List[str],
    golden_manhu_enabled: bool = False,
    golden_manhu_draw_count: int = 2,
    golden_qianhu_enabled: bool = False,
    golden_qianhu_priority_fields: List[str] = ("手坑",),
    golden_qianhu_draw_count: int = 6,
    dark_draw_enabled: bool = False,
    dark_draw_trigger_card: str = "暗之诱惑",
    dark_draw_required_field: str = "暗属性"
) -> List[str]:
    result = hand_names.copy()
    db = LocalCardDB()
    name_to_fields = {}
    for cid, data in db.id_attr_map.items():
        name = data.get("name")
        if name:
            name_to_fields[name] = data.get("field", [])

    def get_fields(cn: str):
        return [f.strip() for f in name_to_fields.get(cn, [])]

    # logger.info(f"【策略启用情况】金满壶: {golden_manhu_enabled}, 金谦壶: {golden_qianhu_enabled}, 类暗抽: {dark_draw_enabled}")

    if golden_manhu_enabled:
        if any("强欲而金满之壶" in get_fields(c) for c in result):
            new_cards = draw_more(pool, result, golden_manhu_draw_count)
            result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])
            logger.info(f"【金满壶】触发成功，补抽: {new_cards}")

    if golden_qianhu_enabled:
        if any("金满而谦虚之壶" in get_fields(c) for c in result):
            new_cards = draw_more(pool, result, golden_qianhu_draw_count)
            chosen = None
            for p in golden_qianhu_priority_fields:
                for c in new_cards:
                    if p in get_fields(c):
                        chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                        break
                if chosen:
                    break
            if not chosen and new_cards:
                chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else new_cards[0]
            if chosen:
                result.append(chosen)
                logger.info(f"【金谦壶】触发成功，选择: {chosen}")

    if dark_draw_enabled:
        logger.info("【类暗抽】开始,条件为: 触发卡名: %s, 所需字段: %s", dark_draw_trigger_card, dark_draw_required_field)
        trigger_cards = [c for c in result if dark_draw_trigger_card in get_fields(c)]
        for matched_card in trigger_cards:
            fields = get_fields(matched_card)
            if dark_draw_required_field in fields:
                new_cards = draw_more(pool, result, 2)
                result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])
                logger.info(f"【类暗抽】触发成功，补抽: {new_cards}")
                break

    return result






# ================== 主流程函数 ==================

def simulate_draws(
    card_pool: List[str],
    conditions: List[CompositeCondition],
    titles: List[str],
    draw_size: int,
    num_draws: int,
    snapshot_interval: int,
    # 金满壶参数
    golden_manhu_enabled: bool = False,
    golden_manhu_draw_count: int = 2,
    # 金谦壶参数
    golden_qianhu_enabled: bool = False,
    golden_qianhu_priority_fields: List[str] = ("手坑",),
    golden_qianhu_draw_count: int = 6,
    # 类暗抽参数
    dark_draw_enabled: bool = False,
    dark_draw_trigger_card: str = "暗之诱惑",
    dark_draw_required_field: str = "暗属性",
    # 日志回调
    callback: Optional[Callable[[str], None]] = None
) -> Tuple[float, str]:
    """
    单线程版本的模拟抽卡主流程函数，适用于桌面打包应用。
    """

    logger.info("开始模拟抽卡任务，总次数：%d", num_draws)
    logger.info("开始模拟抽卡任务，总次数：%d", num_draws)

    # 新增参数调试日志
    logger.debug("传入参数详情：")
    logger.debug("  卡池大小: %d 张", len(card_pool))
    logger.debug("  每次抽卡数量: %d 张", draw_size)
    logger.debug("  条件组数量: %d 组", len(conditions))
    logger.debug("  快照间隔: 每 %d 抽记录一次", snapshot_interval)
    logger.debug("  金满壶启用: %s", golden_manhu_enabled)
    logger.debug("  金谦壶启用: %s", golden_qianhu_enabled)
    logger.debug("  类暗抽启用: %s", dark_draw_enabled)

    # 构建字段映射表
    name_to_fields = _build_name_to_fields()
    logger.debug("已加载 %d 张卡牌字段信息", len(name_to_fields))

    matched_indices = []
    snapshots = []

    for draw_num in range(1, num_draws + 1):
        hand_names = random.sample(card_pool, draw_size)

        hand_names = apply_strategies_flat(
            hand_names,
            card_pool,
            golden_manhu_enabled=golden_manhu_enabled,
            golden_manhu_draw_count=golden_manhu_draw_count,
            golden_qianhu_enabled=golden_qianhu_enabled,
            golden_qianhu_priority_fields=golden_qianhu_priority_fields,
            golden_qianhu_draw_count=golden_qianhu_draw_count,
            dark_draw_enabled=dark_draw_enabled,
            dark_draw_trigger_card=dark_draw_trigger_card,
            dark_draw_required_field=dark_draw_required_field
        )

        card_objects = [
            Card(name=clean_card_name(n), fields=name_to_fields.get(clean_card_name(n), []))
            for n in hand_names
        ]

        matched_index = _match_condition(card_objects, conditions)
        matched_indices.append(matched_index)

        # 快照记录
        if snapshot_interval > 0 and draw_num % snapshot_interval == 0:
            snapshot = _take_snapshot(draw_num, hand_names, matched_index, conditions)
            snapshots.append(snapshot)

    # 输出快照日志
    for snapshot in snapshots:
        _log_snapshot(snapshot, conditions, callback)

    # 总结
    probability = _calculate_probability(matched_indices, num_draws)
    summary_text = _generate_summary(matched_indices, titles, conditions)

    logger.info("模拟完成，成功率 %.2f%%", probability * 100)

    return probability, summary_text
