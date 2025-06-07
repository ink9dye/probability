# entity/condition.py
from typing import List, Tuple

class Condition:
    def __init__(self, expression: str, operator: str, value: int, group_title: str | None = None):
        """
        初始化一个条件对象，支持 AND 组合条件与比较操作符。

        :param expression: 条件表达式，支持 AND 组合，用 & 分隔，如 "坏兽 & 炎"
        :param operator: 比较操作符，如 ">=", "==", "<" 等
        :param value: 目标数值
        :param group_title: 所属标题组（可选）
        """
        self.keywords = [k.strip() for k in expression.split("&")]
        self.operator = operator.strip()
        self.value = value
        self.group_title = group_title.lstrip('#').strip() if group_title else None

    def match_card(self, card) -> bool:
        """
        判断一张卡是否满足本条件中的所有关键词要求。
        可以是卡名包含任意关键字，或者字段中包含所有关键字。
        """
        # 至少有一个关键字出现在卡名中
        name_match = any(kw in card.name for kw in self.keywords)

        # 所有关键字必须在字段中出现（或部分在卡名中）
        field_match = all(card.has_field(kw) or kw in card.name for kw in self.keywords)

        return name_match or field_match

    def is_satisfied(self, cards: List['Card']) -> bool:
        """
        判断给定卡牌列表中，满足本条件的数量是否符合操作符要求。
        """
        matched = [c for c in cards if self.match_card(c)]
        count = len(matched)

        if self.operator in [">", "大于"]:
            return count > self.value
        elif self.operator in [">=", "大于等于"]:
            return count >= self.value
        elif self.operator in ["==", "=", "等于"]:
            return count == self.value
        elif self.operator in ["<", "小于"]:
            return count < self.value
        elif self.operator in ["<=", "小于等于"]:
            return count <= self.value
        return False

    def __repr__(self):
        return f"({' & '.join(self.keywords)}) {self.operator} {self.value}"
