from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QPushButton,
    QLineEdit, QLabel, QSpinBox, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QListWidget, QCheckBox, QTextEdit
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from config.settings import CONDITION_DIR, DECK_DIR


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
        grid = QGridLayout()

        grid.addWidget(self.create_ydk_group(), 0, 0)
        grid.addWidget(self.create_deck_group(), 1, 0)
        grid.addWidget(self.create_condition_group(), 2, 0)
        grid.addWidget(self.create_strategy_settings_group(), 0, 1, 3, 1)

        main_layout.addLayout(grid)
        main_layout.addWidget(self.create_simulation_settings_group())

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        main_layout.addWidget(self.log_output)

        self.setLayout(main_layout)

    def create_ydk_group(self):
        group_box = QGroupBox("导入卡组码（.ydk）")
        layout = QHBoxLayout()

        self.btn_load_ydk = QPushButton("选择 YDK 文件")
        self.ydk_input = QTextEdit()
        self.ydk_input.setPlaceholderText("在此处粘贴 YDK 格式内容")
        self.btn_export_txt = QPushButton("导出为 TXT 卡组")

        layout.addWidget(self.btn_load_ydk)
        layout.addWidget(self.ydk_input, stretch=3)
        layout.addWidget(self.btn_export_txt)

        group_box.setLayout(layout)
        return group_box

    def create_deck_group(self):
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
        group_box = QGroupBox("加载启动条件（.txt）")
        layout = QHBoxLayout()

        self.condition_path_edit = QLineEdit()
        self.condition_path_edit.setPlaceholderText("条件文件路径")
        self.btn_select_condition = QPushButton("选择条件文件")

        layout.addWidget(self.condition_path_edit, stretch=3)
        layout.addWidget(self.btn_select_condition)

        group_box.setLayout(layout)
        return group_box

    def create_strategy_settings_group(self):
        group_box = QGroupBox("策略与规则设置")
        layout = QVBoxLayout()

        self.chk_jinman = QCheckBox("金满表")
        self.chk_priority = QCheckBox("优先级置")

        self.chk_draw_times = QCheckBox("抽取次数")
        self.spin_draw_times = QSpinBox()
        self.spin_draw_times.setRange(1, 20)
        self.spin_draw_times.setValue(6)

        draw_layout = QHBoxLayout()
        draw_layout.addWidget(self.chk_draw_times)
        draw_layout.addWidget(self.spin_draw_times)

        self.chk_blind = QCheckBox("踢名")
        self.chk_self_activate = QCheckBox("自奏启动(主音≥1 & 自奏≥2)")
        self.chk_tune = QCheckBox("帖抽(帖抽≥1 & 帖属性≥2)")

        layout.addWidget(self.chk_jinman)
        layout.addWidget(self.chk_priority)
        layout.addLayout(draw_layout)
        layout.addWidget(self.chk_blind)
        layout.addWidget(self.chk_self_activate)
        layout.addWidget(self.chk_tune)

        group_box.setLayout(layout)
        return group_box

    def create_simulation_settings_group(self):
        group_box = QGroupBox("模拟与输出")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("抽卡张数"))
        self.draw_size_spin = QSpinBox()
        self.draw_size_spin.setValue(5)
        layout.addWidget(self.draw_size_spin)

        layout.addWidget(QLabel("模拟次数"))
        self.num_draws_spin = QSpinBox()
        self.num_draws_spin.setRange(1000, 1000000)
        self.num_draws_spin.setValue(100000)
        layout.addWidget(self.num_draws_spin)

        layout.addWidget(QLabel("快照间隔"))
        self.snapshot_interval_spin = QSpinBox()
        self.snapshot_interval_spin.setRange(1000, 1000000)
        self.snapshot_interval_spin.setValue(20000)
        layout.addWidget(self.snapshot_interval_spin)

        self.btn_start_simulate = QPushButton("开始模拟")
        layout.addWidget(self.btn_start_simulate)

        group_box.setLayout(layout)
        return group_box

    def connect_signals(self):
        self.btn_start_simulate.clicked.connect(self.run_simulation)
        self.btn_load_ydk.clicked.connect(self.load_ydk_file)
        self.btn_export_txt.clicked.connect(self.export_deck_txt)
        self.btn_select_deck.clicked.connect(self.load_txt_deck)
        self.btn_select_condition.clicked.connect(self.load_conditions)

    def load_ydk_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择 YDK 文件", "", "YDK 文件 (*.ydk)")
        if path:
            card_names = self.controller.load_ydk(path)
            self.ydk_input.setPlainText(path)
            self.log_output.append(f"[INFO] 加载了 {len(card_names)} 张卡牌（卡组码）\n")

    def export_deck_txt(self):
        ydk_text = self.ydk_input.toPlainText().strip()
        if ydk_text:
            card_names = self.controller.load_ydk(ydk_text, is_path=False)
            if not card_names:
                raise ValueError("YDK 内容为空或解析失败")

        self.controller.export_current_deck()

    def load_txt_deck(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择卡组文件", DECK_DIR, "文本文件 (*.txt)")
        if path:
            self.deck_path = path
            self.deck_path_edit.setText(path)
            self.controller.load_deck_txt(source=path, is_path=True)
            self.log_output.append(f"[INFO] 加载构筑成功，共 {len(self.controller.card_pool)} 张卡牌\n")

    def load_conditions(self):
        path, _ = QFileDialog.getOpenFileName(self, "选择条件文件", CONDITION_DIR, "文本文件 (*.txt)")
        if path:
            self.condition_path = path
            self.condition_path_edit.setText(path)
            conditions = self.controller.load_condition_txt(source=path, is_path=True)
            self.log_output.append(f"[INFO] 加载了 {len(conditions)} 条启动条件\n")

    def run_simulation(self):
        self.btn_start_simulate.setEnabled(False)

        self.thread = QThread()
        self.worker = SimulationWorker(
            self.controller,
            draw_size=self.draw_size_spin.value(),
            num_draws=self.num_draws_spin.value()
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.log_signal.connect(self.log_output.append)
        self.worker.result_ready.connect(self.handle_result)
        self.worker.finished.connect(self.on_simulation_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_result(self, prob, report):
        self.log_output.append(f"\n[RESULT] 所有情况的总概率为: {prob:.2%}\n")
        self.log_output.append(report + "\n")

    def on_simulation_finished(self):
        self.btn_start_simulate.setEnabled(True)
