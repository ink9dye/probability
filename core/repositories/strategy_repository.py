# core/repositories/strategy_repository.py

import os
import json
from typing import Dict, List, Optional
from config.settings import STRATEGY_FILE
from core.entity.strategy import Strategy, register_strategy
from core.engine.strategy_rules import create_golden_manhu_strategy, create_golden_qianhu_strategy, dark_draw_strategy,dark_draw_condition_factory,dark_draw_action_factory
from core.engine.strategy_rules import STRATEGY_FUNCTION_REGISTRY
class LocalStrategyDB:
    """
    本地策略数据库封装类：封装策略名 → 策略对象 的映射与操作
    - 支持缓存
    - 支持启用/禁用策略
    - 自动保存变更回 JSON 文件
    """

    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}  # name → Strategy
        self._load_from_file()

    def _load_from_file(self):
        """从 JSON 文件加载策略"""
        self._strategies.clear()

        if not os.path.exists(STRATEGY_FILE):
            print("⚠️ 策略文件不存在")
            self._ensure_default_strategies()
            return

        try:
            with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    print("⚠️ 策略文件为空")
                    self._ensure_default_strategies()
                    return

            data = json.loads(content)

            for name, strategy_data in data.items():
                try:
                    strategy = Strategy.from_dict(strategy_data, STRATEGY_FUNCTION_REGISTRY)
                    self._strategies[name] = strategy
                    register_strategy(name, strategy)
                except Exception as e:
                    print(f"[ERROR] 加载策略失败：{name} - {e}")

        except json.JSONDecodeError as e:
            print(f"[ERROR] 策略文件 JSON 解码失败: {e}")
            self._ensure_default_strategies()

    def refresh(self):
        """刷新缓存"""
        self._load_from_file()
        print("✅ 策略数据库已刷新")

    def get_all_strategies(self) -> Dict[str, Strategy]:
        """获取所有策略"""
        return dict(self._strategies)

    def get_strategy(self, name: str) -> Optional[Strategy]:
        """根据名称获取策略"""
        if name not in self._strategies:
            self.refresh()
        return self._strategies.get(name)

    def add_strategy(self, strategy: Strategy) -> bool:
        """添加新策略"""
        if strategy.name in self._strategies:
            print(f"🚫 策略 {strategy.name} 已存在")
            return False
        self._strategies[strategy.name] = strategy
        register_strategy(strategy.name, strategy)
        self._save_to_file([strategy.name])
        return True

    def update_strategy(self, strategy: Strategy) -> bool:
        """更新已有策略"""
        if strategy.name not in self._strategies:
            return False
        self._strategies[strategy.name] = strategy
        register_strategy(strategy.name, strategy)
        self._save_to_file([strategy.name])
        return True

    def delete_strategy(self, name: str) -> bool:
        """删除指定策略"""
        if name not in self._strategies:
            return False
        del self._strategies[name]
        self._save_to_file([])
        return True

    def apply_strategies(self, hand: List[str], pool: List[str]) -> List[str]:
        """应用所有启用的策略到当前手牌"""
        from core.entity.strategy import apply_all_strategies
        strategies = [s for s in self._strategies.values() if s.enabled]
        return apply_all_strategies(hand, pool, strategies)

    def reorder_strategies(self, ordered_names: List[str]):
        """按指定顺序调整策略优先级"""
        for idx, name in enumerate(ordered_names):
            if name in self._strategies:
                self._strategies[name].priority = idx
                self._save_to_file([name])

    def enable_strategy(self, name: str, enabled: bool = True):
        """启用或禁用策略"""
        strategy = self.get_strategy(name)
        if strategy:
            strategy.enabled = enabled
            return self.update_strategy(strategy)
        return False

    def disable_strategy(self, name: str):
        return self.enable_strategy(name, False)

    def _save_to_file(self, updated_names: List[str]):
        all_data = {}
        if os.path.exists(STRATEGY_FILE):
            try:
                with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        all_data = json.loads(content)
            except Exception as e:
                print(f"⚠️ 无法读取旧策略数据，将覆盖写入新数据: {e}")
                all_data = {}

        for name in updated_names:
            all_data[name] = self._strategies[name].to_dict()

        current_names = set(self._strategies.keys())
        for name in list(all_data.keys()):
            if name not in current_names:
                del all_data[name]

        with open(STRATEGY_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"已写入 {len(updated_names)} 个策略")

    def _ensure_default_strategies(self):
        """
        确保至少有金满壶、金谦壶、暗抽这三个策略。
        如果策略文件不存在或内容为空，则添加它们，默认启用状态为 False，并使用自增优先级。
        """

        default_strategy_names = ["金满壶", "金谦壶", "暗抽"]

        current_names = set(self._strategies.keys())

        added = []

        # 1. 创建金满壶策略
        if "金满壶" not in current_names:
            strategy = create_golden_manhu_strategy(name="金满壶", draw_count=2)
            strategy.enabled = False
            self.add_strategy(strategy)
            added.append("金满壶")

        # 2. 创建金谦壶策略
        if "金谦壶" not in current_names:
            strategy = create_golden_qianhu_strategy(
                name="金谦壶",
                required_card="金谦壶",
                draw_count=6,
                priority_fields=["赌魂", "螺禅", "博士", "苏", "手坑"]
            )
            strategy.enabled = False
            self.add_strategy(strategy)
            added.append("金谦壶")

        # 3. 创建暗抽策略
        if "暗抽" not in current_names:
            strategy = Strategy(
                name="暗抽",
                description="",
                condition_func=dark_draw_condition_factory(["暗抽", "暗"], required_count=2),
                action_func=dark_draw_action_factory(2),
                enabled=False,
            )
            self.add_strategy(strategy)
            added.append("暗抽")

        if added:
            print(f"✅ 已添加默认策略（已禁用）：{', '.join(added)}")
            self._save_to_file(updated_names=added)  # 🔥 主动写入磁盘


# 单例访问点
__strategy_db_instance = None


def get_local_strategy_db() -> LocalStrategyDB:
    global __strategy_db_instance
    if __strategy_db_instance is None:
        __strategy_db_instance = LocalStrategyDB()
    return __strategy_db_instance
