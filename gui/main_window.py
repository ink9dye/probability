# main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
from gui.controller import AppController
from gui.frames.main_frame import MainFrame
from gui.frames.card_editor_frame import CardEditorFrame


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("游戏王卡组模拟器")
        self.geometry("1100x750")

        self.controller = AppController(self)

        # 创建 Notebook 作为主界面容器
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # 主控面板
        self.main_frame = MainFrame(self.notebook, self.controller)
        self.notebook.add(self.main_frame, text="模拟器")

        # 字段编辑器面板
        self.card_editor_frame = CardEditorFrame(self.notebook, controller=self.controller)
        self.notebook.add(self.card_editor_frame, text="字段管理")

        # 菜单栏
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="刷新数据库", command=self.refresh_database)
        file_menu.add_command(label="字段管理", command=self.show_card_editor)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.destroy)
        menu_bar.add_cascade(label="文件", menu=file_menu)

    def refresh_database(self):
        try:
            self.controller.refresh_local_db()
            messagebox.showinfo("提示", "数据库刷新成功")
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败: {e}")

    def show_card_editor(self):
        # 切换到字段管理 Tab
        self.notebook.select(self.card_editor_frame)


if __name__ == '__main__':
    MainWindow().mainloop()
