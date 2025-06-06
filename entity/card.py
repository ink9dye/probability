class Card:
    def __init__(self, name: str, count: int = 1, id_: str = None, fields: list = None):
        """
        表示一张卡牌的基本信息。

        :param name: 卡牌名称（必填）
        :param count: 卡牌数量，默认为 1
        :param id_: 卡牌编号（可选）
        :param fields: 卡牌字段标签列表（如 ["手坑", "补"]），可用于筛选分类
        """
        self.name = name  # 卡牌名称
        self.count = count  # 卡牌数量
        self.id = id_  # 可选编号
        self.fields = fields or []  # 字段标签列表，若为空则初始化为空列表

    def has_field(self, keyword: str) -> bool:
        """
        判断卡牌是否具有指定的字段标签。

        :param keyword: 要查找的字段标签
        :return: 如果包含该字段返回 True，否则返回 False
        """
        return keyword in self.fields

    def __repr__(self):
        """
        返回该卡牌对象的字符串表示，便于调试打印输出。

        :return: 格式化字符串，显示卡牌名称和数量
        """
        return f"Card(name={self.name}, count={self.count})"
