from PySide6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction
from gui.controller import AppController
from gui.frames.main_frame import MainFrame
from gui.frames.card_editor_frame import CardEditorFrame
from gui.frames.condition_editor_frame import ConditionEditorFrame
from gui.frames.deck_editor_frame import DeckEditorFrame
from gui.frames.strategy_editor_frame import StrategyEditorFrame


class MainWindow(QMainWindow):
    """
    游戏王卡组模拟器的主窗口类，包含主界面和字段管理界面，并集成了菜单栏和控制器。
    """
    def __init__(self):
        """
        初始化主窗口，设置窗口标题和尺寸，创建控制器、Tab页面和菜单栏。
        """
        super().__init__()
        ExceptionCatcher.install()
        # 设置窗口标题和初始尺寸
        self.setWindowTitle("游戏王卡组模拟器")
        self.setGeometry(300, 200, 1100, 750)

        # 初始化控制器（业务逻辑层）
        self.controller = AppController(self)

        # 创建中心控件：选项卡容器
        self.notebook = QTabWidget()
        self.setCentralWidget(self.notebook)

        # 创建并添加主功能页面（模拟器界面）
        self.main_frame = MainFrame(controller=self.controller)
        self.notebook.addTab(self.main_frame, "计算器")

        # 创建并添加字段管理页面（卡片属性编辑）
        self.card_editor_frame = CardEditorFrame(controller=self.controller)
        self.notebook.addTab(self.card_editor_frame, "本地卡片数据库")

        # 创建并添加字段管理页面（卡片属性编辑）
        self.condition_editor_frame = ConditionEditorFrame(controller=self.controller)
        self.notebook.addTab(self.condition_editor_frame, "条件文件管理")

        self.deck_editor_frame = DeckEditorFrame(controller=self.controller)
        self.notebook.addTab(self.deck_editor_frame, "卡组文件管理")



        # 创建菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("文件")
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(
            lambda: QMessageBox.about(self, "关于", "游戏王卡组模拟器 v1.0\n© 墨水"))
        help_menu.addAction(about_action)





import sys
import traceback

class ExceptionCatcher:
    """
    全局异常处理器，用于捕捉未处理的异常并输出堆栈信息。
    """

    @staticmethod
    def install():
        sys.excepthook = ExceptionCatcher.handle_exception

    @staticmethod
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        print("=== 捕获未处理异常 ===")
        print("类型:", exc_type)
        print("内容:", exc_value)
        traceback.print_tb(exc_traceback)
