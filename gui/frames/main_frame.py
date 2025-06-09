
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.controller import AppController


class MainFrame(ttk.Frame):
    def __init__(self, parent, controller: AppController):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # === 卡组码导入区域（YDK → TXT）===
        ydk_frame = ttk.LabelFrame(self, text="导入卡组码（.ydk）")
        ydk_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        ttk.Button(ydk_frame, text="选择 YDK 文件", command=self.load_ydk_file).pack(side="left", padx=5, pady=5)
        ttk.Button(ydk_frame, text="从剪贴板粘贴 YDK 文本", command=self.load_ydk_from_clipboard).pack(side="left", padx=5, pady=5)
        ttk.Button(ydk_frame, text="导出为 TXT 卡组", command=self.export_deck_txt).pack(side="left", padx=5, pady=5)

        # === 卡组加载区域（TXT）===
        deck_frame = ttk.LabelFrame(self, text="加载卡组（TXT）")
        deck_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        self.deck_path_var = tk.StringVar()
        ttk.Entry(deck_frame, textvariable=self.deck_path_var, width=60).pack(side="left", padx=5, pady=5)
        ttk.Button(deck_frame, text="选择 TXT 文件", command=self.load_txt_deck).pack(side="left", padx=5, pady=5)

        # 卡组预览
        self.deck_preview = tk.Text(self, height=10, width=80)
        self.deck_preview.pack(padx=10, pady=5, fill="both", expand=True)

        # === 条件加载区域（TXT）===
        condition_frame = ttk.LabelFrame(self, text="加载条件（TXT）")
        condition_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        self.condition_path_var = tk.StringVar()
        ttk.Entry(condition_frame, textvariable=self.condition_path_var, width=60).pack(side="left", padx=5, pady=5)
        ttk.Button(condition_frame, text="选择条件文件", command=self.load_conditions).pack(side="left", padx=5, pady=5)

        self.condition_tree = ttk.Treeview(condition_frame, columns=("表达式", "符号", "值"), show="headings", height=5)
        for col in ("表达式", "符号", "值"):
            self.condition_tree.heading(col, text=col)
        self.condition_tree.pack(padx=10, pady=5, fill="x")

        # === 模拟区域 ===
        simulate_frame = ttk.LabelFrame(self, text="模拟设置")
        simulate_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        ttk.Label(simulate_frame, text="抽卡数").pack(side="left", padx=5)
        self.draw_size_var = tk.IntVar(value=5)
        ttk.Spinbox(simulate_frame, from_=1, to=10, textvariable=self.draw_size_var, width=5).pack(side="left", padx=5)

        ttk.Label(simulate_frame, text="模拟次数").pack(side="left", padx=5)
        self.num_draws_var = tk.IntVar(value=100000)
        ttk.Spinbox(simulate_frame, from_=1000, to=1000000, increment=1000,
                     textvariable=self.num_draws_var, width=10).pack(side="left", padx=5)

        ttk.Button(simulate_frame, text="开始模拟", command=self.run_simulation).pack(side="left", padx=5)

        # 日志输出
        self.log_output = tk.Text(self, height=10, width=80)
        self.log_output.pack(padx=10, pady=5, fill="both", expand=True)

    def load_ydk_file(self):
        path = filedialog.askopenfilename(filetypes=[("YDK 文件", "*.ydk")])
        if path:
            card_names = self.controller.load_ydk_file(path)
            self.update_deck_preview(card_names)

    def load_ydk_from_clipboard(self):
        try:
            ydk_text = self.clipboard_get()
            card_names = self.controller.load_ydk_file(ydk_text, is_path=False)
            self.update_deck_preview(card_names)
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def export_deck_txt(self):
        try:
            self.controller.export_current_deck()
            messagebox.showinfo("导出完成", "卡组已导出为 TXT")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def load_txt_deck(self):
        path = filedialog.askopenfilename(filetypes=[("TXT 文件", "*.txt")])
        if path:
            self.deck_path_var.set(path)
            try:
                self.controller.load_deck_file(path)  # 替换这一行
                card_names = self.controller.card_pool
                self.update_deck_preview(card_names)
            except Exception as e:
                messagebox.showerror("错误", f"加载卡组失败：{e}")

    def load_conditions(self):
        path = filedialog.askopenfilename(filetypes=[("TXT 文件", "*.txt")])
        if path:
            self.condition_path_var.set(path)
            try:
                # 使用新接口加载条件
                self.controller.load_condition(source=path, is_path=True)

                # 更新 TreeView 显示
                self.condition_tree.delete(*self.condition_tree.get_children())
                for cond in self.controller.condition_data:
                    self.condition_tree.insert("", "end", values=(cond.expression, cond.operator, cond.value))
            except Exception as e:
                messagebox.showerror("错误", f"加载条件失败：{e}")
    def run_simulation(self):
        try:
            prob = self.controller.run_simulation(draw_size=self.draw_size_var.get(), num_draws=self.num_draws_var.get())
            self.log_output.insert(tk.END, f"[RESULT] 满足条件概率：{prob:.2%}\n")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def update_deck_preview(self, card_names):
        self.deck_preview.delete("1.0", tk.END)
        for name in card_names:
            self.deck_preview.insert(tk.END, name + "\n")
