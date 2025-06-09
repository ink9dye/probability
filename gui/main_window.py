
import tkinter as tk
from tkinter import ttk, messagebox
from gui.controller import AppController
from gui.frames.main_frame import MainFrame


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("游戏王卡组模拟器")
        self.geometry("1100x750")

        self.controller = AppController(self)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.main_frame = MainFrame(self.notebook, self.controller)
        self.notebook.add(self.main_frame, text="模拟器")

        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="刷新数据库", command=self.refresh_database)
        file_menu.add_command(label="退出", command=self.destroy)
        menu_bar.add_cascade(label="文件", menu=file_menu)

    def refresh_database(self):
        try:
            self.controller.refresh_local_db()
            messagebox.showinfo("提示", "数据库刷新成功")
        except Exception as e:
            messagebox.showerror("错误", f"刷新失败: {e}")


if __name__ == '__main__':
    MainWindow().mainloop()
