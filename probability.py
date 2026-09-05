"""
向后兼容层：旧脚本 `import probability` 仍可用。
新代码请使用 app / domain / parsers。
"""

from domain.conditions.evaluator import check_conditions
from domain.conditions.metrics import (
    amphibian_kind_count_merged,
    amphibian_substring_count_merged,
    dong_count_adjusted,
    is_kind_condition,
    is_kind_sum_condition,
    special_condition_value,
)
from domain.deck import SANCAI_MARK, get_remaining_cards, strip_leading_post
from app.settings import (
    DEFAULT_SNAPSHOT_EVERY,
    DRAW_SIZE,
    POT_CARD_NUMBER,
    default_num_trials,
)
from domain.draw.rng import draw_cards, draw_one_inplace, seed_rng

DEFAULT_NUM_DRAWS = default_num_trials()
from domain.effects.dai_man import handle_dai_man_pot as _handle_dai_man_ctx
from domain.effects.going_second import (
    apply_fake_g,
    apply_going_second_sanhao,
    apply_going_second_sanhao_excavated_only,
)
from domain.effects.plugins import anchou, jianshen, zizou
from domain.effects.pots import handle_pot as _handle_pot_ctx
from domain.effects.going_second import handle_sancai_draw as _handle_sancai_ctx
from domain.engine.monte_carlo import MonteCarloEngine
from domain.models.scenario import RuleBundle, Scenario, SimulationOptions
from infrastructure.reporters.console import ConsoleReporter

draw_size = DRAW_SIZE
num_draws = default_num_trials()
num_show = DEFAULT_SNAPSHOT_EVERY
pot_card_number = POT_CARD_NUMBER

_strip_leading_post = strip_leading_post
_SANCAI_MARK = SANCAI_MARK
_SANHAO_GOING_SECOND_TRAP = "两栖后手魔陷"


def _seed_rng_from_env():
    return seed_rng(None)


def handle_fake_g_going_second(drawn_cards, card_pool, draw_times=1):
    from domain.draw.context import DrawContext
    from domain.models.scenario import SimulationOptions

    ctx = DrawContext(
        card_pool=card_pool,
        hand=drawn_cards,
        opening_first_5=drawn_cards[:draw_size],
        options=SimulationOptions(),
        rules=RuleBundle(),
    )
    apply_fake_g(ctx, draw_times)
    return ctx.hand


def handle_pot(drawn_cards, card_pool):
    from domain.draw.context import DrawContext
    from domain.models.scenario import RuleBundle, SimulationOptions

    ctx = DrawContext(
        card_pool=card_pool,
        hand=drawn_cards,
        opening_first_5=drawn_cards[:draw_size],
        options=SimulationOptions(),
        rules=RuleBundle(),
    )
    _handle_pot_ctx(ctx)
    return ctx.hand


def handle_sancai_draw(drawn_cards, card_pool):
    from domain.draw.context import DrawContext
    from domain.models.scenario import RuleBundle, SimulationOptions

    ctx = DrawContext(
        card_pool=card_pool,
        hand=drawn_cards,
        opening_first_5=drawn_cards[:draw_size],
        options=SimulationOptions(),
        rules=RuleBundle(),
    )
    _handle_sancai_ctx(ctx)
    return True


def handle_dai_man_pot(drawn_cards, card_pool, n, *, used_sancai=False, used_sanhao=False):
    from domain.draw.context import DrawContext
    from domain.models.scenario import RuleBundle, SimulationOptions

    ctx = DrawContext(
        card_pool=card_pool,
        hand=drawn_cards,
        opening_first_5=drawn_cards[:draw_size],
        options=SimulationOptions(),
        rules=RuleBundle(),
    )
    _handle_dai_man_ctx(ctx, n, used_sancai=used_sancai, used_sanhao=used_sanhao)
    return ctx.hand, ctx.dai_man_compare, ctx.excav_kept


def simulate_draws(
    card_pool,
    conditions_list,
    enable_going_second=False,
    amphibian_merge_one_rules=(),
    dong_merge_rules=(),
    dai_man_pot_n=None,
    sixth_draw_exclusions=(),
    dong_bu_exclusions=(),
):
    scenario = Scenario(
        card_pool=card_pool,
        conditions_list=conditions_list,
        group_sizes=[],
        group_titles=[],
        rules=RuleBundle(
            amphibian_merge_one=tuple(amphibian_merge_one_rules),
            dong_merge=tuple(dong_merge_rules),
            sixth_draw_exclusions=tuple(sixth_draw_exclusions),
            dong_bu_exclusions=tuple(dong_bu_exclusions),
        ),
        options=SimulationOptions(
            going_second=enable_going_second,
            dai_man_pot_n=dai_man_pot_n,
        ),
    )
    result = MonteCarloEngine().run(scenario)
    snapshots = [
        (
            s.draw_num,
            s.hand,
            conditions_list[s.matched_case_index] if s.matched_case_index is not None else None,
            s.dai_man_compare,
        )
        for s in result.snapshots
    ]
    return result.case_probabilities, snapshots


def simulate_and_report(
    card_pool,
    conditions_list,
    title,
    group_sizes,
    enable_going_second=False,
    amphibian_merge_one_rules=(),
    dong_merge_rules=(),
    dai_man_pot_n=None,
    sixth_draw_exclusions=(),
    dong_bu_exclusions=(),
):
    scenario = Scenario(
        card_pool=card_pool,
        conditions_list=conditions_list,
        group_sizes=group_sizes,
        group_titles=title,
        rules=RuleBundle(
            amphibian_merge_one=tuple(amphibian_merge_one_rules),
            dong_merge=tuple(dong_merge_rules),
            sixth_draw_exclusions=tuple(sixth_draw_exclusions),
            dong_bu_exclusions=tuple(dong_bu_exclusions),
        ),
        options=SimulationOptions(
            going_second=enable_going_second,
            dai_man_pot_n=dai_man_pot_n,
        ),
    )
    result = MonteCarloEngine().run(scenario)
    ConsoleReporter().emit(result)


def report_drawn_cards(drawn_cards_snapshots, conditions_list):
    from domain.models.simulation_result import DrawSnapshot

    snaps = [
        DrawSnapshot(
            draw_num=d,
            hand=h,
            matched_case_index=conditions_list.index(m) if m else None,
            dai_man_compare=dm,
        )
        for d, h, m, dm in drawn_cards_snapshots
    ]
    ConsoleReporter()._report_snapshots(snaps, conditions_list)


def report_probabilities(probabilities, conditions_list, title, group_sizes):
    from domain.models.simulation_result import SimulationResult

    cumulative = []
    group_start = 0
    for idx, size in enumerate(group_sizes):
        group_end = min(group_start + size, len(probabilities))
        if group_end <= group_start:
            continue
        group_prob = sum(probabilities[i] for i in range(group_start, group_end))
        t = title[idx] if idx < len(title) else "无标题"
        cumulative.append((t, group_prob))
        group_start = group_end

    result = SimulationResult(
        case_probabilities=probabilities,
        conditions_list=conditions_list,
        group_sizes=group_sizes,
        group_titles=title,
        total_probability=sum(probabilities.values()),
        group_cumulative=cumulative,
    )
    ConsoleReporter()._report_probabilities(result)
