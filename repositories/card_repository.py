# repositories/card_repository.py

import csv
import os
from typing import List, Dict, Set, Optional
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
    本地卡牌数据库封装类：封装卡牌 ID → 名称 / 字段 等映射与操作
    - 支持缓存
    - 支持字段增删改查
    - 自动保存变更回 CSV 文件
    """

    def __init__(self):
        # 初始化空缓存结构
        self.existing_ids = set()       # 所有存在的卡片 ID（str 类型）
        self.id_name_map = {}           # 卡片 ID → 名称映射
        self.id_field_map = {}          # 卡片 ID → 字段列表映射
        self.load_existing_data()       # 加载本地 CSV 数据初始化

    def load_existing_data(self):
        """
        从 CSV 文件加载数据到缓存结构中。
        会清空旧数据。
        """
        self.existing_ids.clear()
        self.id_name_map.clear()
        self.id_field_map.clear()

        if not os.path.exists(CSV_FILE):
            return  # 文件不存在时，跳过加载

        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cid = row.get("id")
                name = row.get("name")
                fields = row.get("field", "").split("、")  # 多字段用“、”分隔
                if cid:
                    self.existing_ids.add(cid)
                    self.id_name_map[cid] = name
                    self.id_field_map[cid] = fields

    def refresh(self):
        """
        重新加载 CSV 文件数据，刷新缓存。
        """
        self.load_existing_data()
        print("本地数据库已刷新")

    def get_card_name(self, cid: str) -> str:
        """
        根据卡牌 ID 获取卡牌名称，若未加载则自动刷新。
        """
        if cid not in self.existing_ids:
            self.refresh()
        return self.id_name_map.get(cid, f"未知卡牌({cid})")

    def get_all_cards(self) -> dict:
        """
        返回卡牌 ID → 名称 的完整映射副本
        """
        return dict(self.id_name_map)

    def has_field(self, cid: str, keyword: str) -> bool:
        """
        判断某张卡是否含有指定字段关键词
        """
        return keyword in self.id_field_map.get(cid, [])

    def get_card_fields(self, cid: str) -> List[str]:
        """
        获取某张卡的字段列表（如：“怪兽”、“效果”、“炎”等）
        """
        return self.id_field_map.get(cid, [])

    def get_all_fields(self) -> Set[str]:
        """
        汇总所有卡牌出现过的字段，返回不重复集合
        """
        all_fields = set()
        for fields in self.id_field_map.values():
            all_fields.update(fields)
        return all_fields

    def search_cards_by_keyword(self, keyword: str) -> Dict[str, str]:
        """
        根据关键词模糊搜索卡牌名称（不区分大小写）
        返回 {cid: name} 字典
        """
        all_cards = self.get_all_cards()
        result = {}
        for cid, name in all_cards.items():
            if keyword.lower() in name.lower():
                result[cid] = name
        return result

    def update_card_field(self, cid: str, old_field: str, new_field: str) -> bool:
        """
        替换指定卡牌中的字段。
        成功替换并保存返回 True，否则 False。
        """
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if old_field in current:
            idx = current.index(old_field)
            current[idx] = new_field
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])  # 保存修改到文件
            return True
        return False

    def add_card_field(self, cid: str, field: str) -> bool:
        """
        向指定卡牌添加一个新字段。
        成功添加并保存返回 True，否则 False。
        """
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if field not in current:
            current.append(field)
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])
            return True
        return False

    def remove_card_field(self, cid: str, field: str) -> bool:
        """
        从指定卡牌中移除某字段。
        成功删除并保存返回 True，否则 False。
        """
        if cid not in self.existing_ids:
            return False
        current = self.id_field_map.get(cid, [])
        if field in current:
            current.remove(field)
            self.id_field_map[cid] = current
            self._save_updated_fields([cid])
            return True
        return False

    def _save_updated_fields(self, updated_cids: List[str]):
        """
        将指定卡牌的字段修改保存回 CSV 文件。
        仅影响更新过的卡牌。
        """
        if not updated_cids:
            return

        # 加载全部现有数据
        all_data = []
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                all_data = list(reader)

        data_map = {item['id']: item for item in all_data}

        # 更新字段
        for cid in updated_cids:
            if cid in data_map:
                data_map[cid]['field'] = '、'.join(self.id_field_map[cid])

        # 排序写回（按 id 升序）
        sorted_data = sorted(data_map.values(), key=lambda x: int(x['id']))

        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            writer.writeheader()
            writer.writerows(sorted_data)

        print(f"✅ 已更新 {len(updated_cids)} 张卡牌的字段信息")
