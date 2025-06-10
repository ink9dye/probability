# services/strategy_service.py
from core.repositories import strategy_repository

class StrategyService:
    def __init__(self):
        self.strategies = strategy_repository.get_builtin_strategies()

    def get_all_strategies(self):
        return self.strategies

    def get_strategy(self, name: str):
        for s in self.strategies:
            if s.name == name:
                return s
        return None

    def enable_strategy(self, name: str, enabled: bool = True) -> bool:
        strategy = self.get_strategy(name)
        if strategy:
            strategy.enabled = enabled
            return True
        return False

    def set_priority(self, name: str, priority: int) -> bool:
        strategy = self.get_strategy(name)
        if strategy:
            strategy.priority = priority
            return True
        return False

    def apply_all(self, hand, pool):
        return strategy_repository.apply_all_strategies(hand, pool, self.strategies)


# 单例实例
strategy_service = StrategyService()

def get_local_strategy_db():
    return strategy_service
