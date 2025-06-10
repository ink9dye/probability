# gui/widgets/base_editable_tree.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableView, QLineEdit, QMenu
from PySide6.QtCore import Qt, QSortFilterProxyModel
from PySide6.QtGui import QStandardItemModel, QStandardItem


class BaseEditableTree(QWidget):
    """
    所有可编辑表格的基类
    子类应重写 load_data(), add_row(), get_all_rows() 等方法
    """

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.model = None
        self.proxy_model = None
        self.table_view = None

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 搜索框（可选）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索")
        self.search_input.textChanged.connect(self.apply_filter)
        layout.addWidget(self.search_input)

        # 表格视图
        self.table_view = QTableView()
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table_view)

        # 数据模型
        self.model = QStandardItemModel(0, self.get_column_count())
        self.model.setHorizontalHeaderLabels(self.get_header_labels())
        self.table_view.setModel(self.model)

        # 过滤代理模型
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.model)
        self.proxy_model.setFilterKeyColumn(-1)  # 全字段过滤
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.table_view.setModel(self.proxy_model)

        # 右键菜单
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.show_context_menu)

    def get_column_count(self) -> int:
        """子类必须重写：返回列数"""
        raise NotImplementedError()

    def get_header_labels(self) -> list:
        """子类必须重写：返回表头标签"""
        raise NotImplementedError()

    def load_data(self):
        """子类必须重写：加载数据到表格"""
        raise NotImplementedError()

    def apply_filter(self, text: str):
        """应用搜索过滤"""
        self.proxy_model.setFilterFixedString(text)

    def show_context_menu(self, position):
        """右键菜单通用实现"""
        menu = QMenu(self)

        action_add = menu.addAction("添加记录")
        action_delete = menu.addAction("删除记录")

        action = menu.exec_(self.table_view.viewport().mapToGlobal(position))

        if action == action_add:
            self.on_add_record()

        elif action == action_delete:
            index = self.table_view.indexAt(position)
            if index.isValid():
                self.on_delete_record(index)

    def on_add_record(self):
        """添加一条空记录"""
        row = [QStandardItem("") for _ in range(self.get_column_count())]
        for item in row:
            item.setEditable(True)
        self.model.appendRow(row)

    def on_delete_record(self, proxy_index):
        """删除记录（子类需处理具体业务）"""
        source_index = self.proxy_model.mapToSource(proxy_index)
        confirm = self._show_confirm("确认删除", "确定要删除该行吗？")
        if confirm:
            self.model.removeRow(source_index.row())

    def get_all_rows(self) -> list:
        """获取所有非空行数据"""
        rows = []
        for i in range(self.model.rowCount()):
            row = [self.model.item(i, j).text() for j in range(self.model.columnCount())]
            if any(row):
                rows.append(row)
        return rows

    def _show_info(self, title: str, message: str):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.information(self, title, message)

    def _show_error(self, title: str, message: str):
        from PySide6.QtWidgets import QMessageBox
        QMessageBox.critical(self, title, message)

    def _show_confirm(self, title: str, message: str) -> bool:
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(self, title, message,
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        return reply == QMessageBox.Yes
