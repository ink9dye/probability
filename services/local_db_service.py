# services/local_db_service.py
import csv
import os
from typing import List, Dict, Set
from config.settings import CSV_FILE, CSV_HEADERS

def refresh_database():
    """
    全局函数：刷新本地卡牌数据库缓存。
    可供外部（如菜单项、命令行工具）调用。
    """
    db = LocalCardDB()
    db.refresh()

class LocalCardDB:
    def __init__(self):
        self.existing_ids = set()
        self.id_name_map = {}
        self.id_field_map = {}
        self.load_existing_data()

    # ================== 数据加载与刷新 ==================
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
        """重新加载本地数据库"""
        self.load_existing_data()
        print("本地数据库已刷新")

    # ================== 卡片信息查询 ==================
    def get_card_name(self, cid: str) -> str:
        if cid not in self.existing_ids:
            self.refresh()
        return self.id_name_map.get(cid, f"未知卡牌({cid})")

    def get_all_cards(self) -> dict:
        return dict(self.id_name_map)

    # ================== 字段相关操作 ==================
    def has_field(self, cid: str, keyword: str) -> bool:
        return keyword in self.id_field_map.get(cid, [])

    def get_card_fields(self, cid: str) -> List[str]:
        return self.id_field_map.get(cid, [])

    def get_all_fields(self) -> Set[str]:
        """获取所有存在的字段标签"""
        all_fields = set()
        for fields in self.id_field_map.values():
            all_fields.update(fields)
        return all_fields

    def add_card_field(self, cid: str, field: str):
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if field not in current:
            current.append(field)
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])
            return True
        return False

    def remove_card_field(self, cid: str, field: str):
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if field in current:
            current.remove(field)
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])
            return True
        return False

    def update_card_field(self, cid: str, old_field: str, new_field: str):
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if old_field in current:
            idx = current.index(old_field)
            current[idx] = new_field
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])
            return True
        return False

    def update_cards_field(self, cids: List[str], new_field: str):
        """
        为指定的卡牌列表添加字段标签。
        :param cids: 卡牌 ID 列表
        :param new_field: 新字段名称
        """
        updated = []

        for cid in cids:
            if cid not in self.existing_ids:
                continue
            current_fields = self.id_field_map.get(cid, [])
            if new_field not in current_fields:
                current_fields.append(new_field)
                self.id_field_map[cid] = current_fields
                updated.append(cid)

        if updated:
            self._save_updated_fields(updated)

    # ================== 数据写入与保存 ==================
    def save_new_cards(self, new_data: list[Dict]):
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

        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = list(reader)

        merged = {item['id']: item for item in all_data}
        for item in filtered:
            merged[item['id']] = item

        sorted_data = sorted(merged.values(), key=lambda x: int(x['id']))

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"✅ 添加新卡 {len(filtered)} 条记录，并已按 ID 排序更新 CSV 文件")

    def _save_updated_fields(self, updated_cids: List[str]):
        if not updated_cids:
            return

        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = list(reader)

        data_map = {item['id']: item for item in all_data}

        for cid in updated_cids:
            if cid in data_map:
                fields = self.id_field_map[cid]
                data_map[cid]['field'] = '、'.join(fields)

        sorted_data = sorted(data_map.values(), key=lambda x: int(x['id']))

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"✅ 已更新 {len(updated_cids)} 张卡牌的字段信息")
