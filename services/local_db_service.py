# services/local_db_service.py
import csv
import os
from collections import defaultdict
from config.settings import CSV_FILE, CSV_HEADERS


class LocalCardDB:
    def __init__(self):
        self.existing_ids = set()
        self.id_name_map = {}
        self.id_field_map = {}
        self.load_existing_data()

    def load_existing_data(self):
        self.existing_ids.clear()
        self.id_name_map.clear()
        self.id_field_map.clear()

        if not os.path.exists(CSV_FILE):
            return

        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("id")
                name = row.get("name")
                fields = row.get("field", "").split("、")
                if cid:
                    self.existing_ids.add(cid)
                    self.id_name_map[cid] = name
                    self.id_field_map[cid] = fields

    def refresh(self):
        self.load_existing_data()
        print("🔄 本地数据库已刷新")

    def get_card_name(self, cid: str) -> str:
        if cid not in self.existing_ids:
            self.refresh()
        return self.id_name_map.get(cid, f"未知卡牌({cid})")

    def has_field(self, cid: str, keyword: str) -> bool:
        return keyword in self.id_field_map.get(cid, [])

    def get_all_keywords(self) -> set[str]:
        keywords = set()
        for fields in self.id_field_map.values():
            keywords.update(fields)
        return keywords

    def get_all_cards(self) -> dict[str, str]:
        return dict(self.id_name_map)

    def save_new_cards(self, new_data: list[dict]):
        filtered = []
        for item in new_data:
            cid = item.get("id")
            if cid and cid not in self.existing_ids:
                filtered.append(item)
                self.existing_ids.add(cid)
                self.id_name_map[cid] = item.get("name")
                self.id_field_map[cid] = item.get("field", "").split("、")

        if not filtered:
            return

        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writerows(filtered)

        print(f"✅ 添加新卡 {len(filtered)} 条记录")
