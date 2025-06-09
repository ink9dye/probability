import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from gui.controller import AppController
import threading

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
        deck_frame = ttk.LabelFrame(self, text="加载卡组构筑（.txt）")
        deck_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        self.deck_path_var = tk.StringVar()
        ttk.Entry(deck_frame, textvariable=self.deck_path_var, width=60).pack(side="left", padx=5, pady=5)
        ttk.Button(deck_frame, text="选择 TXT 卡组", command=self.load_txt_deck).pack(side="left", padx=5, pady=5)

        # === 条件加载区域（TXT）===
        condition_frame = ttk.LabelFrame(self, text="加载启动条件（.txt）")
        condition_frame.pack(padx=10, pady=5, fill="x", anchor="w")

        self.condition_path_var = tk.StringVar()
        ttk.Entry(condition_frame, textvariable=self.condition_path_var, width=60).pack(side="left", padx=5, pady=5)
        ttk.Button(condition_frame, text="选择条件文件", command=self.load_conditions).pack(side="left", padx=5, pady=5)

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

        self.progress = ttk.Progressbar(simulate_frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress.pack(side="left", padx=10)

        ttk.Button(simulate_frame, text="开始模拟", command=self.run_simulation_thread).pack(side="left", padx=5)

        # 日志输出
        self.log_output = tk.Text(self, height=30, width=100, font=("Courier New", 10))
        self.log_output.pack(padx=10, pady=5, fill="both", expand=True)

    def load_ydk_file(self):
        path = filedialog.askopenfilename(filetypes=[("YDK 文件", "*.ydk")])
        if path:
            card_names = self.controller.load_ydk_file(path)
            self.log_output.insert(tk.END, f"[INFO] 加载了 {len(card_names)} 张卡牌（卡组码）\n")

    def load_ydk_from_clipboard(self):
        try:
            ydk_text = self.clipboard_get()
            card_names = self.controller.load_ydk_file(ydk_text, is_path=False)
            self.log_output.insert(tk.END, f"[INFO] 从剪贴板加载了 {len(card_names)} 张卡牌（卡组码）\n")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def export_deck_txt(self):
        try:
            self.controller.export_current_deck()
            messagebox.showinfo("导出完成", "卡组码已导出为 TXT 构筑")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def load_txt_deck(self):
        path = filedialog.askopenfilename(filetypes=[("TXT 文件", "*.txt")])
        if path:
            self.deck_path_var.set(path)
            try:
                self.controller.load_deck_txt(path)
                self.log_output.insert(tk.END, f"[INFO] 加载构筑成功，共 {len(self.controller.card_pool)} 张卡牌\n")
            except Exception as e:
                messagebox.showerror("错误", f"加载卡组失败：{e}")

    def load_conditions(self):
        path = filedialog.askopenfilename(filetypes=[("TXT 文件", "*.txt")])
        if path:
            self.condition_path_var.set(path)
            try:
                conditions = self.controller.load_condition_txt(source=path, is_path=True)
                self.log_output.insert(tk.END, f"[INFO] 加载了 {len(conditions)} 条启动条件\n")
            except Exception as e:
                messagebox.showerror("错误", f"加载条件失败：{e}")

    def run_simulation_thread(self):
        thread = threading.Thread(target=self.run_simulation)
        thread.start()

    def run_simulation(self):
        try:
            self.progress.start()
            prob, report = self.controller.run_simulation(
                draw_size=self.draw_size_var.get(),
                num_draws=self.num_draws_var.get(),
                callback=lambda msg: self.log_output.insert(tk.END, msg + "\n")
            )
            self.progress.stop()
            self.log_output.insert(tk.END, f"\n[RESULT] 所有情况的总概率为: {prob:.2%}\n")
            self.log_output.insert(tk.END, report + "\n")
        except Exception as e:
            self.progress.stop()
            messagebox.showerror("错误", str(e))
