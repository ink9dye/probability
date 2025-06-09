# gui/frames/condition_editor_frame.py
import tkinter as tk
from tkinter import ttk, filedialog
import json
from services.condition_service import get_conditions

class ConditionEditorFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.label = ttk.Label(self, text="条件文件路径：")
        self.label.pack(anchor="w", padx=10, pady=(10, 0))

        self.file_entry = ttk.Entry(self, width=60)
        self.file_entry.pack(padx=10, pady=5, fill="x")

        self.browse_button = ttk.Button(self, text="加载条件文件", command=self.load_conditions)
        self.browse_button.pack(padx=10, pady=5)

        self.tree = ttk.Treeview(self, columns=("表达式", "符号", "值"), show="headings")
        self.tree.heading("表达式", text="表达式")
        self.tree.heading("符号", text="符号")
        self.tree.heading("值", text="值")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

    def load_conditions(self):
        path = filedialog.askopenfilename(filetypes=[("JSON 文件", "*.json")])
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)
            try:
                conds = get_conditions(path, is_path=True)
                self.tree.delete(*self.tree.get_children())
                for cond in conds:
                    self.tree.insert("", "end", values=(cond.expression, cond.operator, cond.value))
            except Exception as e:
                self.tree.insert("", "end", values=("加载失败", str(e), ""))