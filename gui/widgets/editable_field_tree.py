# gui/widgets/editable_field_tree.py (PySide6 version, inline edit + add/delete row)
from PySide6.QtGui import QStandardItemModel, QStandardItem

from gui.widgets.base_editable_tree import BaseEditableTree


class EditableFieldTree(BaseEditableTree):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent=parent, controller=controller)

    def get_column_count(self) -> int:
        return 3

    def get_header_labels(self) -> list:
        return ["卡牌ID", "卡牌名称", "字段列表"]

    def load_data(self):
        """加载数据库中的卡牌数据"""
        cards = self.controller.get_all_cards()  # {cid: name}
        for cid, name in cards.items():
            fields = ", ".join(self.controller.get_card_fields(cid))
            self.add_row(cid, name, fields)

    def add_row(self, cid="", name="", fields=""):
        row = [
            QStandardItem(cid),
            QStandardItem(name),
            QStandardItem(fields)
        ]
        for item in row:
            item.setEditable(True)
        self.model.appendRow(row)

    def get_all_rows(self):
        rows = []
        for i in range(self.model.rowCount()):
            cid = self.model.item(i, 0).text()
            name = self.model.item(i, 1).text()
            fields = self.model.item(i, 2).text()
            if cid or name or fields:
                rows.append([cid, name, fields])
        return rows

    def commit_data(self):
        """保存修改到数据库"""
        for i in range(self.model.rowCount()):
            old_cid = self.model.item(i, 0).data()
            old_name = self.model.item(i, 1).data()
            old_fields = self.model.item(i, 2).data()

            new_cid = self.model.item(i, 0).text().strip()
            new_name = self.model.item(i, 1).text().strip()
            new_fields = self.model.item(i, 2).text().strip()

            if not new_cid or not new_name:
                self._show_error("错误", "卡牌 ID 和名称不能为空")
                continue

            try:
                if not self._card_exists(new_cid):
                    field_list = [f.strip() for f in new_fields.split(",") if f.strip()]
                    self.controller.add_card(cid=new_cid, name=new_name, fields=field_list)
                else:
                    self.controller.update_card_attribute(old_cid, "id", old_cid, new_cid)
                    self.controller.update_card_attribute(new_cid, "name", old_name, new_name)
                    self._update_fields(old_cid, old_fields, new_fields)
            except Exception as e:
                self._show_error("错误", f"保存失败: {e}")

    def _card_exists(self, cid: str) -> bool:
        return cid in self.controller.get_all_cards()

    def _update_fields(self, cid: str, old_str: str, new_str: str):
        old_list = [f.strip() for f in old_str.split(",") if f.strip()]
        new_list = [f.strip() for f in new_str.split(",") if f.strip()]

        added = set(new_list) - set(old_list)
        removed = set(old_list) - set(new_list)

        for f in removed:
            self.controller.remove_card_attribute(cid, "field", f)
        for f in added:
            self.controller.add_card_attribute(cid, "field", f)
