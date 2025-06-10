# gui/frames/main_frame.py

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QApplication, QHBoxLayout, QGroupBox, QPushButton,
    QLineEdit, QLabel, QSpinBox, QProgressBar, QTextEdit, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from PySide6.QtGui import QClipboard
from config.settings import CONDITION_DIR, DECK_DIR


# ✅ 模拟任务类：封装运行逻辑
class SimulationWorker(QObject):
    log_signal = Signal(str)
    result_ready = Signal(float, str)
    finished = Signal()

    def __init__(self, controller, draw_size, num_draws):
        super().__init__()
        self.controller = controller
        self.draw_size = draw_size
        self.num_draws = num_draws

    def run(self):
        try:
            def callback(msg):
                self.log_signal.emit(msg)

            prob, report = self.controller.run_simulation(
                draw_size=self.draw_size,
                num_draws=self.num_draws,
                callback=callback
            )
            self.result_ready.emit(prob, report)
        except Exception as e:
            self.log_signal.emit(f"[ERROR] {e}")
        finally:
            self.finished.emit()


# ✅ 主界面类
class MainFrame(QWidget):
    def __init__(self, parent=None, controller=None):
        super().__init__(parent)
        self.controller = controller

        self.deck_path = ""
        self.condition_path = ""

        self.init_ui()
        self.connect_signals()

    def init_ui(self):
        main_layout = QVBoxLayout()

        ydk_group = self.create_ydk_group()
        main_layout.addWidget(ydk_group)

        deck_group = self.create_deck_group()
        main_layout.addWidget(deck_group)

        condition_group = self.create_condition_group()
        main_layout.addWidget(condition_group)

        simulate_group = self.create_simulation_group()
        main_layout.addWidget(simulate_group)

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
        self.btn_load_ydk.clicked.connect(self.load_ydk_file)
        self.btn_export_txt.clicked.connect(self.export_deck_txt)
        self.btn_select_deck.clicked.connect(self.load_txt_deck)
        self.btn_select_condition.clicked.connect(self.load_conditions)
        self.btn_start_simulate.clicked.connect(self.run_simulation)

    def load_ydk_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 YDK 文件", "", "YDK 文件 (*.ydk)")
        if not path:
            return

        try:
            card_names = self.controller.load_ydk(path)
            self.ydk_input.setPlainText(path)
            self.log_output.append(f"[INFO] 加载了 {len(card_names)} 张卡牌（卡组码）\n")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载 YDK 文件失败: {e}")

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
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def load_txt_deck(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "选择卡组文件", DECK_DIR, "文本文件 (*.txt)"
        )
        if path:
            self.deck_path = path
            self.deck_path_edit.setText(path)
            try:
                self.controller.load_deck_txt(source=path, is_path=True)
                self.log_output.append(f"[INFO] 加载构筑成功，共 {len(self.controller.card_pool)} 张卡牌\n")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载卡组失败：{e}")

    def load_conditions(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择条件文件",
            CONDITION_DIR,
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

    def run_simulation(self):
        # 禁用按钮防止重复点击
        self.btn_start_simulate.setEnabled(False)
        self.progress_bar.setMaximum(0)  # 设置为忙碌状态

        # 创建线程和工作对象
        self.thread = QThread()
        self.worker = SimulationWorker(
            self.controller,
            draw_size=self.draw_size_spin.value(),
            num_draws=self.num_draws_spin.value()
        )

        # 移动到线程中
        self.worker.moveToThread(self.thread)

        # 连接信号
        self.thread.started.connect(self.worker.run)
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # 启动线程
        self.thread.start()

    def handle_result(self, prob, report):
        self.log_output.append(f"\n[RESULT] 所有情况的总概率为: {prob:.2%}\n")
        self.log_output.append(report + "\n")

    def on_simulation_finished(self):
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.btn_start_simulate.setEnabled(True)
