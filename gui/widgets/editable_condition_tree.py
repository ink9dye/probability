# gui/widgets/editable_condition_tree.py

from gui.widgets.base_editable_tree import BaseEditableTree
from PySide6.QtGui import QStandardItem


class EditableConditionTree(BaseEditableTree):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent=parent, controller=controller)

    def get_column_count(self) -> int:
        return 3

    def get_header_labels(self) -> list:
        return ["表达式", "操作符", "值"]

    def load_data(self, conditions: list = None):
        self.model.setRowCount(0)
        if not conditions:
            return

        for cond in conditions:
            if len(cond) >= 3:
                self.add_row(cond[0], cond[1], cond[2])

    def add_row(self, expr="", op="", val=""):
        row = [
            QStandardItem(expr),
            QStandardItem(op),
            QStandardItem(val)
        ]
        for item in row:
            item.setEditable(True)
        self.model.appendRow(row)

    def get_all_rows(self):
        rows = []
        for i in range(self.model.rowCount()):
            expr = self.model.item(i, 0).text()
            op = self.model.item(i, 1).text()
            val = self.model.item(i, 2).text()
            if expr or op or val:
                rows.append([expr, op, val])
        return rows
