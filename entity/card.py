class Card:
    def __init__(self, name: str, count: int = 1, id_: str = None, fields: list = None):
        """
        表示一张卡牌的基本信息。

        :param name: 卡牌名称（必填）
        :param count: 卡牌数量，默认为 1
        :param id_: 卡牌编号（可选）
        :param fields: 卡牌字段标签列表（如 ["手坑", "补"]），可用于筛选分类
        """
        self.name = name
        self.count = count
        self.id = id_
        if isinstance(fields, str):
            self.fields = [f.strip() for f in fields.split("、")]
        else:
            self.fields = fields or []

    def has_field(self, keyword: str) -> bool:
        return any(keyword in field for field in self.fields)

    def __repr__(self):
        return f"Card(name={self.name}, count={self.count})"