# gui/widgets/raw_text_editor.py
from PySide6.QtWidgets import QTextEdit, QFileDialog
from PySide6.QtCore import Qt


class RawTextEditor(QTextEdit):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller
        self.file_path = None  # 当前打开的文件路径

    def load_file(self, file_path: str):
        """加载文本文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.setPlainText(content)
                self.file_path = file_path
        except Exception as e:
            self.controller._show_error("加载失败", f"无法读取文件: {e}")

    def save_file(self, file_path: str = None):
        """保存当前内容到指定路径"""
        if not file_path and not self.file_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "保存文件", "", "文本文件 (*.txt)")
            if not file_path:
                return False

        path_to_save = file_path or self.file_path
        try:
            with open(path_to_save, 'w', encoding='utf-8') as f:
                f.write(self.toPlainText())
            self.file_path = path_to_save
            return True
        except Exception as e:
            self.controller._show_error("保存失败", f"写入文件时出错: {e}")
            return False
