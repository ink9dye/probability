import os, json
from typing import List, Union, Dict, Tuple, Set, Optional

from PySide6.QtWidgets import QMessageBox, QFileDialog, QInputDialog
from services.file_service import load_file, export_data, save_ydk
from services.simulation_service import simulate_with_options, StrategyConfig
from services.ydk_service import load_ydk_file, export_to_txt, batch_fetch_missing
from services.local_db_service import get_local_db
from config.settings import DECK_DIR, CONDITION_DIR
from dataclasses import asdict, is_dataclass


class AppController:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.card_pool: List[str] = []
        self.condition_data = []
        self.titles = []
        self.db = get_local_db()
        self.strategy_configs = []

    # ──────────────────────────────── 加载相关 ────────────────────────────────

    def load_ydk(self, source: Union[str, os.PathLike], is_path: bool = True, field_tag: str = None) -> List[str]:
        try:
            self.card_pool = load_ydk_file(source=source, is_path=is_path, field_tag=field_tag)
            return self.card_pool
        except Exception as e:
            raise RuntimeError(f"加载 YDK 失败: {e}")

    def load_deck_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List[str]:
        try:
            self.card_pool = load_file(source, handler_type="deck", is_path=is_path)
            return self.card_pool
        except Exception as e:
            self._show_error("加载失败", f"加载构筑失败: {e}")
            return []

    def load_condition_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List:
        try:
            result, self.titles = load_file(source, handler_type="condition", is_path=is_path)
            self.condition_data = result
            return result
        except Exception as e:
            self._show_error("加载失败", f"加载条件失败: {e}")
            return []

    # ──────────────────────────────── 导出相关 ────────────────────────────────

    def export_current_deck(self, file_name: str = None, *subdirs) -> None:
        if not self.card_pool:
            self._show_error("导出失败", "当前卡组为空，无法导出")
            return

        file_name = file_name or self._ask_for_filename("导出卡组", "请输入文件名（不含扩展名）：")
        if not file_name:
            return

        try:
            export_data(data=self.card_pool, file_name=file_name + ".txt", data_type='deck')
            self._show_info("成功", f"卡组已导出至 data/构筑/{file_name}.txt")
        except Exception as e:
            self._show_error("导出失败", f"{e}")

    def export_current_deck_with_ydk(self, ydk_content: str, file_name: str = None):
        """
        接收 YDK 文本内容，解析并导出为 TXT 卡组文件（主卡组 / 额外 / 副卡组全处理）。
        """
        try:
            from services.file_service import load_file

            # 1️⃣ 从文本中解析 main / extra / side 三个区域
            ydk_data = load_file(ydk_content, handler_type="ydk", is_path=False)
            main_ids = ydk_data.get("main", [])
            extra_ids = ydk_data.get("extra", [])
            side_ids = ydk_data.get("side", [])

            # 2️⃣ 自动补全卡牌信息
            all_ids = main_ids + extra_ids + side_ids
            batch_fetch_missing(all_ids)

            # 3️⃣ 打印调试信息（模仿 ydk_main）
            print(f"总卡牌数量（含重复）: {len(all_ids)}")
            print(f"唯一卡牌数量: {len(set(all_ids))}")
            db = get_local_db()
            print(f"当前数据库缓存大小: {len(db.id_attr_map)}")

            def print_section(title: str, ids: list[str]):
                print(f"\n=== {title} ===")
                for idx, cid in enumerate(ids, 1):
                    name = db.get_card_name(cid)
                    print(f"{idx:2d}. [{cid}] {name}")

            print_section("主卡组", main_ids)
            print_section("额外卡组", extra_ids)
            print_section("副卡组", side_ids)

            # 4️⃣ 导出 TXT 构筑（只主卡组）
            export_to_txt(main_ids, extra_ids, side_ids, output_file=file_name)

            self._show_info("导出成功", f"构筑卡组已导出为：{file_name}")

        except Exception as e:
            self._show_error("导出失败", f"导出 YDK 内容时发生错误: {e}")

    def export_current_deck_with_data(self, card_names: list):
        if not card_names:
            self._show_error("导出失败", "当前卡组为空")
            return

        file_name = self._ask_for_filename("导出卡组", "请输入文件名（不含扩展名）：")
        if not file_name:
            return

        try:
            export_data(data=card_names, file_name=file_name + ".txt", data_type='deck')
            self._show_info("成功", f"卡组已导出至 data/构筑/{file_name}.txt")
        except Exception as e:
            self._show_error("导出失败", f"{e}")

    def export_condition_data(self, filename: str = "default_conditions.txt", *subdirs) -> None:
        if not self.condition_data:
            self._show_error("导出失败", "没有可导出的条件数据")
            return
        try:
            export_data(data=self.condition_data, filename=filename, data_type='condition', titles=self.titles, *subdirs)
            self._show_info("成功", f"条件数据已导出至 {filename}")
        except Exception as e:
            self._show_error("导出失败", f"{e}")

    # ──────────────────────────────── 模拟逻辑 ────────────────────────────────

    def run_simulation(self, draw_size=5, num_draws=10000, snapshot_interval=2000, callback=None) -> Tuple[
        float, str]:
        print(f"✔ 传入的策略配置为: {asdict(self.strategy_configs[0]) if self.strategy_configs else '无'}")

        if not self.card_pool or not self.condition_data:
            self._show_error("模拟失败", "缺少卡组或条件数据")
            return 0.0, ""

        try:
            strategy_config = self.strategy_configs[0] if self.strategy_configs else StrategyConfig()
            probability, summary = simulate_with_options(
                card_pool=self.card_pool,
                conditions=self.condition_data,
                titles=self.titles,
                draw_size=draw_size,
                num_draws=num_draws,
                snapshot_interval=snapshot_interval,  # 确保 snapshot_interval 参数被传递
                strategy_config=self.strategy_configs[0],
                callback=callback,
                **asdict(strategy_config)
            )
            return probability, summary
        except Exception as e:
            self._show_error("模拟失败", str(e))
            return 0.0, ""

    def set_strategy_config(self, configs: list):
        from dataclasses import asdict
        self.strategy_configs = [StrategyConfig(**c) for c in configs]

    # ──────────────────────────────── 数据库操作 ────────────────────────────────

    def get_all_cards(self): return self.db.get_all_cards()
    def update_card_attribute(self, cid, attr, old, new): return self.db.update_card_attribute(cid, attr, old, new)
    def add_card_attribute(self, cid, attr, val): return self.db.add_card_attribute(cid, attr, val)
    def remove_card_attribute(self, cid, attr, val): return self.db.remove_card_attribute(cid, attr, val)
    def get_card_attributes(self, cid): return self.db.get_card_attributes(cid)
    def get_all_fields(self): return self.db.get_all_fields()
    def get_card_fields(self, cid): return self.db.get_card_fields(cid)
    def search_cards_by_keyword(self, keyword): return self.db.search_cards_by_keyword(keyword)
    def refresh_local_db(self): self.db.refresh()
    def add_card(self, cid, name, fields=None): return self.db.add_card(cid, name, fields or [])
    def delete_card(self, cid): return self.db.delete_card(cid)

    def save_condition_data(self, file_path: str, data: list):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                for cond in data:
                    if len(cond) >= 3:
                        f.write(f"{cond[0]},{cond[1]},{cond[2]}\n")
            return True
        except Exception as e:
            raise RuntimeError(f"保存失败: {e}")

    # ──────────────────────────────── 文件 / 弹窗辅助 ────────────────────────────────

    def _ask_for_filename(self, title: str, prompt: str) -> Optional[str]:
        name, ok = QInputDialog.getText(self.main_window, title, prompt)
        return name if ok and name else None

    def _show_info(self, title: str, msg: str): QMessageBox.information(self.main_window, title, msg)
    def _show_error(self, title: str, msg: str): QMessageBox.critical(self.main_window, title, msg)
    def _show_confirm(self, title: str, msg: str) -> bool:
        return QMessageBox.question(self.main_window, title, msg, QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.Yes

    def select_ydk_file(self) -> str:
        file_path, _ = QFileDialog.getOpenFileName(None, "选择 YDK 文件", "", "YDK 文件 (*.ydk)")
        return file_path

    def select_output_file(self) -> str:
        file_path, _ = QFileDialog.getSaveFileName(None, "选择导出路径", "", "文本文件 (*.txt)")
        return file_path

    def _get_cids_from_names(self, names: List[str]) -> List[str]:
        cids = []
        for name in names:
            result = self.db.search_cards_by_keyword(name)
            if result:
                cids.append(next(iter(result.keys())))
        return cids
