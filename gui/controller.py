# gui/controller.py

import os
from PySide6.QtWidgets import QMessageBox, QFileDialog
from PySide6.QtWidgets import QInputDialog

# ✅ 替换 parser_service 导入为 file_service
from services.file_service import load_file, export_data, save_ydk
from services.simulation_service import run_simulation as service_run_simulation
from services.ydk_service import load_ydk_file, export_to_txt
from services.local_db_service import get_local_db

from typing import List, Union, Dict, Tuple, Set

from config.settings import DECK_DIR, CONDITION_DIR


class AppController:
    def __init__(self, main_window=None):
        """
        控制器构造函数。
        :param main_window: 主窗口对象，用于显示对话框。
        """
        self.main_window = main_window
        self.card_pool: List[str] = []  # 当前加载的卡组中的卡名列表
        self.condition_data = []       # 当前加载的模拟条件数据
        self.titles = []               # 条件对应的标题（列名）
        self.db = get_local_db()       # 本地数据库服务实例

    # ✅ 加载 YDK 文件或文本
    def load_ydk(self, source: Union[str, os.PathLike], is_path: bool = True, field_tag: str = None) -> List[str]:
        """
        从 YDK 文件或文本加载卡牌名称。
        :param source: 文件路径或 YDK 文本内容
        :param is_path: 是否为文件路径（默认是）
        :param field_tag: 用于过滤的字段标签（可选）
        :return: 加载出的卡牌名称列表
        """
        try:
            # 直接传递给服务层处理，由它决定是否读取文件
            card_names = load_ydk_file(source=source, is_path=is_path, field_tag=field_tag)
            self.card_pool = card_names
            print("控制器：加载后的 card_pool:", self.card_pool)  # 调试输出
            print(f"控制器：路径是否：{is_path}")
            return card_names
        except Exception as e:
            raise RuntimeError(f"加载 YDK 失败: {e}")

    # ✅ 导出当前卡组到 TXT
    def export_current_deck(self, file_name: str = None, *subdirs) -> None:
        """
        导出当前卡组到指定路径下的 TXT 文件。
        如果未指定文件名，则弹窗让用户输入。
        """
        if not self.card_pool:
            self._show_error("导出失败", "当前卡组为空，无法导出")
            return

        if file_name is None:
            file_name, ok = QInputDialog.getText(
                self.main_window,
                "导出卡组",
                "请输入文件名（不含扩展名）："
            )
            if not ok or not file_name:
                return
            file_name += ".txt"

        try:
            # 使用统一导出接口，并根据 data_type 自动选择目录
            export_data(data=self.card_pool, file_name=file_name, data_type='deck')
            self._show_info("成功", f"卡组已导出至 data/构筑/{file_name}")
        except Exception as e:
            self._show_error("导出失败", f"{e}")

    def export_condition_data(self, filename: str = "default_conditions.txt", *subdirs) -> None:
        """
        导出当前条件数据到指定路径下的 TXT 文件。
        """
        if not self.condition_data:
            self._show_error("导出失败", "没有可导出的条件数据")
            return

        try:
            export_data(
                data=self.condition_data,
                filename=filename,
                data_type='condition',
                titles=self.titles,
                *subdirs
            )
            self._show_info("成功", f"条件数据已导出至 {filename}")
        except Exception as e:
            self._show_error("导出失败", f"{e}")

    # ✅ 弹出信息提示框
    def _show_info(self, title: str, message: str):
        QMessageBox.information(self.main_window, title, message)

    # ✅ 弹出错误提示框
    def _show_error(self, title: str, message: str):
        QMessageBox.critical(self.main_window, title, message)

    # ✅ 弹出确认对话框，返回是否确认
    def _show_confirm(self, title: str, message: str) -> bool:
        reply = QMessageBox.question(self.main_window, title, message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes

    # ✅ 加载 TXT 卡组（非 YDK）
    def load_deck_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List[str]:
        """
        从 TXT 文件或字符串中加载卡组。
        :param source: 文件路径或卡组文本内容
        :param is_path: 是否为文件路径
        :return: 卡组中的卡名列表
        """
        try:
            # ✅ 改用 file_service 接口
            result = load_file(source, handler_type="deck", is_path=is_path)
            self.card_pool = result
            return self.card_pool
        except Exception as e:
            self._show_error("加载失败", f"加载构筑失败: {e}")
            return []

    # ✅ 加载条件数据 TXT
    def load_condition_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List:
        """
        加载模拟使用的条件数据。
        :param source: 条件文件路径或字符串内容
        :param is_path: 是否为文件路径
        :return: 条件数据（多维列表）
        """
        try:
            # ✅ 改用 file_service 接口
            result, titles = load_file(source, handler_type="condition", is_path=is_path)
            self.condition_data = result
            self.titles = titles
            return result
        except Exception as e:
            self._show_error("加载失败", f"加载条件失败: {e}")
            return []

    # ✅ 运行模拟器逻辑
    def run_simulation(self, draw_size=5, num_draws=100000, snapshot_interval=20000, callback=None) -> Tuple[float, str]:
        """
        执行模拟抽卡计算。
        :param draw_size: 每次抽卡数
        :param num_draws: 总模拟次数
        :param snapshot_interval: 每隔多少次记录一次快照
        :param callback: 进度回调函数（可选）
        :return: Tuple(成功率, 模拟输出日志)
        """
        if not self.card_pool or not self.condition_data:
            self._show_error("模拟失败", "缺少卡组或条件数据，无法模拟")
            return 0.0, ""

        try:
            result = service_run_simulation(
                card_pool=self.card_pool,
                conditions=self.condition_data,
                draw_size=draw_size,
                num_draws=num_draws,
                snapshot_interval=snapshot_interval,
                titles=self.titles,
                callback=callback
            )
            return result
        except Exception as e:
            self._show_error("模拟失败", f"执行模拟时发生错误: {e}")
            return 0.0, ""

    # 🗃️ —— 与卡牌数据库交互的方法 —— #

    def get_all_cards(self) -> Dict[str, str]:
        """返回全部卡牌（cid -> 名称）"""
        return self.db.get_all_cards()

    def update_card_attribute(self, cid: str, attr_name: str, old_value: str, new_value: str) -> bool:
        """更新卡牌属性值"""
        return self.db.update_card_attribute(cid, attr_name, old_value, new_value)

    def add_card_attribute(self, cid: str, attr_name: str, value: str) -> bool:
        """添加新属性值"""
        return self.db.add_card_attribute(cid, attr_name, value)

    def remove_card_attribute(self, cid: str, attr_name: str, value: str) -> bool:
        """删除属性值"""
        return self.db.remove_card_attribute(cid, attr_name, value)

    def get_card_attributes(self, cid: str) -> Dict[str, Union[str, List[str]]]:
        """查询某卡牌的所有属性"""
        return self.db.get_card_attributes(cid)

    def get_all_fields(self) -> Set[str]:
        """获取数据库中所有可用的属性字段名"""
        return self.db.get_all_fields()

    def get_card_fields(self, cid: str) -> List[str]:
        """获取某张卡牌拥有的字段列表"""
        return self.db.get_card_fields(cid)

    def search_cards_by_keyword(self, keyword: str) -> Dict[str, str]:
        """使用关键字搜索卡牌，返回 {cid: 名称}"""
        return self.db.search_cards_by_keyword(keyword)

    def refresh_local_db(self) -> None:
        """刷新数据库缓存"""
        self.db.refresh()

    # 🧩 —— 文件对话框辅助 —— #

    def select_ydk_file(self) -> str:
        """弹出文件选择框，选择 YDK 文件"""
        file_path, _ = QFileDialog.getOpenFileName(None, "选择 YDK 文件", "", "YDK 文件 (*.ydk)")
        return file_path

    def select_output_file(self) -> str:
        """弹出保存路径选择框，选择导出文件路径"""
        file_path, _ = QFileDialog.getSaveFileName(None, "选择导出路径", "", "文本文件 (*.txt)")
        return file_path

    def _get_cids_from_names(self, names: List[str]) -> List[str]:
        """
        根据卡名列表查询对应卡片 ID。
        :param names: 卡名列表
        :return: 对应卡片的 cid 列表
        """
        cids = []
        for name in names:
            result = self.db.search_cards_by_keyword(name)
            if result:
                cids.append(next(iter(result.keys())))
        return cids

    def add_card(self, cid: str, name: str, fields: List[str] = None) -> bool:
        """
        添加一张新卡牌记录。
        :param cid: 卡牌 ID
        :param name: 卡牌名称
        :param fields: 字段列表
        :return: 是否添加成功
        """
        return self.db.add_card(cid=cid, name=name, fields=fields or [])

    def delete_card(self, cid: str) -> bool:
        """
        删除一张卡牌记录。
        :param cid: 卡牌 ID
        :return: 是否删除成功
        """
        return self.db.delete_card(cid)

    def save_condition_data(self, file_path: str, data: list):
        """
        保存条件数据到指定路径
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for cond in data:
                    if len(cond) >= 3:
                        f.write(f"{cond[0]},{cond[1]},{cond[2]}\n")
            return True
        except Exception as e:
            raise RuntimeError(f"保存失败: {e}")
