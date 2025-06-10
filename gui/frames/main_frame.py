from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QPushButton,
    QLineEdit, QLabel, QSpinBox, QProgressBar, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QClipboard
from config.settings import CONDITION_DIR, DECK_DIR

class MainFrame(QWidget):
    """
    模拟器主界面，集成卡组导入、条件加载、模拟执行等功能模块。
    """
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller  # 控制器对象：负责调用后端逻辑

        self.deck_path = ""       # 当前选择的卡组文件路径
        self.condition_path = ""  # 当前选择的条件文件路径

        self.init_ui()            # 初始化界面布局
        self.connect_signals()    # 绑定各按钮的信号与槽函数

    def init_ui(self):
        """
        构建主界面的 UI 结构，分为多个 GroupBox 模块。
        """
        main_layout = QVBoxLayout()

        # 卡组码导入功能（.ydk -> 内存卡组）
        ydk_group = self.create_ydk_group()
        main_layout.addWidget(ydk_group)

        # 构筑文件加载（.txt）
        deck_group = self.create_deck_group()
        main_layout.addWidget(deck_group)

        # 启动条件文件加载（.txt）
        condition_group = self.create_condition_group()
        main_layout.addWidget(condition_group)

        # 模拟执行设置区域
        simulate_group = self.create_simulation_group()
        main_layout.addWidget(simulate_group)

        # 日志输出框（只读）
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        self.setLayout(main_layout)

    def create_ydk_group(self):
        group_box = QGroupBox("导入卡组码（.ydk）")
        layout = QHBoxLayout()

        self.btn_load_ydk = QPushButton("选择 YDK 文件")
        self.ydk_input = QTextEdit()  # 新增：允许用户手动粘贴 YDK 内容
        self.ydk_input.setPlaceholderText("在此处粘贴 YDK 格式内容")

        self.btn_export_txt = QPushButton("导出为 TXT 卡组")

        layout.addWidget(self.btn_load_ydk)
        layout.addWidget(self.ydk_input, stretch=3)
        layout.addWidget(self.btn_export_txt)

        group_box.setLayout(layout)
        return group_box

    def create_deck_group(self):
        """
        创建 TXT 卡组加载区域。
        """
        group_box = QGroupBox("加载卡组构筑（.txt）")
        layout = QHBoxLayout()

        self.deck_path_edit = QLineEdit()
        self.deck_path_edit.setPlaceholderText("卡组文件路径")
        self.btn_select_deck = QPushButton("选择 TXT 卡组")

        layout.addWidget(self.deck_path_edit, stretch=3)
        layout.addWidget(self.btn_select_deck)

        group_box.setLayout(layout)
        return group_box

    def create_condition_group(self):
        """
        创建条件文件加载区域。
        """
        group_box = QGroupBox("加载启动条件（.txt）")
        layout = QHBoxLayout()

        self.condition_path_edit = QLineEdit()
        self.condition_path_edit.setPlaceholderText("条件文件路径")
        self.btn_select_condition = QPushButton("选择条件文件")

        layout.addWidget(self.condition_path_edit, stretch=3)
        layout.addWidget(self.btn_select_condition)

        group_box.setLayout(layout)
        return group_box

    def create_simulation_group(self):
        """
        创建模拟设置和运行按钮区域。
        """
        group_box = QGroupBox("模拟设置")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("抽卡数:"))
        self.draw_size_spin = QSpinBox()
        self.draw_size_spin.setRange(1, 10)
        self.draw_size_spin.setValue(5)
        layout.addWidget(self.draw_size_spin)

        layout.addWidget(QLabel("模拟次数:"))
        self.num_draws_spin = QSpinBox()
        self.num_draws_spin.setRange(1000, 1000000)
        self.num_draws_spin.setSingleStep(1000)
        self.num_draws_spin.setValue(100000)
        layout.addWidget(self.num_draws_spin)

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)

        self.btn_start_simulate = QPushButton("开始模拟")
        layout.addWidget(self.btn_start_simulate)

        group_box.setLayout(layout)
        return group_box

    def connect_signals(self):
        """
        将界面组件的信号连接到对应的槽函数（控制逻辑）。
        """
        self.btn_load_ydk.clicked.connect(self.load_ydk_file)
        self.btn_export_txt.clicked.connect(self.export_deck_txt)
        self.btn_select_deck.clicked.connect(self.load_txt_deck)
        self.btn_select_condition.clicked.connect(self.load_conditions)
        self.btn_start_simulate.clicked.connect(self.run_simulation_thread)

    def load_ydk_file(self):
        """
        通过文件对话框选择 YDK 文件并加载，同时显示文件内容到文本框。
        """
        path, _ = QFileDialog.getOpenFileName(self, "选择 YDK 文件", "", "YDK 文件 (*.ydk)")
        if not path:
            return

        try:
            # 读取文件内容
            with open(path, 'r', encoding='utf-8') as f:
                ydk_content = f.read()

            # 显示到文本框中
            self.ydk_input.setPlainText(ydk_content)

            # 调用控制器加载卡组
            card_names = self.controller.load_ydk(path)
            self.log_output.append(f"[INFO] 加载了 {len(card_names)} 张卡牌（卡组码）\n")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 YDK 文件失败: {e}")

    def load_ydk_from_clipboard(self):
        try:
            ydk_text = self.ydk_input.toPlainText().strip()
            if not ydk_text:
                raise ValueError("请输入或粘贴 YDK 内容后再加载")

            card_names = self.controller.load_ydk(ydk_text, is_path=False)
            self.log_output.append(f"[INFO] 从文本框加载了 {len(card_names)} 张卡牌（卡组码）\n")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def export_deck_txt(self):
        try:
            ydk_text = self.ydk_input.toPlainText().strip()
            if ydk_text:
                card_names = self.controller.load_ydk(ydk_text, is_path=False)
                if not card_names:
                    raise ValueError("YDK 内容解析成功但返回空列表，请检查数据库状态")

            if not self.controller.card_pool:
                raise ValueError("当前卡组为空，无法导出")

            self.controller.export_current_deck()
            # QMessageBox.information(self, "导出完成", "卡组码已导出为 TXT 构筑")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def load_txt_deck(self):
        """
        加载 TXT 格式的卡组构筑文件。
        """
        path, _ = QFileDialog.getOpenFileName(self, "选择卡组文件",DECK_DIR, "文本文件 (*.txt)")
        if path:
            self.deck_path = path
            self.deck_path_edit.setText(path)
            try:
                self.controller.load_deck_txt(path)
                self.log_output.append(f"[INFO] 加载构筑成功，共 {len(self.controller.card_pool)} 张卡牌\n")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载卡组失败：{e}")

    def load_conditions(self):
        """
        加载 TXT 条件文件（用于模拟条件）。
        """
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择条件文件",
            CONDITION_DIR,  # 设置默认打开路径为 settings 中定义的条件目录
            "文本文件 (*.txt)"
        )
        if path:
            self.condition_path = path
            self.condition_path_edit.setText(path)
            try:
                conditions = self.controller.load_condition_txt(source=path, is_path=True)
                self.log_output.append(f"[INFO] 加载了 {len(conditions)} 条启动条件\n")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载条件失败：{e}")

    def run_simulation_thread(self):
        """
        使用后台线程运行模拟，避免阻塞主线程。
        """
        from threading import Thread
        thread = Thread(target=self.run_simulation)
        thread.start()

    def run_simulation(self):
        """
        执行模拟操作，计算概率并输出日志。
        """
        try:
            self.progress_bar.setMaximum(0)  # 设置为不确定模式（忙碌状态）
            prob, report = self.controller.run_simulation(
                draw_size=self.draw_size_spin.value(),
                num_draws=self.num_draws_spin.value(),
                callback=lambda msg: self.log_output.append(msg)
            )
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            self.log_output.append(f"\n[RESULT] 所有情况的总概率为: {prob:.2%}\n")
            self.log_output.append(report + "\n")
        except Exception as e:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(0)
            QMessageBox.critical(self, "错误", str(e))
