# core/repositories/strategy_repository.py

import os
import json
from typing import Dict, List, Optional
from config.settings import STRATEGY_FILE
from core.entity.strategy import Strategy, register_strategy
from core.repositories.strategy_repository import LocalStrategyDB
#
# class LocalStrategyDB:
#     """
#     本地策略数据库封装类：封装策略名 → 策略对象 的映射与操作
#     - 支持缓存
#     - 支持启用/禁用策略
#     - 自动保存变更回 JSON 文件
#     """
#
#     def __init__(self):
#         self._strategies: Dict[str, Strategy] = {}  # name → Strategy
#         self._load_from_file()
#
#     def _load_from_file(self):
#         """从 JSON 文件加载策略"""
#         self._strategies.clear()
#         if not os.path.exists(STRATEGY_FILE):
#             return
#
#         with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
#             data = json.load(f)
#
#         for name, strategy_data in data.items():
#             try:
#                 strategy = Strategy.from_dict(strategy_data)
#                 self._strategies[name] = strategy
#                 register_strategy(name, strategy)
#             except Exception as e:
#                 print(f"[ERROR] 加载策略失败：{name} - {e}")
#
#     def refresh(self):
#         """刷新缓存"""
#         self._load_from_file()
#         print("✅ 策略数据库已刷新")
#
#     def get_all_strategies(self) -> Dict[str, Strategy]:
#         """获取所有策略"""
#         return dict(self._strategies)
#
#     def get_strategy(self, name: str) -> Optional[Strategy]:
#         """根据名称获取策略"""
#         if name not in self._strategies:
#             self.refresh()
#         return self._strategies.get(name)
#
#     def add_strategy(self, strategy: Strategy) -> bool:
#         """添加新策略"""
#         if strategy.name in self._strategies:
#             print(f"🚫 策略 {strategy.name} 已存在")
#             return False
#         self._strategies[strategy.name] = strategy
#         register_strategy(strategy.name, strategy)
#         self._save_to_file([strategy.name])
#         return True
#
#     def update_strategy(self, strategy: Strategy) -> bool:
#         """更新已有策略"""
#         if strategy.name not in self._strategies:
#             return False
#         self._strategies[strategy.name] = strategy
#         register_strategy(strategy.name, strategy)
#         self._save_to_file([strategy.name])
#         return True
#
#     def delete_strategy(self, name: str) -> bool:
#         """删除指定策略"""
#         if name not in self._strategies:
#             return False
#         del self._strategies[name]
#         self._save_to_file([])
#         return True
#
#     def apply_strategies(self, hand: List[str], pool: List[str]) -> List[str]:
#         """应用所有启用的策略到当前手牌"""
#         from core.entity.strategy import apply_all_strategies
#         strategies = [s for s in self._strategies.values() if s.enabled]
#         return apply_all_strategies(hand, pool, strategies)
#
#     def reorder_strategies(self, ordered_names: List[str]):
#         """按指定顺序调整策略优先级"""
#         for idx, name in enumerate(ordered_names):
#             if name in self._strategies:
#                 self._strategies[name].priority = idx
#                 self._save_to_file([name])
#
#     def enable_strategy(self, name: str, enabled: bool = True):
#         """启用或禁用策略"""
#         strategy = self.get_strategy(name)
#         if strategy:
#             strategy.enabled = enabled
#             return self.update_strategy(strategy)
#         return False
#
#     def disable_strategy(self, name: str):
#         return self.enable_strategy(name, False)
#
#     def _save_to_file(self, updated_names: List[str]):
#         """将策略写入磁盘"""
#         all_data = {}
#         if os.path.exists(STRATEGY_FILE):
#             with open(STRATEGY_FILE, 'r', encoding='utf-8') as f:
#                 all_data = json.load(f)
#
#         for name in updated_names:
#             all_data[name] = self._strategies[name].to_dict()
#
#         current_names = set(self._strategies.keys())
#         for name in list(all_data.keys()):
#             if name not in current_names:
#                 del all_data[name]
#
#         with open(STRATEGY_FILE, 'w', encoding='utf-8') as f:
#             json.dump(all_data, f, ensure_ascii=False, indent=2)
#
#         print(f"✅ 已写入 {len(updated_names)} 个策略")
#
#
# 单例访问点
__strategy_db_instance = None


def get_local_strategy_db() -> LocalStrategyDB:
    global __strategy_db_instance
    if __strategy_db_instance is None:
        __strategy_db_instance = LocalStrategyDB()
    return __strategy_db_instance
