# main.py

import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def main():
    """
    应用程序主入口。
    初始化 Qt 应用、主窗口，并进入主事件循环。
    """
    app = QApplication(sys.argv)

    app.setApplicationName("游戏王卡组模拟器")
    app.setOrganizationName("YGO Simulator Team")

    # 创建主窗口并显示
    main_window = MainWindow()
    main_window.show()

    # 进入主事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
