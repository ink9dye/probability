# entity/condition.py

class Condition:
    def __init__(self, card_name: str, operator: str, value: int, group_title: str | None = None):
        """
        初始化一个条件对象，用于判断卡牌或字段的数量是否满足某种逻辑条件。

        :param card_name: 条件对应的卡名或关键词（如 "手坑"、"融合" 等）
        :param operator: 逻辑操作符（支持中文和符号形式，如 "大于等于", ">="）
        :param value: 目标数量值，用于比较
        :param group_title: 所属标题组（从 # 行中继承，可为 None，表示该条件归属的分类标题）
        """
        self.card_name = card_name.strip()  # 去除前后空格，标准化卡名或关键词
        self.operator = operator.strip()  # 标准化操作符字符串
        self.value = value  # 比较的目标数值
        self.group_title = group_title.lstrip('#').strip() if group_title else None  # 新增字段，用于分组显示或筛选

    def is_satisfied(self, count: int) -> bool:
        """
        判断给定数量是否满足当前条件。

        :param count: 当前统计到的卡牌或字段数量
        :return: 如果满足条件返回 True，否则返回 False
        """
        if self.operator == "大于" or self.operator == ">":
            return count > self.value
        elif self.operator == "大于等于" or self.operator == ">=":
            return count >= self.value
        elif self.operator == "等于" or self.operator == "=":
            return count == self.value
        elif self.operator == "小于" or self.operator == "<":
            return count < self.value
        elif self.operator == "小于等于" or self.operator == "<=":
            return count <= self.value
        return False  # 默认不满足任何条件时返回 False

    def __repr__(self):
        """
        返回当前条件对象的简洁字符串表示。
        :return: 字符串格式为 "card_name operator value"
        """
        return f"{self.card_name} {self.operator} {self.value}"

