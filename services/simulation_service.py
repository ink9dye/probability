# services/simulation_service.py

from core.probability import simulate_and_report
from typing import List, Dict,Tuple

class SimulationService:
    def __init__(self):
        self.deck = []
        self.conditions_list = []
        self.title = []

    def set_card_pool(self, deck: List[str]):
        """
        设置卡组。
        """
        self.deck = deck

    def set_conditions_list(self, conditions_list: List[List[Tuple[str, str, int]]]):
        """
        设置条件列表。
        """
        self.conditions_list = conditions_list

    def set_title(self, title: List[str]):
        """
        设置标题。
        """
        self.title = title

    def run_simulation(self) -> Dict[int, float]:
        """
        运行抽卡模拟，并返回概率统计结果。
        """
        probabilities, _ = simulate_and_report(self.deck, self.conditions_list, self.title)
        return probabilities
