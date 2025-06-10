from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QMessageBox, QMenu
)
from PySide6.QtCore import Qt, QPoint
from gui.widgets.strategy_item_widget import StrategyItemWidget


class StrategyEditorFrame(QWidget):
    def __init__(self, controller=None, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.strategy_widgets = []

        self.init_ui()
        self.load_strategies()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # 滚动区域设置为卡片样式布局
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setAlignment(Qt.AlignTop)

        scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(scroll_area)

    def show_context_menu_for_widget(self, widget, pos: QPoint):
        menu = QMenu(widget)
        action_delete = menu.addAction("删除该策略")
        action = menu.exec_(widget.mapToGlobal(pos))
        if action == action_delete:
            self.delete_specific_strategy(widget)

    def load_strategies(self):
        """加载并展示策略"""
        strategies = self.controller.get_all_strategies().values()
        self.clear_strategy_widgets()

        for strategy in sorted(strategies, key=lambda s: s.priority):
            widget = StrategyItemWidget(strategy)
            widget.setContextMenuPolicy(Qt.CustomContextMenu)
            widget.customContextMenuRequested.connect(
                lambda pos, w=widget: self.show_context_menu_for_widget(w, pos)
            )
            self.scroll_layout.addWidget(widget)
            self.strategy_widgets.append(widget)

    def create_new_strategy(self):
        from core.entity.strategy import Strategy

        new_strategy = Strategy(
            name=f"新策略_{len(self.strategy_widgets)+1}",
            description="",
            condition_func=lambda hand, pool: False,
            action_func=lambda hand, pool: hand,
            enabled=False,
        )
        self.controller.add_strategy(new_strategy)
        widget = StrategyItemWidget(new_strategy)
        widget.setContextMenuPolicy(Qt.CustomContextMenu)
        widget.customContextMenuRequested.connect(
            lambda pos, w=widget: self.show_context_menu_for_widget(w, pos)
        )
        self.scroll_layout.addWidget(widget)
        self.strategy_widgets.append(widget)

    def delete_specific_strategy(self, widget):
        if widget in self.strategy_widgets:
            self.strategy_widgets.remove(widget)
            name = widget.strategy.name
            self.controller.delete_strategy(name)
            widget.setParent(None)
            widget.deleteLater()

    def delete_selected_strategy(self):
        """删除最后一个策略"""
        if not self.strategy_widgets:
            return
        widget = self.strategy_widgets.pop()
        name = widget.strategy.name
        self.controller.delete_strategy(name)
        widget.setParent(None)
        widget.deleteLater()

    def clear_strategy_widgets(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.strategy_widgets.clear()
