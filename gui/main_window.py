import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from app.settings import DECK_DIR, DEFAULT_DECK_PATH, DEFAULT_START_PATH, START_DIR
from gui.facade import AppFacade
from infrastructure.reporters.format import format_simulation_result


class MainWindow(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("YGO 卡组概率计算器")
        self.geometry("880x640")
        self.minsize(720, 520)

        self._facade = AppFacade()
        self._running = False

        self._deck_var = tk.StringVar(value=str(DEFAULT_DECK_PATH))
        self._start_var = tk.StringVar(value=str(DEFAULT_START_PATH))
        self._second_var = tk.BooleanVar(value=False)
        self._ydk_var = tk.BooleanVar(value=False)
        self._dai_man_var = tk.StringVar(value="6")
        self._trials_var = tk.StringVar(value="400000")
        self._seed_var = tk.StringVar(value="")

        self._build_ui()
        self._sync_dai_man_state()

    def _build_ui(self) -> None:
        pad = {"padx": 8, "pady": 4}
        root = ttk.Frame(self, padding=10)
        root.pack(fill=tk.BOTH, expand=True)

        files = ttk.LabelFrame(root, text="文件", padding=8)
        files.pack(fill=tk.X, **pad)
        self._file_row(files, "构筑", self._deck_var, self._pick_deck)
        self._file_row(files, "启动", self._start_var, self._pick_start)

        opts = ttk.LabelFrame(root, text="模拟选项", padding=8)
        opts.pack(fill=tk.X, **pad)

        row1 = ttk.Frame(opts)
        row1.pack(fill=tk.X, pady=2)
        ttk.Checkbutton(row1, text="后手模式", variable=self._second_var).pack(side=tk.LEFT)
        ttk.Checkbutton(row1, text="构筑为 YDK", variable=self._ydk_var).pack(side=tk.LEFT, padx=16)
        ttk.Label(row1, text="怠慢壶 n:").pack(side=tk.LEFT, padx=(16, 4))
        self._dai_man_spin = ttk.Spinbox(row1, from_=1, to=60, width=6, textvariable=self._dai_man_var)
        self._dai_man_spin.pack(side=tk.LEFT)

        row2 = ttk.Frame(opts)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="模拟次数:").pack(side=tk.LEFT)
        ttk.Entry(row2, width=12, textvariable=self._trials_var).pack(side=tk.LEFT, padx=4)
        ttk.Label(row2, text="随机种子(可选):").pack(side=tk.LEFT, padx=(12, 0))
        ttk.Entry(row2, width=12, textvariable=self._seed_var).pack(side=tk.LEFT, padx=4)

        actions = ttk.Frame(root)
        actions.pack(fill=tk.X, **pad)
        self._btn_run = ttk.Button(actions, text="开始模拟", command=self._on_run)
        self._btn_run.pack(side=tk.LEFT)
        ttk.Button(actions, text="YDK → 构筑 txt", command=self._on_export_ydk).pack(side=tk.LEFT, padx=8)
        ttk.Button(actions, text="刷新本地卡库", command=self._on_refresh_db).pack(side=tk.LEFT)

        self._progress = ttk.Progressbar(root, mode="indeterminate")
        self._progress.pack(fill=tk.X, **pad)

        result_frame = ttk.LabelFrame(root, text="结果", padding=4)
        result_frame.pack(fill=tk.BOTH, expand=True, **pad)
        self._output = scrolledtext.ScrolledText(result_frame, wrap=tk.WORD, font=("Consolas", 10))
        self._output.pack(fill=tk.BOTH, expand=True)

        self._status = ttk.Label(root, text="就绪", anchor=tk.W)
        self._status.pack(fill=tk.X, **pad)

        self._deck_var.trace_add("write", lambda *_: self._sync_dai_man_state())
        self._second_var.trace_add("write", lambda *_: self._sync_dai_man_state())

    def _file_row(self, parent, label: str, var: tk.StringVar, cmd) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text=label, width=6).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)
        ttk.Button(row, text="浏览…", command=cmd, width=8).pack(side=tk.LEFT)

    def _pick_deck(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=PROJECT_ROOT,
            title="选择构筑或 YDK",
            filetypes=[("构筑/YDK", "*.txt *.ydk"), ("所有", "*.*")],
        )
        if path:
            self._deck_var.set(path)
            self._ydk_var.set(path.lower().endswith(".ydk"))

    def _pick_start(self) -> None:
        path = filedialog.askopenfilename(
            initialdir=START_DIR,
            title="选择启动条件",
            filetypes=[("文本", "*.txt"), ("所有", "*.*")],
        )
        if path:
            self._start_var.set(path)

    def _sync_dai_man_state(self) -> None:
        path = Path(self._deck_var.get())
        has_pot = False
        if path.exists() and not self._ydk_var.get():
            try:
                has_pot = "怠慢壶" in path.read_text(encoding="utf-8")
            except OSError:
                pass
        state = tk.NORMAL if (has_pot and self._second_var.get()) else tk.DISABLED
        self._dai_man_spin.configure(state=state)

    def _parse_int(self, var: tk.StringVar, default: int | None) -> int | None:
        raw = var.get().strip()
        if not raw:
            return default
        try:
            return int(raw)
        except ValueError:
            return default

    def _on_refresh_db(self) -> None:
        self._facade.refresh_card_db()
        n = len(self._facade.list_field_keywords())
        self._status.config(text=f"本地库已刷新，字段关键词 {n} 个")

    def _on_export_ydk(self) -> None:
        ydk = filedialog.askopenfilename(
            initialdir=PROJECT_ROOT,
            filetypes=[("YDK", "*.ydk"), ("所有", "*.*")],
        )
        if not ydk:
            return
        out = filedialog.asksaveasfilename(
            initialdir=DECK_DIR,
            defaultextension=".txt",
            filetypes=[("构筑 txt", "*.txt")],
        )
        if not out:
            return
        try:
            path = self._facade.export_ydk_txt(ydk, out)
            messagebox.showinfo("完成", f"已导出至\n{path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))

    def _on_run(self) -> None:
        if self._running:
            return
        deck = Path(self._deck_var.get())
        start = Path(self._start_var.get())
        if not deck.exists():
            messagebox.showwarning("提示", "构筑文件不存在")
            return
        if not start.exists():
            messagebox.showwarning("提示", "启动文件不存在")
            return

        dai_man_n = None
        if str(self._dai_man_spin.cget("state")) != str(tk.DISABLED):
            dai_man_n = self._parse_int(self._dai_man_var, 6)

        trials = self._parse_int(self._trials_var, 400_000) or 400_000
        seed = self._parse_int(self._seed_var, None)

        self._running = True
        self._btn_run.configure(state=tk.DISABLED)
        self._progress.start(12)
        self._status.config(text="模拟进行中…")
        self._output.delete("1.0", tk.END)

        def work() -> None:
            try:
                result = self._facade.run_simulation(
                    deck_path=deck,
                    start_path=start,
                    deck_is_ydk=self._ydk_var.get(),
                    going_second=self._second_var.get(),
                    dai_man_pot_n=dai_man_n,
                    trials=trials,
                    seed=seed,
                    print_report=False,
                )
                if result is None:
                    self.after(0, lambda: self._finish_error("无法加载文件或解析失败"))
                else:
                    text = format_simulation_result(result)
                    self.after(0, lambda: self._finish_ok(text))
            except Exception as e:
                self.after(0, lambda: self._finish_error(str(e)))

        threading.Thread(target=work, daemon=True).start()

    def _finish_ok(self, text: str) -> None:
        self._output.insert(tk.END, text)
        self._status.config(text="模拟完成")
        self._run_done()

    def _finish_error(self, msg: str) -> None:
        messagebox.showerror("模拟失败", msg)
        self._status.config(text="失败")
        self._run_done()

    def _run_done(self) -> None:
        self._progress.stop()
        self._btn_run.configure(state=tk.NORMAL)
        self._running = False


def run_app() -> None:
    app = MainWindow()
    app.mainloop()
