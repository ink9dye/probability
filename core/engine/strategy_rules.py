# # core/engine/strategy_rules.py
# from typing import List, Callable, Tuple, Dict, Optional
# import random
#
# # ========= 抽卡逻辑 =========
# def draw_more(pool: List[str], exclude: List[str], count: int) -> List[str]:
#     """
#     从牌池中抽取未在手牌中的卡。
#     :param pool: 牌池（所有可用卡）
#     :param exclude: 已有手牌
#     :param count: 抽取数量
#     :return: 新抽到的卡列表
#     """
#     remaining = [c for c in pool if c not in exclude]
#     return random.sample(remaining, min(len(remaining), count))
#
#
# # ========= 策略类型定义 =========
#
# StrategyRule = Tuple[Callable[[List[str], List[str]], bool],  # 条件函数
#                      Callable[[List[str], List[str]], List[str]]]  # 动作函数
#
# StrategyConfig = Dict[str, bool]  # 策略启用配置
#
#
# # ========= 策略工厂函数 =========
#
# def golden_manhu_condition_factory(required_card: str = "金满壶") -> Callable[[List[str], List[str]], bool]:
#     def condition(hand: List[str], pool: List[str]) -> bool:
#         return any(required_card in card for card in hand)
#     return condition
#
# def golden_manhu_action_factory(draw_count: int = 2) -> Callable[[List[str], List[str]], List[str]]:
#     def action(hand: List[str], pool: List[str]) -> List[str]:
#         new_cards = draw_more(pool, hand, draw_count)
#         new_cards = [c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards]
#         return hand + new_cards
#     return action
#
# def golden_qianhu_condition_factory(required_card: str = "金谦壶") -> Callable[[List[str], List[str]], bool]:
#     def condition(hand: List[str], pool: List[str]) -> bool:
#         return any(required_card in card for card in hand)
#     return condition
#
# def golden_qianhu_action_factory(priority_fields: List[str], draw_count: int = 6) -> Callable[[List[str], List[str]], List[str]]:
#     def action(hand: List[str], pool: List[str]) -> List[str]:
#         new_cards = draw_more(pool, hand, draw_count)
#         chosen = None
#         for p in priority_fields:
#             for c in new_cards:
#                 if p in c:
#                     chosen = c.replace("手坑", "手后坑") if "手坑" in c else c
#                     break
#             if chosen:
#                 break
#         if not chosen and new_cards:
#             chosen = new_cards[0].replace("手坑", "手后坑") if "手坑" in new_cards[0] else "后置" + new_cards[0]
#         if chosen:
#             hand.append(chosen)
#         return hand
#     return action
#
# def dark_draw_condition_factory(required_cards: List[str], required_count: int) -> Callable[[List[str], List[str]], bool]:
#     def condition(hand: List[str], pool: List[str]) -> bool:
#         return sum(1 for c in hand if any(req in c for req in required_cards)) >= required_count
#     return condition
#
# def dark_draw_action_factory(draw_count: int) -> Callable[[List[str], List[str]], List[str]]:
#     def action(hand: List[str], pool: List[str]) -> List[str]:
#         new_cards = draw_more(pool, hand, draw_count)
#         new_cards = [c.replace("手坑", "手后坑") if "手坑" in c else c for c in new_cards]
#         return hand + new_cards
#     return action
#
#
# # ========= 策略仓库 =========
#
# STRATEGY_RULES = {
#     "golden_manhu": (
#         golden_manhu_condition_factory("金满壶"),
#         golden_manhu_action_factory(2),
#         "手牌中包含'金满壶'则抽1或2张卡"
#     ),
#     "golden_qianhu": (
#         golden_qianhu_condition_factory("金谦壶"),
#         golden_qianhu_action_factory(["手坑"], 6),
#         "手牌中包含'金谦壶'则按关键字抽取卡"
#     ),
#     "dark_draw": (
#         dark_draw_condition_factory(["暗属性"], 1),
#         dark_draw_action_factory(2),
#         "有特定字段卡时抽二"
#     )
# }
#
# def get_builtin_strategy_names() -> List[str]:
#     """
#     获取所有内置策略名称
#     """
#     return list(STRATEGY_RULES.keys())
#
# def get_strategy_description(name: str) -> Optional[str]:
#     """
#     获取某个策略的描述信息
#     """
#     return STRATEGY_RULES.get(name, (None, None, None))[2]
#
#
# # ========= 策略应用逻辑 =========
#
# def apply_strategy_by_name(name: str, hand: List[str], pool: List[str]) -> List[str]:
#     """
#     根据策略名称应用策略
#     """
#     cond_func, act_func, _ = STRATEGY_RULES.get(name, (None, None, None))
#     if cond_func is None:
#         return hand
#     if cond_func(hand, pool):
#         return act_func(hand, pool)
#     return hand
#
# def apply_all_strategies(hand: List[str], pool: List[str], enabled: List[str]) -> List[str]:
#     """
#     应用所有启用的策略
#     """
#     result = hand.copy()
#     for name in enabled:
#         result = apply_strategy_by_name(name, result, pool)
#     return result
#
#
# # ========= 示例导出 =========
#
# __all__ = [
#     "apply_all_strategies",
#     "get_builtin_strategy_names",
#     "get_strategy_description",
#     "draw_more",
# ]
