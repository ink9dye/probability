# gui/widgets/editable_field_tree.py
import tkinter as tk
from tkinter import ttk


class EditableFieldTree(ttk.Frame):
    """
    可编辑表格控件：支持点击任意列进行编辑
    - 支持 ID、名称、字段等任意列编辑
    - 编辑后自动调用 controller 的更新接口
    """

    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.current_item = None
        self.current_cid = None
        self.current_old_value = None
        self.current_attr_name = None  # 当前正在编辑的字段名

        self.column_map = {
            "#1": "id",
            "#2": "name",
            "#3": "field"
        }

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
        cards = self.controller.get_all_cards()
        self.update_tree(cards)

    def update_tree(self, cards: dict):
        """刷新表格数据"""
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cid, name in cards.items():
            fields = ", ".join(self.controller.get_card_fields(cid))
            self.tree.insert("", tk.END, values=(cid, name, fields))

    def on_cell_edit(self, event):
        """点击任意单元格进入编辑模式"""
        x, y = event.x, event.y
        col = self.tree.identify_column(x)
        item = self.tree.identify_row(y)

        if not item:
            return

        # 获取原始数据
        values = list(self.tree.item(item, "values"))
        column_names = ["id", "name", "field"]  # 与 Treeview 列顺序一致
        col_index = int(col[1:]) - 1  # 将 "#2" 转换为索引 1
        cid = values[0]

        # 设置当前编辑的字段名和旧值
        self.current_attr_name = column_names[col_index]
        original_data = self.controller.get_card_attributes(cid)
        old_value = ""

        if self.current_attr_name == "id":
            old_value = cid
        elif self.current_attr_name == "name":
            old_value = original_data.get("name", "")
        elif self.current_attr_name == "field":
            old_value = ", ".join(original_data.get("field", []))

        # 定位 Entry
        bbox = self.tree.bbox(item, column=col)
        if not bbox:
            return

        self.current_item = item
        self.current_cid = cid
        self.current_old_value = old_value

        # 设置 Entry 内容并定位
        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, old_value)
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_entry.focus_set()
        self.edit_entry.selection_range(0, tk.END)

        # 绑定事件
        self.edit_entry.bind("<FocusOut>", self.save_edit)
        self.edit_entry.bind("<Return>", self.save_edit)

    def save_edit(self, event=None):
        """保存字段修改"""
        new_value = self.edit_entry.get().strip()
        self.edit_entry.place_forget()

        if not hasattr(self, 'current_item'):
            return

        cid = self.current_cid
        attr_name = self.current_attr_name
        old_value = self.current_old_value

        if new_value == old_value:
            self.reset_current_state()
            return

        try:
            if attr_name == "id":
                success = self.controller.update_card_attribute(cid, "id", cid, new_value)
            elif attr_name == "name":
                success = self.controller.update_card_attribute(cid, "name", old_value, new_value)
            elif attr_name == "field":
                old_list = [f.strip() for f in old_value.split(",") if f.strip()]
                new_list = [f.strip() for f in new_value.split(",") if f.strip()]
                added = set(new_list) - set(old_list)
                removed = set(old_list) - set(new_list)

                for f in removed:
                    self.controller.remove_card_attribute(cid, "field", f)
                for f in added:
                    self.controller.add_card_attribute(cid, "field", f)
                success = True
            else:
                success = self.controller.update_card_attribute(cid, attr_name, old_value, new_value)

            if success:
                self.load_data()
        except Exception as e:
            print(f"保存失败: {e}")

        self.reset_current_state()

    def reset_current_state(self):
        """重置当前编辑状态"""
        self.current_item = None
        self.current_cid = None
        self.current_old_value = None
        self.current_attr_name = None
