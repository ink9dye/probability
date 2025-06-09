# gui/widgets/editable_field_tree.py (PySide6 version, inline edit + add/delete row)

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableView, QLineEdit, QMenu,
    QMessageBox
)
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem

class EditableFieldTree(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索")
        layout.addWidget(self.search_input)

        # 表格视图
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)

        # 数据模型
        self.model = QStandardItemModel(0, 3)
        self.model.setHorizontalHeaderLabels(["卡牌ID", "卡牌名称", "字段列表"])
        self.table_view.setModel(self.model)

        # 过滤代理模型
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.search_input.textChanged.connect(self.proxy_model.setFilterFixedString)
        self.table_view.setModel(self.proxy_model)

        # 右键菜单绑定
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

    def load_data(self):
        """加载数据库中的卡牌数据"""
        cards = self.controller.get_all_cards()  # {cid: name}
        for cid, name in cards.items():
            fields = ", ".join(self.controller.get_card_fields(cid))
            self.add_row(cid, name, fields)

    def add_row(self, cid, name, fields):
        row = [
            QStandardItem(cid),
            QStandardItem(name),
            QStandardItem(fields)
        ]
        for item in row:
            item.setEditable(True)  # 所有列都允许编辑
        self.model.appendRow(row)

    def refresh(self):
        self.model.setRowCount(0)
        self.load_data()

    def show_context_menu(self, position):
        index = self.table_view.indexAt(position)
        menu = QMenu(self)

        action_add = menu.addAction("添加记录")
        action_delete = menu.addAction("删除记录")

        action = menu.exec_(self.table_view.viewport().mapToGlobal(position))

        if action == action_add:
            self.on_add_record()

        elif action == action_delete and index.isValid():
            self.on_delete_record(index)

    def on_add_record(self):
        """添加一条空记录（默认值为空）"""
        row = [
            QStandardItem(""),  # CID
            QStandardItem(""),  # Name
            QStandardItem("")   # Fields
        ]
        for item in row:
            item.setEditable(True)
        self.model.appendRow(row)

    def on_delete_record(self, proxy_index):
        source_index = self.proxy_model.mapToSource(proxy_index)
        cid = self.model.item(source_index.row(), 0).text()
        confirm = QMessageBox.question(
            self, "确认删除", f"确定要删除卡牌 {cid} 吗？",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                success = self.controller.delete_card(cid)
                if success:
                    self.model.removeRow(source_index.row())
                else:
                    raise Exception("删除失败，请检查数据库连接或权限。")
            except Exception as e:
                QMessageBox.critical(self, "错误", str(e))

    def commit_data(self, index):
        """
        编辑完成后提交数据到模型并保存至数据库。
        :param index: 被修改的单元格索引（来自 proxy model）
        """
        proxy_row = index.row()
        source_row = self.proxy_model.mapToSource(proxy_row)

        cid_item = self.model.item(source_row.row(), 0)
        name_item = self.model.item(source_row.row(), 1)
        fields_item = self.model.item(source_row.row(), 2)

        old_cid = cid_item.data(Qt.DisplayRole)
        old_name = name_item.data(Qt.DisplayRole)
        old_fields = fields_item.data(Qt.DisplayRole)

        new_cid = cid_item.text().strip()
        new_name = name_item.text().strip()
        new_fields = fields_item.text().strip()

        if not new_cid or not new_name:
            QMessageBox.warning(self, "警告", "卡牌ID和名称不能为空！")
            return

        try:
            if not self._card_exists(new_cid):
                # 新增记录
                field_list = [f.strip() for f in new_fields.split(",") if f.strip()]
                self.controller.add_card(cid=new_cid, name=new_name, fields=field_list)
            else:
                # 更新已有记录
                self.controller.update_card_attribute(old_cid, "id", old_cid, new_cid)
                self.controller.update_card_attribute(new_cid, "name", old_name, new_name)
                self._update_fields(old_cid, old_fields, new_fields)

        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存失败: {e}")
            self.refresh()  # 回滚显示数据

    def _card_exists(self, cid: str) -> bool:
        """检查是否已存在该卡牌"""
        return cid in self.controller.get_all_cards()

    def _update_fields(self, cid: str, old_str: str, new_str: str):
        """同步字段变化"""
        old_list = [f.strip() for f in old_str.split(",") if f.strip()]
        new_list = [f.strip() for f in new_str.split(",") if f.strip()]

        added = set(new_list) - set(old_list)
        removed = set(old_list) - set(new_list)

        for f in removed:
            self.controller.remove_card_attribute(cid, "field", f)
        for f in added:
            self.controller.add_card_attribute(cid, "field", f)

