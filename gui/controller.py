import os
from services.ydk_service import load_ydk_file, export_to_txt
from services.parser_service import load_deck, load_conditions
from services.simulation_service import run_simulation,simulate_draws,summarize_results
from typing import List, Union, Set, Dict,Tuple
from services.local_db_service import get_local_db


class AppController:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.card_pool: List[str] = []
        self.condition_data = []
        self.titles = []
        self.db = get_local_db()



    # ✅ 加载 YDK（文件或文本）
    def load_ydk(self, source: Union[str, os.PathLike], is_path: bool = True, field_tag: str = None) -> List[str]:
        try:
            ydk_text = open(source, encoding='utf-8').read() if is_path else source
            card_names = load_ydk_file(ydk_text, field_tag=field_tag, is_path=False)
            return card_names
        except Exception as e:
            raise RuntimeError(f"加载 YDK 失败: {e}")

    def export_current_deck(self, output_file: str = None) -> None:
        if not self.card_pool:
            raise RuntimeError("当前卡组为空，无法导出")
        main_ids = self._get_cids_from_names(self.card_pool)
        export_to_txt(main_ids, [], [], output_file=output_file)

    # ✅ 加载 TXT（支持路径或文本）
    def load_deck_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List[str]:
        try:
            self.card_pool = load_deck(source, is_ydk=False, is_path=is_path)
            return self.card_pool
        except Exception as e:
            raise RuntimeError(f"加载构筑失败: {e}")

    # ✅ 加载条件 TXT（支持路径或文本）
    def load_condition_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List:
        try:
            self.condition_data, self.titles = load_conditions(source, is_path=is_path)
            return self.condition_data
        except Exception as e:
            raise RuntimeError(f"条件加载失败: {e}")

    # ✅ 执行模拟
    def run_simulation(self, draw_size=5, num_draws=100000, snapshot_interval=20000, callback=None) -> tuple[
        float, str]:
        if not self.card_pool or not self.condition_data:
            raise RuntimeError("缺少卡组或条件数据，无法模拟")

        from services.simulation_service import run_simulation as service_run_simulation

        # 只负责参数转发
        return service_run_simulation(
            card_pool=self.card_pool,
            conditions=self.condition_data,
            draw_size=draw_size,
            num_draws=num_draws,
            snapshot_interval=snapshot_interval,
            titles=self.titles,
            callback=callback
        )

    #卡片数据库相关

    def get_all_cards(self):
        return self.db.get_all_cards()

    def add_card(self, name: str, fields: List[str]) -> None:
        self.db.add_card(name, fields)  # ✅ 使用 self.db

    def add_field_to_cards(self, cids: List[str], field: str) -> None:
        for cid in cids:
            self.db.add_card_field(cid, field)  # ✅ 使用 self.db

    def update_card_field(self, cid: str, old_field: str, new_field: str) -> bool:
        return self.db.update_card_field(cid, old_field, new_field)

    def remove_card_field(self, cid: str, field: str) -> bool:
        return self.db.remove_card_field(cid, field)

    def get_all_fields(self) -> Set[str]:
        return self.db.get_all_fields()

    def get_card_fields(self, cid: str) -> List[str]:
        return self.db.get_card_fields(cid)

    def search_cards_by_keyword(self, keyword: str) -> Dict[str, str]:
        """
        根据关键词模糊搜索卡牌名称（不区分大小写）
        返回 {cid: name} 字典
        """
        return self.db.search_cards_by_keyword(keyword)

    def refresh_local_db(self) -> None:
        self.db.refresh()
