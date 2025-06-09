# gui/widgets/editable_field_tree.py
import tkinter as tk
from tkinter import ttk


class EditableFieldTree(ttk.Frame):
    """
    可编辑字段表格控件：
    - 显示卡牌ID、名称、字段
    - 支持点击字段列直接编辑
    - 自动保存增删字段变更
    """

    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.current_item = None
        self.current_cid = None
        self.current_old_fields = []

        self.create_widgets()

    def create_widgets(self):
        # 表格展示
        self.tree = ttk.Treeview(self, columns=("ID", "名称", "字段"), show="headings")
        self.tree.heading("ID", text="卡牌ID")
        self.tree.heading("名称", text="卡牌名称")
        self.tree.heading("字段", text="字段列表")
        self.tree.column("ID", width=80)
        self.tree.column("名称", width=150)
        self.tree.column("字段", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 编辑用 Entry（隐藏初始）
        self.edit_entry = ttk.Entry(self)
        self.edit_entry.place_forget()

        # 绑定点击事件
        self.tree.bind("<Button-1>", self.on_cell_edit)

    def load_data(self):
        """加载并显示所有卡牌数据"""
        cards = self.controller.get_all_cards()  # 假设 controller 提供 get_all_cards()
        self.update_tree(cards)

    def update_tree(self, cards: dict):
        """刷新表格数据"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cid, name in cards.items():
            fields = ", ".join(self.controller.get_card_fields(cid))
            self.tree.insert("", tk.END, values=(cid, name, fields))

    def on_cell_edit(self, event):
        """点击字段列进入编辑模式"""
        x, y = event.x, event.y
        col = self.tree.identify_column(x)
        item = self.tree.identify_row(y)

        if not item or col != "#3":  # 只允许点击“字段”列（第3列）
            return

        # 获取原始数据
        values = self.tree.item(item, "values")
        cid = values[0]
        old_fields = self.controller.get_card_fields(cid)

        # 定位 Entry
        bbox = self.tree.bbox(item, column=col)
        if not bbox:
            return

        self.current_item = item
        self.current_cid = cid
        self.current_old_fields = old_fields

        # 设置 Entry 内容并定位
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, ",".join(old_fields))
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_entry.focus_set()
        self.edit_entry.selection_range(0, tk.END)

        # 绑定失去焦点或回车事件
        self.edit_entry.bind("<FocusOut>", self.save_edit)
        self.edit_entry.bind("<Return>", self.save_edit)

    def save_edit(self, event=None):
        """保存字段修改"""
        new_input = self.edit_entry.get().strip()
        self.edit_entry.place_forget()

        if not hasattr(self, 'current_item'):
            return

        cid = self.current_cid
        old_fields = self.current_old_fields

        if not new_input:
            del self.current_item
            return

        new_fields = [f.strip() for f in new_input.split(",") if f.strip()]
        if set(new_fields) == set(old_fields):
            del self.current_item
            return  # 没有变化不保存

        added = set(new_fields) - set(old_fields)
        removed = set(old_fields) - set(new_fields)

        for f in removed:
            self.controller.remove_card_field(cid, f)
        for f in added:
            self.controller.add_field_to_cards([cid], f)

        del self.current_item  # 清除临时变量
        self.load_data()  # 刷新界面

