class CompositeCondition:
    def __init__(self, conditions: list):
        """
        表示多个条件的 AND 组合。

        :param conditions: 条件列表，所有条件必须同时满足
        """
        self.conditions = conditions

    def is_satisfied(self, cards: list) -> bool:
        """
        所有条件都必须满足才算整体满足。

        :param cards: 卡牌列表
        :return: 是否满足所有子条件
        """
        return all(cond.is_satisfied(cards) for cond in self.conditions)

    def get_sub_conditions(self) -> list:
        """返回所有子条件"""
        return self.conditions.copy()

    def __repr__(self):
        return " AND ".join(f"({cond})" for cond in self.conditions)
