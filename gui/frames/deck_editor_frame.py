# gui/frames/deck_editor_frame.py

import tkinter as tk
from tkinter import ttk, filedialog


class DeckEditorFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller  # 保存 controller

        self.label = ttk.Label(self, text="卡组文件路径：")
        self.label.pack(anchor="w", padx=10, pady=(10, 0))

        self.file_entry = ttk.Entry(self, width=60)
        self.file_entry.pack(padx=10, pady=5, fill="x")

        self.browse_button = ttk.Button(self, text="选择 YDK 文件", command=self.load_file)
        self.browse_button.pack(padx=10, pady=5)

    def load_file(self):
        path = filedialog.askopenfilename(filetypes=[("YDK 文件", "*.ydk")])
        if path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, path)
            try:
                card_names = self.controller.load_deck_from_path(path)  # ← 通过 controller 加载
                self.text_preview.delete("1.0", tk.END)
                for name in card_names:
                    self.text_preview.insert(tk.END, name + "\n")
            except Exception as e:
                self.text_preview.insert(tk.END, f"加载失败：{e}\n")
