# gui/frames/card_editor_frame.py
import tkinter as tk
from tkinter import ttk
from services.local_db_service import LocalCardDB

class CardEditorFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.db = LocalCardDB()

        self.label = ttk.Label(self, text="卡牌字段编辑器")
        self.label.pack(padx=10, pady=10)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(padx=10, pady=5, fill="x")

        self.search_button = ttk.Button(self, text="搜索卡牌", command=self.search_cards)
        self.search_button.pack(padx=10, pady=5)

        self.tree = ttk.Treeview(self, columns=("ID", "名称", "字段"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("名称", text="名称")
        self.tree.heading("字段", text="字段")
        self.tree.pack(padx=10, pady=10, fill="both", expand=True)

    def search_cards(self):
        keyword = self.search_var.get().strip()
        self.tree.delete(*self.tree.get_children())
        all_cards = self.db.get_all_cards()
        for cid, name in all_cards.items():
            if keyword in name:
                fields = "、".join(self.db.get_card_fields(cid))
                self.tree.insert("", "end", values=(cid, name, fields))
