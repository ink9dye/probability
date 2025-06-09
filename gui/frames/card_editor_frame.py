# gui/frames/card_editor_frame.py (简化版)

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QVBoxLayout
from gui.widgets.editable_field_tree import EditableFieldTree


class CardEditorFrame(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # 左侧：可编辑表格
        self.field_tree = EditableFieldTree(controller=self.controller)
        layout.addWidget(self.field_tree, stretch=3)

        # 右侧：仅刷新按钮
        btn_layout = QVBoxLayout()
        self.refresh_btn = QPushButton("刷新数据库")
        self.refresh_btn.clicked.connect(self.on_refresh)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()

        layout.addLayout(btn_layout, stretch=1)

    def on_refresh(self):
        self.field_tree.refresh()
