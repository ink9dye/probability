# core/handlers/strategy_handler.py

import os
import json
from typing import List, Dict, Optional, Callable
from pathlib import Path

# 实体类和注册函数
from core.entity.strategy import Strategy, register_strategy, STRATEGY_REGISTRY
# 工具函数
from utils.file_utils import resolve_path
# 配置路径
from config.settings import STRATEGY_FILE

DEFAULT_STRATEGY_FILE = STRATEGY_FILE


def get_default_function_registry() -> Dict[str, Callable]:
    """
    获取默认的策略条件/动作函数注册表。
    这些函数用于反序列化策略中的 condition 和 action 字段。
    """
    from core.engine.strategy_rules import (
        golden_manhu_condition_factory,
        golden_manhu_action_factory,
        golden_qianhu_condition_factory,
        golden_qianhu_action_factory,
        dark_draw_condition_factory,
        dark_draw_action_factory
    )

    return {
        'golden_manhu_condition_factory': golden_manhu_condition_factory(),
        'golden_manhu_action_factory': golden_manhu_action_factory(),
        'golden_qianhu_condition_factory': golden_qianhu_condition_factory(),
        'golden_qianhu_action_factory': golden_qianhu_action_factory(["赌魂", "螺禅"]),
        'dark_draw_condition_factory': dark_draw_condition_factory(["暗抽", "暗"], required_count=2),
        'dark_draw_action_factory': dark_draw_action_factory(2)
    }


def load_strategies_from_file(file_path: str = DEFAULT_STRATEGY_FILE) -> List[Strategy]:
    """
    从 JSON 文件中加载所有策略，并自动注册到 STRATEGY_REGISTRY。
    """
    func_registry = get_default_function_registry()

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"找不到策略文件：{file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data_list = json.load(f)

    strategies = []
    for data in data_list:
        try:
            strategy = Strategy.from_dict(data, func_registry)
            strategies.append(strategy)
            register_strategy(strategy.name, strategy)
        except Exception as e:
            print(f"[ERROR] 加载策略失败：{e}")
    return strategies


def save_strategies_to_file(strategies: List[Strategy], file_path: str = DEFAULT_STRATEGY_FILE):
    """
    将策略列表保存到 JSON 文件。
    """
    data_list = [strategy.to_dict() for strategy in strategies]
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_list, f, ensure_ascii=False, indent=2)


def get_all_registered_strategies() -> List[Strategy]:
    """
    获取当前已注册的所有策略。
    """
    return list(STRATEGY_REGISTRY.values())


def add_new_strategy(strategy: Strategy, file_path: str = DEFAULT_STRATEGY_FILE):
    """
    添加新策略并保存到文件。
    """
    register_strategy(strategy.name, strategy)
    strategies = get_all_registered_strategies()
    save_strategies_to_file(strategies, file_path)


def remove_strategy(name: str, file_path: str = DEFAULT_STRATEGY_FILE):
    """
    删除指定名称的策略，并更新文件。
    """
    if name in STRATEGY_REGISTRY:
        del STRATEGY_REGISTRY[name]

    strategies = get_all_registered_strategies()
    save_strategies_to_file(strategies, file_path)


def update_strategy(strategy: Strategy, file_path: str = DEFAULT_STRATEGY_FILE):
    """
    更新已有策略，并保存到文件。
    """
    if strategy.name in STRATEGY_REGISTRY:
        register_strategy(strategy.name, strategy)
    strategies = get_all_registered_strategies()
    save_strategies_to_file(strategies, file_path)


def create_empty_strategy_template() -> Strategy:
    """
    创建一个空模板策略，用于 GUI 新建时使用。
    """
    return Strategy(
        name="新策略",
        description="描述",
        condition_func=lambda hand, pool: False,
        action_func=lambda hand, pool: hand,
        priority=0,
        tags=["自定义"]
    )
