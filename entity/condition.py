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
        # 将表达式按 & 分割，并去除每个关键词两侧空白字符
        self.keywords = [k.strip() for k in expression.split("&")]
        # 去除操作符前后空格，确保准确匹配
        self.operator = operator.strip()
        # 存储目标数量值
        self.value = value
        # 处理组名：去掉开头的 # 和两端空格；若未提供则设为 None
        self.group_title = group_title.lstrip('#').strip() if group_title else None

    def match_card(self, card) -> bool:
        """
        判断一张卡牌是否满足本条件中的关键词要求。

        :param card: 卡牌对象
        :return: 是否匹配成功
        """
        # 如果卡牌有字段信息，则使用字段判断所有关键词是否存在
        if card.fields:
            return all(card.has_field(kw) for kw in self.keywords)
        else:
            # 否则退而求其次，检查关键词是否出现在卡牌名称中
            return all(kw in card.name for kw in self.keywords)

    def is_satisfied(self, cards: List['Card']) -> bool:
        """
        判断给定卡牌列表中，满足本条件的数量是否符合操作符要求。

        :param cards: 一组卡牌对象
        :return: 条件是否满足
        """
        # 筛选出所有满足当前条件的卡牌
        matched = [c for c in cards if self.match_card(c)]
        count = len(matched)

        # 根据操作符判断是否满足条件（支持中英文写法）
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
        return False  # 若操作符不识别，默认返回 False

    def __repr__(self):
        """
        返回该条件的字符串表示，便于调试输出
        """
        return f"({' & '.join(self.keywords)}) {self.operator} {self.value}"
