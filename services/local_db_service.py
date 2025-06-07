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
        self.field_to_names = defaultdict(set)  # 新增：字段 → 卡名集合
        self.load_existing_data()

    def load_existing_data(self):
        self.existing_ids.clear()
        self.id_name_map.clear()
        self.id_field_map.clear()
        self.field_to_names.clear()  # 清空旧字段映射

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

                # 更新字段 → 卡名映射
                for field in fields:
                    self.field_to_names[field].add(name)

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
        return set(self.field_to_names.keys())

    def get_all_cards(self) -> dict[str, str]:
        return dict(self.id_name_map)

    def get_cards_by_field(self, keyword: str) -> set[str]:
        """
        获取具有指定字段的所有卡牌名称集合
        :param keyword: 字段关键词，如 "炎"
        :return: 卡牌名称集合
        """
        return self.field_to_names.get(keyword, set())

    def save_new_cards(self, new_data: list[dict]):
        filtered = []
        for item in new_data:
            cid = item.get("id")
            if cid and cid not in self.existing_ids:
                filtered.append(item)
                self.existing_ids.add(cid)
                self.id_name_map[cid] = item.get("name")
                fields = item.get("field", "").split("、")
                self.id_field_map[cid] = fields

                # 同步更新 field_to_names
                for field in fields:
                    self.field_to_names[field].add(item["name"])

        if not filtered:
            return

        # 读取现有数据 + 合并新数据 + 排序
        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = list(reader)

        merged = {item['id']: item for item in all_data}
        for item in filtered:
            merged[item['id']] = item

        sorted_data = sorted(merged.values(), key=lambda x: int(x['id']))

        # 覆盖写入整个 CSV 文件
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"添加新卡 {len(filtered)} 条记录，并已按 ID 排序更新 CSV 文件")
