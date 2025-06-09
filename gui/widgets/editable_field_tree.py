import tkinter as tk
from tkinter import ttk, messagebox, Menu


class EditableFieldTree(ttk.Frame):
    def __init__(self, parent, controller=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.controller = controller
        self.last_search_keyword = ""
        self.current_item = None
        self.current_cid = None
        self.current_old_value = None
        self.current_attr_name = None

        self.column_map = {
            "#1": "id",
            "#2": "name",
            "#3": "field"
        }

        self.create_widgets()

    def create_widgets(self):
        self.tree = ttk.Treeview(self, columns=("ID", "名称", "字段"), show="headings")
        self.tree.heading("ID", text="卡牌ID")
        self.tree.heading("名称", text="卡牌名称")
        self.tree.heading("字段", text="字段列表")
        self.tree.column("ID", width=80)
        self.tree.column("名称", width=150)
        self.tree.column("字段", width=300)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.edit_entry = ttk.Entry(self)
        self.edit_entry.place_forget()

        self.tree.bind("<Button-1>", self.handle_click_and_edit)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = Menu(self.winfo_toplevel(), tearoff=0)
        self.context_menu.add_command(label="删除该记录", command=self.delete_selected_row)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=5, fill=tk.X)
        self.search_entry.bind("<Return>", lambda e: self.on_search_enter())

    def load_data(self):
        cards = self.controller.get_all_cards()
        self.update_tree(cards)

    def refresh_tree_preserving_search(self):
        keyword = self.last_search_keyword.strip()
        if keyword:
            result = self.controller.search_cards_by_keyword(keyword)
            self.update_tree(result)
        else:
            self.load_data()

    def handle_click_and_edit(self, event):
        if self.edit_entry.winfo_ismapped():
            # 如果编辑框还在显示中，尝试保存当前编辑
            self.save_edit()

        # 延迟处理点击进入编辑的逻辑（让 save_edit 完成）
        self.after(150, lambda: self.on_cell_edit(event))

    def update_tree(self, cards: dict):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for cid, name in cards.items():
            fields = ", ".join(self.controller.get_card_fields(cid))
            self.tree.insert("", tk.END, values=(cid, name, fields))

    def on_cell_edit(self, event):
        x, y = event.x, event.y
        col = self.tree.identify_column(x)
        item = self.tree.identify_row(y)

        if not item:
            return

        values = list(self.tree.item(item, "values"))
        column_names = ["id", "name", "field"]
        col_index = int(col[1:]) - 1
        cid = values[0]

        self.current_attr_name = column_names[col_index]
        original_data = self.controller.get_card_attributes(cid)
        old_value = ""

        if self.current_attr_name == "id":
            old_value = cid
        elif self.current_attr_name == "name":
            old_value = original_data.get("name", "")
        elif self.current_attr_name == "field":
            old_value = ", ".join(original_data.get("field", []))

        bbox = self.tree.bbox(item, column=col)
        if not bbox:
            return

        self.current_item = item
        self.current_cid = cid
        self.current_old_value = old_value

        self.edit_entry.delete(0, tk.END)
        self.edit_entry.insert(0, old_value)
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_entry.focus_set()
        self.edit_entry.selection_range(0, tk.END)

        # 清除旧的事件绑定，防止重复绑定触发多次
        for seq in ("<FocusOut>", "<Return>", "<Escape>"):
            self.edit_entry.unbind(seq)

        # 绑定事件：失去焦点（稍微延迟），按回车保存，Esc 取消编辑
        self.edit_entry.bind("<FocusOut>", lambda e: self.after(100, self.save_edit))
        self.edit_entry.bind("<Return>", self.save_edit)
        self.edit_entry.bind("<Escape>", lambda e: self.edit_entry.place_forget())

    def update_current_row(self):
        if not self.current_item or not self.current_cid:
            return

        name = self.controller.get_card_attributes(self.current_cid).get("name", "")
        fields = ", ".join(self.controller.get_card_fields(self.current_cid))
        self.tree.item(self.current_item, values=(self.current_cid, name, fields))

    def save_edit(self, event=None):
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
                self.update_current_row()


        except Exception as e:
            print(f"保存失败: {e}")

        self.reset_current_state()

    def reset_current_state(self):
        self.current_item = None
        self.current_cid = None
        self.current_old_value = None
        self.current_attr_name = None

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def delete_selected_row(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = selected_items[0]
        values = self.tree.item(item, "values")
        cid = values[0]

        confirm = messagebox.askyesno("删除卡牌", f"确定要删除卡牌 {cid} 吗？")
        if confirm:
            try:
                self.controller.delete_card(cid)
                self.load_data()
            except Exception as e:
                messagebox.showerror("错误", f"删除失败: {e}")

    def on_search_enter(self):
        keyword = self.search_var.get().strip()
        self.last_search_keyword = keyword  # ✅ 记录当前搜索关键词

        if keyword:
            result = self.controller.search_cards_by_keyword(keyword)
            self.update_tree(result)
        else:
            self.load_data()


