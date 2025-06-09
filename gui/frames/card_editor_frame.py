# gui/frames/card_editor_frame.py

import tkinter as tk
from tkinter import ttk, messagebox

# 引入自定义控件
from gui.widgets.editable_field_tree import EditableFieldTree


class CardEditorFrame(ttk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.create_widgets()

    def create_widgets(self):
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=5, fill=tk.X)
        self.search_entry.bind("<Return>", lambda e: self.on_search())  # ← 新增绑定回车搜索
        self.search_button = ttk.Button(self, text="搜索", command=self.on_search)
        self.search_button.pack(pady=2, fill=tk.X)

        # 字段表格（使用自定义控件）
        self.field_tree = EditableFieldTree(self, controller=self.controller)
        self.field_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 加载全部卡片
        self.field_tree.load_data()

        # 按钮区
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5, fill=tk.X)

        self.add_btn = ttk.Button(btn_frame, text="添加字段", command=self.on_add_field)
        self.add_btn.pack(side=tk.LEFT, padx=2)

        self.edit_btn = ttk.Button(btn_frame, text="修改字段", command=self.on_edit_field)
        self.edit_btn.pack(side=tk.LEFT, padx=2)

        self.remove_btn = ttk.Button(btn_frame, text="删除字段", command=self.on_remove_field)
        self.remove_btn.pack(side=tk.LEFT, padx=2)

        self.batch_btn = ttk.Button(btn_frame, text="批量添加字段", command=self.on_batch_add)
        self.batch_btn.pack(side=tk.LEFT, padx=2)

        self.refresh_btn = ttk.Button(btn_frame, text="刷新数据库", command=self.on_refresh)
        self.refresh_btn.pack(side=tk.RIGHT, padx=2)

    def on_search(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            return
        cards = self.controller.search_cards_by_keyword(keyword)
        self.field_tree.update_tree(cards)

    def get_selected_cids(self) -> list:
        selected_items = self.field_tree.tree.selection()
        return [self.field_tree.tree.item(i)['values'][0] for i in selected_items]

    def on_add_field(self):
        cids = self.get_selected_cids()
        if not cids:
            messagebox.showwarning("警告", "请先选择卡牌")
            return
        field = tk.simpledialog.askstring("添加字段", "请输入要添加的字段：")
        if field:
            self.controller.add_field_to_cards(cids, field)
            self.field_tree.load_data()

    def on_edit_field(self):
        cids = self.get_selected_cids()
        if not cids or len(cids) > 1:
            messagebox.showwarning("警告", "请选择一张卡牌进行编辑")
            return
        old_field = tk.simpledialog.askstring("修改字段", "请输入要修改的字段名：")
        new_field = tk.simpledialog.askstring("修改字段", "请输入新的字段名：")
        if old_field and new_field:
            self.controller.update_card_field(cids[0], old_field, new_field)
            self.field_tree.load_data()

    def on_remove_field(self):
        cids = self.get_selected_cids()
        if not cids:
            messagebox.showwarning("警告", "请先选择卡牌")
            return
        field = tk.simpledialog.askstring("删除字段", "请输入要删除的字段名：")
        if field:
            for cid in cids:
                self.controller.remove_card_field(cid, field)
            self.field_tree.load_data()

    def on_batch_add(self):
        cids = self.get_selected_cids()
        if not cids:
            messagebox.showwarning("警告", "请先选择卡牌")
            return
        field = tk.simpledialog.askstring("批量添加字段", "请输入要添加的字段名：")
        if field:
            self.controller.add_field_to_cards(cids, field)
            self.field_tree.load_data()

    def on_refresh(self):
        self.controller.refresh_local_db()
        keyword = self.search_var.get().strip()
        if keyword:
            self.on_search()
        else:
            self.field_tree.load_data()
