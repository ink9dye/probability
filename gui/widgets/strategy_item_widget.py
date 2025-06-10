# gui/widgets/strategy_item_widget.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox,
    QLineEdit, QSpinBox, QCheckBox
)
from PySide6.QtCore import Qt


class StrategyItemWidget(QWidget):
    def __init__(self, strategy, parent=None):
        super().__init__(parent)
        self.strategy = strategy

        layout = QHBoxLayout()

        # 启用状态勾选框
        self.enable_checkbox = QCheckBox()
        self.enable_checkbox.setChecked(strategy.enabled)
        self.enable_checkbox.stateChanged.connect(self.on_enable_changed)
        layout.addWidget(self.enable_checkbox)

        # 内容区域
        info_layout = QVBoxLayout()
        self.name_label = QLabel(f"{strategy.name} (priority: {strategy.priority})")
        info_layout.addWidget(self.name_label)

        # 动态添加参数控件
        self.param_widgets = {}

        if hasattr(strategy, "draw_count"):
            self.draw_count_combo = QComboBox()
            self.draw_count_combo.addItems(["1", "2", "3", "4", "5", "6"])
            self.draw_count_combo.setCurrentText(str(getattr(strategy, "draw_count", 2)))
            self.draw_count_combo.currentTextChanged.connect(self.on_draw_count_changed)
            self.param_widgets["draw_count"] = self.draw_count_combo
            info_layout.addWidget(QLabel("抽卡张数："))
            info_layout.addWidget(self.draw_count_combo)

        if hasattr(strategy, "priority_fields"):
            self.priority_field_edit = QLineEdit(", ".join(strategy.priority_fields))
            self.priority_field_edit.textChanged.connect(self.on_priority_fields_changed)
            self.param_widgets["priority_fields"] = self.priority_field_edit
            info_layout.addWidget(QLabel("优先字段："))
            info_layout.addWidget(self.priority_field_edit)

        if hasattr(strategy, "required_cards"):
            self.keyword_edit = QLineEdit(", ".join(strategy.required_cards))
            self.keyword_edit.textChanged.connect(self.on_keyword_changed)
            self.param_widgets["keywords"] = self.keyword_edit
            info_layout.addWidget(QLabel("关键词："))
            info_layout.addWidget(self.keyword_edit)

        if hasattr(strategy, "required_count"):
            self.count_spin = QSpinBox()
            self.count_spin.setRange(1, 10)
            self.count_spin.setValue(strategy.required_count)
            self.count_spin.valueChanged.connect(self.on_count_changed)
            self.param_widgets["count"] = self.count_spin
            info_layout.addWidget(QLabel("数量："))
            info_layout.addWidget(self.count_spin)

        layout.addLayout(info_layout)
        self.setLayout(layout)

    def on_enable_changed(self, state):
        self.strategy.enabled = state == Qt.Checked

    def on_draw_count_changed(self, value):
        if hasattr(self.strategy, "draw_count"):
            self.strategy.draw_count = int(value)

    def on_priority_fields_changed(self, text):
        if hasattr(self.strategy, "priority_fields"):
            self.strategy.priority_fields = [x.strip() for x in text.split(",")]

    def on_keyword_changed(self, text):
        if hasattr(self.strategy, "required_cards"):
            self.strategy.required_cards = [x.strip() for x in text.split(",")]

    def on_count_changed(self, value):
        if hasattr(self.strategy, "required_count"):
            self.strategy.required_count = value
