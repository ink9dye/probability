# gui/frames/deck_editor_frame.py

from PySide6.QtWidgets import QFrame, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
from PySide6.QtCore import Qt
from gui.widgets.raw_text_editor import RawTextEditor
from config.settings import DECK_DIR  # ✅ 引入 settings 中定义的路径常量


class DeckEditorFrame(QFrame):
    """
    卡组编辑器界面，用于加载、编辑和保存 TXT 格式的卡组文件。
    支持浏览、新建、保存操作，默认路径为 settings 中定义的 DECK_DIR。
    """

    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.current_file = None
        self.default_dir = DECK_DIR  # ✅ 使用 settings 中定义的路径
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # 文件路径选择区域
        path_layout = QHBoxLayout()
        self.file_entry = QLineEdit()
        btn_browse = QPushButton("浏览")
        btn_save = QPushButton("保存")

        path_layout.addWidget(self.file_entry)
        path_layout.addWidget(btn_browse)
        path_layout.addWidget(btn_save)
        layout.addLayout(path_layout)

        # 编辑器主体
        self.editor = RawTextEditor(controller=self.controller)
        layout.addWidget(self.editor, stretch=1)

        # 底部按钮区域
        btn_layout = QHBoxLayout()
        btn_new = QPushButton("新建")
        btn_save_top = QPushButton("保存")
        btn_layout.addWidget(btn_new)
        btn_layout.addWidget(btn_save_top)
        layout.addLayout(btn_layout)

        # 绑定事件
        btn_browse.clicked.connect(self.load_deck)
        btn_save.clicked.connect(self.save_deck)
        btn_save_top.clicked.connect(self.save_deck)
        btn_new.clicked.connect(self.new_file)

    def load_deck(self):
        from PySide6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择卡组文件",
            self.default_dir,  # ✅ 使用 settings 中定义的默认路径
            "TXT 文件 (*.txt)"
        )
        if not path:
            return

        try:
            # with open(path, 'r', encoding='utf-8') as f:
            #     content = f.read()
                content = "\n".join(self.controller.load_deck_txt(path))
                self.editor.setPlainText(content)
                self.file_entry.setText(path)
                self.current_file = path
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "加载失败", str(e))

    def save_deck(self):
        if not self.current_file:
            from PySide6.QtWidgets import QFileDialog
            self.current_file, _ = QFileDialog.getSaveFileName(
                self,
                "保存文件",
                self.default_dir,  # ✅ 使用 settings 中定义的默认路径
                "TXT 文件 (*.txt)"
            )
            if not self.current_file:
                return

        try:
            content = self.editor.toPlainText()
            with open(self.current_file, 'w', encoding='utf-8') as f:
                f.write(content)
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "成功", f"已保存至 {self.current_file}")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "保存失败", str(e))

    def new_file(self):
        self.current_file = None
        self.file_entry.clear()
        self.editor.clear()
