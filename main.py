"""
命令行交互入口：在本文件顶部选择构筑与启动，再运行。
"""

from pathlib import Path

from cli.legacy import run_interactive

# --- 在此选择本次要用的文件 ---
DECK_PATH = Path("构筑/41卡魔法师均构筑.txt")
START_PATH = Path("启动/魔法师均启动.txt")

if __name__ == "__main__":
    raise SystemExit(run_interactive(DECK_PATH, START_PATH))
