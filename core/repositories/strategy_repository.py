# core/repositories/strategy_repository.py
import json
import os
from typing import Dict
from core.entity.strategy import Strategy
from core.engine.strategy_rules import STRATEGY_FUNCTION_REGISTRY

STRATEGY_FILE_PATH = "data/strategies.json"

class LocalStrategyDB:
    def __init__(self):
        self._strategies: Dict[str, Strategy] = {}
        self._load_from_file()

    def _load_from_file(self):
        if not os.path.exists(STRATEGY_FILE_PATH):
            print("⚠️ 策略文件不存在")
            self._ensure_default_strategies()
            return

        with open(STRATEGY_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if not data:
                    print("⚠️ 策略文件为空")
                    self._ensure_default_strategies()
                    return
                for item in data:
                    try:
                        strategy = Strategy.from_dict(item, STRATEGY_FUNCTION_REGISTRY)
                        self._strategies[strategy.name] = strategy
                    except Exception as e:
                        print(f"[ERROR] 加载策略失败：{item.get('name')} - {e}")
            except json.JSONDecodeError as e:
                print(f"[ERROR] 策略文件 JSON 解码失败: {e}")
                self._ensure_default_strategies()

    def _save_to_file(self, updated_names=None):
        try:
            with open(STRATEGY_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump([s.to_dict() for s in self._strategies.values()], f, ensure_ascii=False, indent=2)
                if updated_names:
                    print(f"已写入 {len(updated_names)} 个策略")
        except Exception as e:
            print(f"[ERROR] 策略保存失败: {e}")

    def add_strategy(self, strategy: Strategy):
        self._strategies[strategy.name] = strategy
        self._save_to_file(updated_names=[strategy.name])

    def remove_strategy(self, name: str):
        if name in self._strategies:
            del self._strategies[name]
            self._save_to_file(updated_names=[name])

    def get_all_strategies(self):
        return list(self._strategies.values())

    def _ensure_default_strategies(self):
        """
        确保至少有金满壶、金谦壶、暗抽这三个策略。
        如果策略文件不存在或内容为空，则添加它们，默认启用状态为 False。
        """
        default_names = ["金满壶", "金谦壶", "暗抽"]
        current_names = set(self._strategies.keys())
        added = []

        if "金满壶" not in current_names:
            s = Strategy(
                name="金满壶",
                description="抽 2 张非手坑卡",
                condition_func=STRATEGY_FUNCTION_REGISTRY["golden_manhu_condition"],
                action_func=STRATEGY_FUNCTION_REGISTRY["golden_manhu_action"],
                enabled=False,
                priority=100,
            )
            self.add_strategy(s)
            added.append("金满壶")

        if "金谦壶" not in current_names:
            s = Strategy(
                name="金谦壶",
                description="按优先级抽指定卡",
                condition_func=STRATEGY_FUNCTION_REGISTRY["golden_qianhu_condition"],
                action_func=STRATEGY_FUNCTION_REGISTRY["golden_qianhu_action"],
                enabled=False,
                priority=90,
            )
            self.add_strategy(s)
            added.append("金谦壶")

        if "暗抽" not in current_names:
            s = Strategy(
                name="暗抽",
                description="当满足条件时抽 2 张",
                condition_func=STRATEGY_FUNCTION_REGISTRY["dark_draw_condition"],
                action_func=STRATEGY_FUNCTION_REGISTRY["dark_draw_action"],
                enabled=False,
                priority=80,
            )
            self.add_strategy(s)
            added.append("暗抽")

        if added:
            print(f"✅ 已添加默认策略（已禁用）：{', '.join(added)}")
            self._save_to_file(updated_names=added)

def get_local_strategy_db():
    global __strategy_db_instance
    if '__strategy_db_instance' not in globals():
        __strategy_db_instance = LocalStrategyDB()
    return __strategy_db_instance
