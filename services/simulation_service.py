# services/simulation_service.py

from core.engine.probability_engine import simulate_draws as engine_simulate_draws
from dataclasses import dataclass
from typing import List, Tuple, Optional, Callable
from core.entity.composite_condition import CompositeCondition

@dataclass
class StrategyConfig:
    golden_manhu_enabled: bool = False
    golden_manhu_draw_count: int = 2
    golden_qianhu_enabled: bool = False
    golden_qianhu_priority_fields: List[str] = ("手坑",)
    golden_qianhu_draw_count: int = 6
    dark_draw_enabled: bool = False
    dark_draw_trigger_card: str = "暗抽卡"
    dark_draw_required_field: str = "暗属性"


def simulate_with_options(
    card_pool: List[str],
    conditions: List[CompositeCondition],
    titles: List[str],
    draw_size: int,
    num_draws: int,
    snapshot_interval: int,
    strategy_config=None,
    callback: Optional[Callable[[str], None]] = None
) -> Tuple[float, str]:
    """
    工具人函数：调用 engine 层的 simulate_draws
    """
    return engine_simulate_draws(
        card_pool=card_pool,
        conditions=conditions,
        titles=titles,
        draw_size=draw_size,
        num_draws=num_draws,
        snapshot_interval=snapshot_interval,
        strategy_config=strategy_config,
        callback=callback
    )
