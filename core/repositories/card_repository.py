# repositories/card_repository.py

import csv
import os
from typing import List, Dict, Set, Optional, Union
from config.settings import CSV_FILE, CSV_HEADERS  # 外部配置，CSV 路径与字段名

# 全局函数：供外部调用刷新本地卡牌数据库缓存
def refresh_database():
    """
    全局函数：刷新本地卡牌数据库缓存。
    可供外部（如菜单项、命令行工具）调用。
    """
    db = LocalCardDB()
    db.refresh()


class LocalCardDB:
    """
    本地卡牌数据库封装类：封装卡牌 ID → 各种属性 的映射与操作
    - 支持缓存
    - 支持任意字段增删改查
    - 自动保存变更回 CSV 文件
    """

    def __init__(self):
        self.existing_ids = set()           # 卡牌 ID 集合
        self.id_attr_map = {}               # ID → 属性字典（包含 name, field, type 等）
        self.load_existing_data()           # 初始化加载数据

    def load_existing_data(self):
        """
        从 CSV 文件加载数据到缓存结构中。
        会清空旧数据。
        """
        self.existing_ids.clear()
        self.id_attr_map.clear()

        if not os.path.exists(CSV_FILE):
            return  # 文件不存在时，跳过加载

        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("id")
                if not cid:
                    continue
                # 将 "field" 字段拆分为列表存储
                if "field" in row:
                    row["field"] = row["field"].split("、")
                else:
                    row["field"] = []
                self.existing_ids.add(cid)
                self.id_attr_map[cid] = dict(row)  # 存储完整属性字典

    def refresh(self):
        """
        重新加载 CSV 文件数据，刷新缓存。
        """
        self.load_existing_data()
        print("本地数据库已刷新")

    def add_card(self, cid: str, name: str, fields: Optional[List[str]] = None) -> bool:
        if cid in self.existing_ids:
            print(f"🚫 卡牌 {cid} 已存在，跳过添加")
            return False

        self.existing_ids.add(cid)
        self.id_attr_map[cid] = {
            "id": cid,
            "name": name,
            "field": fields or []
        }

        self._save_updated_attributes([cid])
        return True

    def save_new_cards(self, cards: List[Dict]):
        """
        批量保存新获取的卡牌数据。
        :param cards: 卡牌字典列表，每个元素包含 id、name、field 等字段
        """
        for card in cards:
            cid = card.get("id")
            name = card.get("name", "")
            fields = card.get("field", "").split("、") if isinstance(card.get("field"), str) else card.get("field", [])
            self.add_card(cid=cid, name=name, fields=fields)
        print(f"已新增 {len(cards)} 张卡牌")

    def delete_card(self, cid: str) -> bool:
        """
        删除指定卡牌记录。
        :param cid: 卡牌 ID
        :return: 删除成功返回 True，不存在返回 False
        """
        if cid not in self.existing_ids:
            return False

        self.existing_ids.remove(cid)
        self.id_attr_map.pop(cid, None)

        # 从 CSV 中移除记录
        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = [row for row in reader if row.get("id") != cid]

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(all_data)

        print(f"🗑️ 卡牌 {cid} 已删除")
        return True

    def get_card_name(self, cid: str) -> str:
        """
        根据卡牌 ID 获取卡牌名称，若未加载则自动刷新。
        """
        if cid not in self.existing_ids:
            self.refresh()
        return self.id_attr_map.get(cid, {}).get("name", f"未知卡牌({cid})")

    def get_all_cards(self) -> dict:
        """
        返回卡牌 ID → 名称 的完整映射副本
        """
        return {cid: data.get("name", "") for cid, data in self.id_attr_map.items()}

    def has_attribute(self, cid: str, attr_name: str, keyword: str) -> bool:
        """
        判断某张卡是否含有指定属性关键词（模糊匹配）
        支持多值字段判断
        """
        if cid not in self.existing_ids:
            self.refresh()

        card = self.id_attr_map.get(cid, {})
        value = card.get(attr_name)

        if value is None:
            return False
        elif isinstance(value, list):
            return keyword in value
        elif isinstance(value, str):
            return keyword == value or keyword.lower() in value.lower()
        return False

    def get_card_fields(self, cid: str) -> List[str]:
        """
        获取某张卡的字段列表（如：“怪兽”、“效果”、“炎”等）
        """
        return self.id_attr_map.get(cid, {}).get("field", [])

    def get_all_fields(self) -> Set[str]:
        """
        汇总所有卡牌出现过的字段，返回不重复集合
        """
        all_fields = set()
        for card in self.id_attr_map.values():
            fields = card.get("field", [])
            if isinstance(fields, list):
                all_fields.update(fields)
        return all_fields

    def search_cards_by_keyword(self, keyword: str) -> Dict[str, str]:
        """
        根据关键词模糊搜索卡牌名称
        返回 {cid: name} 字典
        """
        result = {}
        for cid, card in self.id_attr_map.items():
            name = card.get("name", "")
            if keyword.lower() in name.lower():
                result[cid] = name
        return result

    def update_card_attribute(self, cid: str, attr_name: str, old_value: str, new_value: str) -> bool:
        """
        更新指定卡牌的任意字段。
        - 支持多值字段用 '、' 分隔
        """
        if cid not in self.existing_ids:
            return False

        current_row = self.id_attr_map.get(cid, {})

        # 如果是多值字段，替换特定值
        if attr_name == "field":
            values = current_row.get("field", [])
            if old_value in values:
                idx = values.index(old_value)
                values[idx] = new_value
                current_row["field"] = values
            else:
                return False
        else:
            current_row[attr_name] = new_value

        self.id_attr_map[cid] = current_row
        self._save_updated_attributes([cid])
        return True

    def add_card_attribute(self, cid: str, attr_name: str, value: str) -> bool:
        """
        向指定卡牌添加一个字段值（适用于多值字段）
        """
        if cid not in self.existing_ids:
            return False

        current_row = self.id_attr_map.get(cid, {})

        if attr_name == "field":
            current_values = current_row.get("field", [])
            if value not in current_values:
                current_values.append(value)
                current_row["field"] = current_values
            else:
                return False
        else:
            current_row[attr_name] = value

        self.id_attr_map[cid] = current_row
        self._save_updated_attributes([cid])
        return True

    def remove_card_attribute(self, cid: str, attr_name: str, value: str) -> bool:
        """
        从指定卡牌中移除一个字段值（适用于多值字段）
        """
        if cid not in self.existing_ids:
            return False

        current_row = self.id_attr_map.get(cid, {})

        if attr_name == "field":
            current_values = current_row.get("field", [])
            if value in current_values:
                current_values.remove(value)
                current_row["field"] = current_values
            else:
                return False
        else:
            if current_row.get(attr_name) == value:
                current_row.pop(attr_name, None)
            else:
                return False

        self.id_attr_map[cid] = current_row
        self._save_updated_attributes([cid])
        return True

    def get_card_attributes(self, cid: str) -> Dict[str, Union[str, List[str]]]:
        """
        获取某张卡的所有属性字典
        """
        return self.id_attr_map.get(cid, {})

    def _save_updated_attributes(self, updated_cids: List[str]):
        """
        将指定卡牌的属性变更保存回 CSV 文件。
        支持新增记录。
        """
        if not updated_cids:
            return

        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = list(reader)

        data_map = {item['id']: item for item in all_data}

        for cid in updated_cids:
            updated = self.id_attr_map.get(cid, {})
            if not updated:
                continue

            new_row = {}
            for key in CSV_HEADERS:
                val = updated.get(key, "")
                if key == "field" and isinstance(val, list):
                    val = "、".join(val)
                new_row[key] = val

            data_map[cid] = new_row  # 无论是否存在，直接插入或覆盖

        sorted_data = sorted(data_map.values(), key=lambda x: int(x['id']))

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"已写入 {len(updated_cids)} 张卡牌（支持新增）")
