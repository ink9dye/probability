from typing import List
class Card:
    def __init__(self, card_id: str, name: str, field: List[str]):
        self.id = card_id
        self.name = name
        self.field = field  # 字段列表，如 ["动", "补", "手坑"]
