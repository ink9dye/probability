# main_frame.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QPushButton,
    QLineEdit, QLabel, QSpinBox, QProgressBar, QTextEdit, QFileDialog,
    QMessageBox, QInputDialog, QListWidget, QCheckBox
)
from PySide6.QtCore import Qt, Signal, QObject, QThread
from config.settings import DECK_DIR, CONDITION_DIR
from PySide6.QtCore import Slot

class SimulationWorker(QObject):
    log_signal = Signal(str)
    result_ready = Signal(float, str)
    finished = Signal()

    def __init__(self, controller, draw_size, num_draws, snapshot_interval):
        super().__init__()
        self.controller = controller
        self.draw_size = draw_size
        self.num_draws = num_draws
        self.snapshot_interval = snapshot_interval

    def run(self):
        try:
            def callback(msg):
                self.log_signal.emit(msg)

            prob, report = self.controller.run_simulation(
                draw_size=self.draw_size,
                num_draws=self.num_draws,
                snapshot_interval=self.snapshot_interval,
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

        # 金满壶
        self.chk_jinman = QCheckBox("启用金满壶策略")
        jinman_layout = QHBoxLayout()
        self.spin_jinman_count = QSpinBox()
        self.spin_jinman_count.setRange(1, 3)
        self.spin_jinman_count.setValue(2)
        jinman_layout.addWidget(QLabel("抽取张数:"))
        jinman_layout.addWidget(self.spin_jinman_count)

        layout.addWidget(self.chk_jinman)
        layout.addLayout(jinman_layout)

        # 金谦壶
        self.chk_jinqian = QCheckBox("启用金谦壶策略")
        jinqian_layout = QHBoxLayout()
        self.spin_jinqian_count = QSpinBox()
        self.spin_jinqian_count.setRange(1, 6)
        self.spin_jinqian_count.setValue(3)
        self.jinqian_fields = QLineEdit()
        self.jinqian_fields.setPlaceholderText("字段优先级（英文逗号分隔）")
        jinqian_layout.addWidget(QLabel("选取张数:"))
        jinqian_layout.addWidget(self.spin_jinqian_count)
        jinqian_layout.addWidget(QLabel("字段优先级:"))
        jinqian_layout.addWidget(self.jinqian_fields)

        layout.addWidget(self.chk_jinqian)
        layout.addLayout(jinqian_layout)

        # 类暗抽
        self.chk_dark_draw = QCheckBox("启用类暗抽策略")

        dark_group = QGroupBox("暗抽配置")
        dark_layout = QHBoxLayout()

        self.dark_draw_trigger_card = QLineEdit()
        self.dark_draw_trigger_card.setPlaceholderText("如：暗之诱惑")

        self.dark_draw_required_field = QLineEdit()
        self.dark_draw_required_field.setPlaceholderText("如：暗属性")

        dark_layout.addWidget(QLabel("触发卡名:"))
        dark_layout.addWidget(self.dark_draw_trigger_card)
        dark_layout.addWidget(QLabel("所需字段:"))
        dark_layout.addWidget(self.dark_draw_required_field)

        dark_group.setLayout(dark_layout)
        layout.addWidget(self.chk_dark_draw)
        layout.addWidget(dark_group)

        group_box.setLayout(layout)
        return group_box

    def create_simulation_settings_group(self):
        group_box = QGroupBox("模拟与输出")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("抽卡张数"))
        self.draw_size_spin = QSpinBox()
        self.draw_size_spin.setValue(5)  # 固定默认值
        layout.addWidget(self.draw_size_spin)

        layout.addWidget(QLabel("模拟次数"))
        self.num_draws_spin = QSpinBox()
        self.num_draws_spin.setRange(1, 10000)
        self.num_draws_spin.setValue(10000)  # 固定默认值
        layout.addWidget(self.num_draws_spin)

        layout.addWidget(QLabel("快照间隔"))
        self.snapshot_interval_spin = QSpinBox()
        self.snapshot_interval_spin.setRange(1, 10000)
        self.snapshot_interval_spin.setValue(2000)  # ✅ 默认值保持不变
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
        if not path:
            return

        try:
            from utils.file_utils import read_from_file
            ydk_text = read_from_file(path)
            self.ydk_input.setPlainText(ydk_text)
            self.log_output.append("[INFO] 已加载 YDK 文件内容（原始文本）")

        except Exception as e:
            QMessageBox.critical(self, "加载失败", f"无法读取 YDK 文件: {e}")

    def export_deck_txt(self):
        ydk_text = self.ydk_input.toPlainText().strip()
        if not ydk_text:
            self.controller._show_error("导出失败", "文本框为空")
            return

        try:
            default_name = "刻魔莫忘构筑"
            file_name, ok = QInputDialog.getText(
                self, "导出 TXT 卡组", "请输入文件名（不含扩展名）：", text=default_name
            )
            if not ok or not file_name:
                return

            full_file_name = f"{file_name}.txt"

            self.controller.export_current_deck_with_ydk(ydk_content=ydk_text, file_name=full_file_name)

        except Exception as e:
            self.controller._show_error("导出失败", str(e))

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

    @Slot(str)
    def append_log(self, msg):
        self.log_output.append(msg)

    def run_simulation(self):
        self.btn_start_simulate.setEnabled(False)
        self.log_output.clear()
        self.log_output.append("[INFO] 开始模拟...")

        strategy_dict = {
            'golden_manhu_enabled': self.chk_jinman.isChecked(),
            'golden_manhu_draw_count': self.spin_jinman_count.value(),

            'golden_qianhu_enabled': self.chk_jinqian.isChecked(),
            'golden_qianhu_priority_fields': [f.strip() for f in self.jinqian_fields.text().split(',') if f.strip()],
            'golden_qianhu_draw_count': self.spin_jinqian_count.value(),

            'dark_draw_enabled': self.chk_dark_draw.isChecked(),
            'dark_draw_trigger_card': self.dark_draw_trigger_card.text().strip() or "暗之诱惑",
            'dark_draw_required_field': self.dark_draw_required_field.text().strip() or "暗属性"
        }

        self.controller.set_strategy_config([strategy_dict])

        self.worker = SimulationWorker(
            controller=self.controller,
            draw_size=self.draw_size_spin.value(),
            num_draws=self.num_draws_spin.value(),
            snapshot_interval=self.snapshot_interval_spin.value()
        )

        self.thread = QThread()
        self.worker.moveToThread(self.thread)



        # 替换之前的 connect
        self.worker.log_signal.connect(self.append_log)

        self.worker.result_ready.connect(self.handle_result)
        self.worker.finished.connect(self.on_simulation_finished)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def handle_result(self, prob, report):
        self.log_output.append(f"[RESULT] 所有情况的总概率为: {prob:.2%}\n")
        self.log_output.append(report)

    def on_simulation_finished(self):
        self.btn_start_simulate.setEnabled(True)
