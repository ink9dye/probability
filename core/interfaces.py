# core/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Dict,Tuple

class ICardPoolParser(ABC):
    @abstractmethod
    def parse(self, content: str) -> List[str]:
        pass

class ISimulationEngine(ABC):
    @abstractmethod
    def run_simulation(self, card_pool: List[str], conditions: List[List[tuple]]) -> Dict[int, float]:
        pass
