"""
概率模拟引擎核心模块

提供完整的抽卡模拟流程：
1. 卡池构建
2. 策略应用
3. 条件匹配
4. 结果统计与输出
"""

import random,re
import logging
from typing import List, Tuple, Optional, Callable
from core.entity.card import Card
from core.entity.composite_condition import CompositeCondition
from services.local_db_service import LocalCardDB
from services.file_service import clean_card_name


# ================== 配置 logging ==================
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)  # 关闭所有 INFO 和 DEBUG 日志


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
            fields = data.get("field", [])
            name_to_fields[card_name] = [f.strip() for f in fields]
    return name_to_fields


# 在模块加载时构建字段缓存
NAME_TO_FIELDS = _build_name_to_fields()


def _convert_names_to_cards(names: List[str]) -> List[Card]:
    """
    将卡名列表转换为 Card 对象列表
    """
    return [
        Card(name=clean_card_name(n), fields=NAME_TO_FIELDS.get(clean_card_name(n), []))
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
    调用回调函数记录日志信息（保留接口以兼容UI）
    """
    draw_num, hand_names, matched_cond = snapshot
    if callback:
        line = f"第 {draw_num} 抽: {hand_names} ⇒ " + (
            f"满足条件 {conditions.index(matched_cond) + 1}" if matched_cond else "无匹配"
        )
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

def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
    """
    从卡池中抽取未被排除的卡牌
    """
    remaining = [c for c in pool if c not in exclude]
    return random.sample(remaining, min(len(remaining), count))


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
    """
    应用策略逻辑到当前手牌（扁平化版本，用于主流程）
    """
    result = hand_names.copy()

    def get_fields(cn: str):
        return NAME_TO_FIELDS.get(cn, [])

    # 金满壶策略
    if golden_manhu_enabled:
        if any("强欲而金满之壶" in get_fields(c) for c in result):
            new_cards = draw_more(pool, result, golden_manhu_draw_count)
            result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])

    # 金谦壶策略
    # 金谦壶策略
    if golden_qianhu_enabled and golden_qianhu_priority_fields:
        has_trigger = any("金满而谦虚之壶" in get_fields(c) for c in result)
        if has_trigger:
            new_cards = draw_more(pool, result, golden_qianhu_draw_count)

            chosen = None

            # 构建所有字段集合（支持子串、中英文逗号）
            current_all_fields = [
                field.strip()
                for name in result
                for f in NAME_TO_FIELDS.get(name, [])
                for field in re.split(r"[、,\s]+", f)
            ]

            # 逐级查找字段
            matched_index = -1
            for i, p in enumerate(golden_qianhu_priority_fields):
                if any(p in field for field in current_all_fields):
                    continue  # 当前字段已存在，继续往下找
                else:
                    # 找到第一个未匹配字段
                    matched_index = i
                    break

            # 即使所有字段都匹配，也继续执行补抽逻辑，但是会变成选第一张
            # 从 matched_index 开始查找补抽卡
            search_order = golden_qianhu_priority_fields[matched_index:]

            # 在补抽卡中查找第一个匹配字段
            for p in search_order:
                for c in new_cards:
                    card_fields = [
                        field.strip()
                        for f in NAME_TO_FIELDS.get(c, [])
                        for field in re.split(r"[、,\s]+", f)
                    ]
                    if any(p in field for field in card_fields):
                        chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
                        break
                if chosen:
                    break

            # 如果没找到任何字段匹配的卡，就选第一张
            if not chosen and new_cards:
                chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else new_cards[0]

            if chosen:
                result.append(chosen)
    # 类暗抽策略
    if dark_draw_enabled:
        trigger_cards = [c for c in result if dark_draw_trigger_card in get_fields(c)]
        found_match = False
        for matched_card in trigger_cards:
            if dark_draw_required_field in get_fields(matched_card):
                new_cards = draw_more(pool, result, 2)
                result.extend([c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards])
                found_match = True
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
            Card(name=clean_card_name(n), fields=NAME_TO_FIELDS.get(clean_card_name(n), []))
            for n in hand_names
        ]

        matched_index = _match_condition(card_objects, conditions)
        matched_indices.append(matched_index)

        # 快照记录
        if snapshot_interval > 0 and draw_num % snapshot_interval == 0:
            snapshot = _take_snapshot(draw_num, hand_names, matched_index, conditions)
            snapshots.append(snapshot)

    # 回调写入日志（保留接口）
    for snapshot in snapshots:
        _log_snapshot(snapshot, conditions, callback)

    # 总结
    probability = _calculate_probability(matched_indices, num_draws)
    summary_text = _generate_summary(matched_indices, titles, conditions)

    return probability, summary_text
