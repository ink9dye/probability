from PySide6.QtWidgets import QMainWindow, QTabWidget, QMenuBar, QMenu, QMessageBox
from PySide6.QtGui import QAction
from gui.controller import AppController
from gui.frames.main_frame import MainFrame
from gui.frames.card_editor_frame import CardEditorFrame

class MainWindow(QMainWindow):
    """
    游戏王卡组模拟器的主窗口类，包含主界面和字段管理界面，并集成了菜单栏和控制器。
    """
    def __init__(self):
        """
        初始化主窗口，设置窗口标题和尺寸，创建控制器、Tab页面和菜单栏。
        """
        super().__init__()

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
        self.notebook.addTab(self.main_frame, "模拟器")

        # 创建并添加字段管理页面（卡片属性编辑）
        self.card_editor_frame = CardEditorFrame(controller=self.controller)
        self.notebook.addTab(self.card_editor_frame, "字段管理")

        # 创建顶部菜单栏
        self.create_menu_bar()

    def create_menu_bar(self):
        """
        创建顶部菜单栏，包括文件菜单与相关操作。
        """
        menu_bar = self.menuBar()  # 获取菜单栏对象

        # 创建文件菜单
        file_menu: QMenu = menu_bar.addMenu("文件")

        # 添加“刷新数据库”菜单项
        refresh_action = QAction("刷新数据库", self)
        refresh_action.triggered.connect(self.refresh_database)  # 绑定刷新操作
        file_menu.addAction(refresh_action)

        # 添加“字段管理”菜单项（跳转字段管理Tab）
        open_editor_action = QAction("字段管理", self)
        open_editor_action.triggered.connect(self.show_card_editor)
        file_menu.addAction(open_editor_action)

        # 添加分隔线
        file_menu.addSeparator()

        # 添加“退出”菜单项
        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def refresh_database(self):
        """
        调用控制器刷新本地数据库，并显示消息框反馈操作结果。
        """
        try:
            self.controller.refresh_local_db()
            QMessageBox.information(self, "提示", "数据库刷新成功")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新失败: {e}")

    def show_card_editor(self):
        """
        显示字段管理页面（切换到 card_editor_frame）。
        """
        self.notebook.setCurrentWidget(self.card_editor_frame)
