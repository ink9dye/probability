
from services.ydk_service import load_ydk_file, export_to_txt
from services.deck_service import get_deck
from services.condition_service import get_conditions
from services.simulation_service import run_simulation,simulate_draws,summarize_results
from services.local_db_service import LocalCardDB
from typing import List, Union, Set, Dict,Tuple
import os


class AppController:
    def __init__(self, main_window=None):
        self.main_window = main_window
        self.card_pool: List[str] = []
        self.condition_data = []
        self.titles = []
        self.db = LocalCardDB()

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
            self.card_pool = get_deck(source, is_ydk=False, is_path=is_path)
            return self.card_pool
        except Exception as e:
            raise RuntimeError(f"加载构筑失败: {e}")

    # ✅ 加载条件 TXT（支持路径或文本）
    def load_condition_txt(self, source: Union[str, os.PathLike], is_path: bool = True) -> List:
        try:
            self.condition_data, self.titles = get_conditions(source, is_path=is_path)
            return self.condition_data
        except Exception as e:
            raise RuntimeError(f"条件加载失败: {e}")

    # ✅ 执行模拟
    def run_simulation(self, draw_size=5, num_draws=100000, snapshot_interval=20000) -> Tuple[float, str]:
        if not self.card_pool or not self.condition_data:
            raise RuntimeError("缺少卡组或条件数据，无法模拟")

        matched_indices, _ = simulate_draws(
            card_pool=self.card_pool,
            conditions=self.condition_data,
            draw_size=draw_size,
            num_draws=num_draws,
            snapshot_interval=snapshot_interval,
            titles=self.titles
        )

        summary = summarize_results(
            matched_indices=matched_indices,
            titles=self.titles,
            total_conditions=len(self.condition_data),
            conditions=self.condition_data
        )

        hit_count = sum(1 for i in matched_indices if i is not None)
        return hit_count / len(matched_indices), summary

    def _get_cids_from_names(self, card_names: List[str]) -> List[str]:
        name_to_id = {v: k for k, v in self.db.id_name_map.items()}
        return [name_to_id[name] for name in card_names if name in name_to_id]

    def add_field_to_cards(self, cids: List[str], field: str) -> None:
        self.db.update_cards_field(cids, field)

    def update_card_field(self, cid: str, old_field: str, new_field: str) -> bool:
        return self.db.update_card_field(cid, old_field, new_field)

    def remove_card_field(self, cid: str, field: str) -> bool:
        return self.db.remove_card_field(cid, field)

    def get_all_fields(self) -> Set[str]:
        return self.db.get_all_fields()

    def search_cards_by_keyword(self, keyword: str) -> Dict[str, str]:
        all_cards = self.db.get_all_cards()
        return {cid: name for cid, name in all_cards.items() if keyword in name}

    def refresh_local_db(self) -> None:
        self.db.refresh()
