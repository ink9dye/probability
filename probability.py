import os
import random
import re
from collections import Counter

draw_size = 5
# 单次模拟次数越大，比例估计的标准误越小（约 ∝ 1/√N）；默认较原 30 万略增以缩小随机抖动。
# 环境变量 PROB_SIM_N 可覆盖次数（仅影响数值与耗时，不改变打印格式）。
_raw_n = os.environ.get("PROB_SIM_N", "").strip()
try:
    num_draws = max(1000, int(_raw_n)) if _raw_n else 400000
except ValueError:
    num_draws = 400000
del _raw_n
num_show = 50000
pot_card_number = 6

_rng = random.Random()


def _seed_rng_from_env() -> int | None:
    """若环境变量 PROB_SIM_SEED 为整数则固定 RNG；返回所用种子或 None。"""
    raw = os.environ.get("PROB_SIM_SEED", "").strip()
    if not raw:
        return None
    try:
        v = int(raw)
    except ValueError:
        return None
    _rng.seed(v)
    return v


# 「前缀-种类」：后缀固定为半角 -种类；度量为手牌中含该前缀的不同牌名种数（同名多张只算 1）
_KIND_SUFFIX = "-种类"

# 「种类」求和条件里连接多项的分隔符（半角/全角加号）
_KIND_SUM_PLUS_SPLIT = ("+", "＋")


_SANCAI_MARK = "后置三才"


def _strip_leading_post(card):
    if card.endswith(_SANCAI_MARK):
        card = card[: -len(_SANCAI_MARK)]
    if card.startswith("后置"):
        return card[2:]
    return card


def _hand_has_exact_pool_card(drawn_cards, pool_name):
    return any(_strip_leading_post(c) == pool_name for c in drawn_cards)


def _amphibian_substring_count_merged(drawn_cards, substring, merge_rules):
    """
    含 substring 的张数；每条已触发的 @两栖齐现只算一张 规则会把该组内匹配 substring 的张合并为计 1。
    """
    cnt = sum(1 for c in drawn_cards if substring in c)
    for name_tuple in merge_rules:
        names_set = set(name_tuple)
        if not all(_hand_has_exact_pool_card(drawn_cards, n) for n in name_tuple):
            continue
        k = sum(
            1
            for c in drawn_cards
            if _strip_leading_post(c) in names_set and substring in c
        )
        if k >= 2:
            cnt -= k - 1
    return cnt


def _amphibian_kind_count_merged(drawn_cards, merge_rules):
    """
    「两栖-种类」：手牌中含「两栖」的不同牌实例种数，再对每条齐现规则把组内多种合并减 1。
    """
    distinct = {c for c in drawn_cards if "两栖" in c}
    n = len(distinct)
    for name_tuple in merge_rules:
        names_set = set(name_tuple)
        if not all(_hand_has_exact_pool_card(drawn_cards, x) for x in name_tuple):
            continue
        amphib_from_rule = {c for c in distinct if _strip_leading_post(c) in names_set}
        if len(amphib_from_rule) >= 2:
            n -= len(amphib_from_rule) - 1
    return n


def _dong_count_adjusted(drawn_cards, dong_merge_rules=()):
    """
    统计条件名「动」：先按手牌中含子串「动」的张数计数，再对每个已触发的
    @齐现只算一张动 规则合并——该规则所列牌名均在手牌中至少各 1 张时，
    这些牌名对应的所有张里若有多张含「动」则只保留 1 张的量；若均不含「动」则补 1（整套算 1 动）。
    """
    cnt = sum(1 for c in drawn_cards if "动" in c)
    for name_tuple in dong_merge_rules:
        names_set = set(name_tuple)
        if not all(_hand_has_exact_pool_card(drawn_cards, n) for n in name_tuple):
            continue
        pair_cards = [c for c in drawn_cards if _strip_leading_post(c) in names_set]
        d = sum(1 for c in pair_cards if "动" in c)
        if d >= 2:
            cnt -= d - 1
        elif d == 0:
            cnt += 1
    return cnt


def _split_kind_sum_parts(card_name):
    """按加号拆「种类」求和表达式；无加号则返回单元素列表。"""
    if not any(p in card_name for p in _KIND_SUM_PLUS_SPLIT):
        return [card_name]
    pattern = "|".join(re.escape(p) for p in _KIND_SUM_PLUS_SPLIT)
    return [p.strip() for p in re.split(pattern, card_name) if p.strip()]


def _is_kind_condition(card_name):
    if any(p in card_name for p in _KIND_SUM_PLUS_SPLIT):
        return False
    return card_name.endswith(_KIND_SUFFIX) and len(card_name) > len(_KIND_SUFFIX)


def _is_kind_sum_condition(card_name):
    """
    形如「两栖-种类+后手-种类」：多项均为「前缀-种类」，用 + / ＋ 连接，表示各类种数之和。
    """
    parts = _split_kind_sum_parts(card_name)
    return len(parts) >= 2 and all(_is_kind_condition(p) for p in parts)


def _kind_prefix(card_name):
    return card_name[: -len(_KIND_SUFFIX)]


def _kind_metric_for_prefix(prefix, drawn_cards, amphibian_merge_one_rules):
    if not prefix:
        return None
    if prefix == "两栖":
        return _amphibian_kind_count_merged(drawn_cards, amphibian_merge_one_rules)
    return len({c for c in drawn_cards if prefix in c})


def _special_condition_value(card_name, drawn_cards, amphibian_merge_one_rules):
    """
    返回保留条件名对应的度量；未知名返回 None，由调用方回退到普通子串计数。

    {前缀}-种类：牌名字符串包含「前缀」的不同牌名种数（用于避免两张同名牌计成两种）。
    前缀为「两栖」时应用 @两栖齐现只算一张 合并。
    若干「前缀-种类」用 + / ＋ 连接时，度量为各项种数之和（同一牌可同时计入多项前缀种类时，总和会重复计该牌）。
    """
    if _is_kind_sum_condition(card_name):
        total = 0
        for p in _split_kind_sum_parts(card_name):
            if not _is_kind_condition(p):
                return None
            prefix = _kind_prefix(p)
            v = _kind_metric_for_prefix(prefix, drawn_cards, amphibian_merge_one_rules)
            if v is None:
                return None
            total += v
        return total
    if _is_kind_condition(card_name):
        prefix = _kind_prefix(card_name)
        return _kind_metric_for_prefix(prefix, drawn_cards, amphibian_merge_one_rules)
    return None


def _skip_substring_count(card_name):
    """不参与「子串出现次数」累加的条件名。"""
    return _is_kind_condition(card_name) or _is_kind_sum_condition(card_name)


def draw_cards(card_pool, draw_count):
    """
    从卡池中随机抽取指定数量的卡片。
    使用模块级随机数生成器，避免每次创建/seed 新实例带来的额外开销。
    """
    if len(card_pool) < draw_count:
        raise ValueError("卡池中的卡片数量不足以抽取指定数量的卡片")

    return _rng.sample(card_pool, draw_count)


def _draw_one_inplace(remaining_cards):
    """
    从 remaining_cards 中随机抽 1 张，并从列表中移除该张（避免重复抽到同一张）。
    """
    if not remaining_cards:
        raise ValueError("没有可抽取的剩余卡片")
    idx = _rng.randrange(len(remaining_cards))
    return remaining_cards.pop(idx)


def handle_fake_g_going_second(drawn_cards, card_pool, draw_times=1):
    """
    后手可选逻辑：
    随机起手后，若开启后手模式且「最初 5 张起手」中含「假g」，则按张数再抽：
    1 张假 g → draw_times 为 1；两张及以上 → draw_times 为 2。
    以「后置」前缀加入手牌（不移除原假 g 卡）。
    """
    if draw_times <= 0:
        return drawn_cards

    remaining_cards = get_remaining_cards(card_pool, drawn_cards)
    for _ in range(draw_times):
        if not remaining_cards:
            break
        drawn_cards.append("后置" + _draw_one_inplace(remaining_cards))

    return drawn_cards


def get_remaining_cards(card_pool, drawn_cards):
    """
    按“旧逻辑”实现的剩余卡：
    旧写法是 [card for card in card_pool if card not in drawn_cards]，
    即：只要某张牌名在手牌中出现过，就把卡组里所有同名的牌都去掉。
    这里用 set 加速 membership，语义保持不变。
    """
    drawn_set = set(drawn_cards)
    return [card for card in card_pool if card not in drawn_set]


def check_conditions(
    drawn_cards,
    conditions,
    amphibian_merge_one_rules=(),
    dong_merge_rules=(),
):
    """
    检查抽取的卡片是否符合给定条件集合。
    普通项：统计手牌中「牌名字符串包含 card_name 子串」的张数。
    保留项：{前缀}-种类，以及用「+」连接的多种类之和（如 两栖-种类+后手-种类）— 见 _special_condition_value。
    amphibian_merge_one_rules：@两栖齐现只算一张；影响「两栖」「魔牌两栖」「两栖-种类」。
    dong_merge_rules：@齐现只算一张动；仅影响条件键恰好为「动」的计数。
    """
    card_counts = Counter()
    dong_adjusted = _dong_count_adjusted(drawn_cards, dong_merge_rules)

    for card_name, operator, value in conditions:
        if _skip_substring_count(card_name):
            continue
        if card_name == "动":
            card_counts[card_name] = dong_adjusted
            continue
        if card_name == "两栖":
            card_counts[card_name] = _amphibian_substring_count_merged(
                drawn_cards, "两栖", amphibian_merge_one_rules
            )
            continue
        if card_name == "魔牌两栖":
            card_counts[card_name] = _amphibian_substring_count_merged(
                drawn_cards, "魔牌两栖", amphibian_merge_one_rules
            )
            continue
        for card in drawn_cards:
            if card_name in card:
                card_counts[card_name] += 1

    for card_name, operator, value in conditions:
        special = _special_condition_value(
            card_name, drawn_cards, amphibian_merge_one_rules
        )
        if special is not None:
            card_count = special
        else:
            card_count = card_counts.get(card_name, 0)
        if operator == "大于等于" and card_count < value:
            return False
        elif operator == "大于" and card_count <= value:
            return False
        elif operator == "等于" and card_count != value:
            return False
        elif operator == "小于" and card_count >= value:
            return False
        elif operator == "小于等于" and card_count > value:
            return False

    return True


def _dai_man_shuffle_tier(
    card,
    fake_g_ref_first_5,
    hand_before,
    stripped_shape_counts,
    *,
    is_excavated=False,
    used_sancai=False,
    used_sanhao=False,
):
    """
    怠慢壶：在「去掉壶后的手牌 ∪ 翻出堆」合并列表上为每张牌算 tier；
    全局挑出 tier 最小的 n-1 张洗回（同 tier 随机打散），其余一律留在手牌。

    tier 数字（越小越早洗回）：0 真废件（含「真废件」）>
    1 仅当开局阶段（怠慢壶前）已具备并将结算对应三才或三号时：翻出堆中含「三才」/「三号」的卡（优先洗回）>
    2 怠慢壶（发动用掉一张后，其余在手或翻出堆中的复数壶优先洗回）>
    3 五手外假g > 4 废件（含「废件」且非真废件）> 5 两栖后手魔陷 > 6 手坑 >
    7 皇子+皇国时的皇国 > 8 复数 > 9 其它。
    真废件与普通废件各自为一档；同档且本次只能洗回其中一部分时：名字含「阿莱」或「熟练」的最优先洗回，
    其余次之；同档内再按牌名长度短者优先（见 _dai_man_tier1_junk_keys）。
    tier 9「其它」内部：在全局贪心洗回里处理——裸其它最早洗回；含「两栖」「后手」的牌
    晚于裸其它，并在剩余池里动态倾向洗回较多的一侧以使保留量接近；「动补」与（仅当全池无动补时的）「动」
    尽量晚洗回，并在收尾用交换保证至少保留一张动补或一张动（见 _dai_man_pick_remove_indices）。
    「复数」：当前整段牌型（去掉壶后的手牌 ∪ 翻出堆）里去前缀同名张数 ≥ 2。

    若一张牌命中多类，取 tier **最小值**（更早洗回的一侧生效）。
    「五手外假g」：含「假g」且去前缀牌名不在 **发动怠慢壶前手牌的前 5 张**
    （fake_g_ref_first_5）已出现的牌名集合中。
    """
    st = _strip_leading_post(card)
    tiers = []
    if "真废件" in card:
        tiers.append(0)
    if is_excavated and used_sancai and "三才" in card:
        tiers.append(1)
    if is_excavated and used_sanhao and "三号" in card:
        tiers.append(1)
    if "废件" in card and "真废件" not in card:
        tiers.append(4)
    if "两栖后手魔陷" in card:
        tiers.append(5)
    if "怠慢壶" in card:
        tiers.append(2)
    if "假g" in card:
        ref_names = {_strip_leading_post(c) for c in fake_g_ref_first_5}
        if st not in ref_names:
            tiers.append(3)
    if "手坑" in card:
        tiers.append(6)
    if "皇国" in card:
        has_huangzi = any("皇子" in c for c in hand_before)
        has_huangguo = any("皇国" in c for c in hand_before)
        if has_huangzi and has_huangguo:
            tiers.append(7)
    if stripped_shape_counts.get(st, 0) >= 2:
        tiers.append(8)
    if not tiers:
        tiers.append(9)
    return min(tiers)


def _dai_man_tier1_junk_keys(card):
    """
    真废件（tier 0）与普通废件（tier 4）内部：越早洗回 sort 键越小。
    含「阿莱」或「熟练」最优先(0)；其它废件(1)。同档内再按 len(牌名) 升序。
    """
    if "阿莱" in card or "熟练" in card:
        return (0, len(card))
    return (1, len(card))


def _dai_man_removal_sort_key(
    i,
    combined,
    tiers_by_idx,
    remaining,
    *,
    combined_has_dongbu,
    combined_has_dong,
):
    """
    越小表示本轮越优先洗回。
    tier 0 / 4 废件档、5 两栖后手魔陷：废件档用阿莱/熟练键；tier 9「其它」用后续各档细分贪心。
    """
    tier = tiers_by_idx[i]
    rnd = _rng.random()
    c = combined[i]
    if tier == 0:
        t1_pri, t1_len = _dai_man_tier1_junk_keys(c)
        return (tier, t1_pri, t1_len, 0, 0, 0, rnd, i)
    if tier == 4:
        t1_pri, t1_len = _dai_man_tier1_junk_keys(c)
        return (tier, t1_pri, t1_len, 0, 0, 0, rnd, i)
    if tier == 5:
        return (tier, 0, len(c), 0, 0, 0, rnd, i)
    if tier != 9:
        return (tier, 0, 0, 0, 0, 0, rnd, i)

    need_dong_reserve = (not combined_has_dongbu) and combined_has_dong

    is_db = "动补" in c
    is_ax = "两栖" in c
    is_hs = "后手" in c
    is_dong = "动" in c

    hs_only = is_hs and not is_ax
    ax_only = is_ax and not is_hs
    both_ax_hs = is_ax and is_hs

    rh_ex = sum(
        1
        for j in remaining
        if tiers_by_idx[j] == 9
        and "后手" in combined[j]
        and "两栖" not in combined[j]
    )
    ra_ex = sum(
        1
        for j in remaining
        if tiers_by_idx[j] == 9
        and "两栖" in combined[j]
        and "后手" not in combined[j]
    )

    # 裸其它：无动补、无两栖/后手标签，且不触发「无动补时须留动」的纯动保留
    if not is_db and not is_ax and not is_hs and not (need_dong_reserve and is_dong):
        return (tier, 0, 0, 0, 0, 0, rnd, i)

    if is_db:
        return (tier, 6, 0, 0, 0, 0, rnd, i)

    if need_dong_reserve and is_dong and not is_db:
        return (tier, 5, 0, 0, 0, 0, rnd, i)

    if both_ax_hs:
        return (tier, 4, 0, 0, 0, len(c), rnd, i)

    if hs_only:
        if rh_ex > ra_ex:
            bal = -1
        elif rh_ex < ra_ex:
            bal = 1
        else:
            bal = 0
        return (tier, 3, bal, 0, 0, len(c), rnd, i)

    if ax_only:
        if ra_ex > rh_ex:
            bal = -1
        elif ra_ex < rh_ex:
            bal = 1
        else:
            bal = 0
        return (tier, 3, bal, 0, 0, len(c), rnd, i)

    return (tier, 2, 0, 0, 0, len(c), rnd, i)


def _dai_man_repair_dongbu_dong(combined, tiers_by_idx, rm_indices):
    """
    若全池曾存在动补却未保留任一：与同档 tier 交换一张非动补进洗回列。
    若全池无动补但曾存在「动」却未保留任一：同理交换保留一张动。
    """
    rm = set(rm_indices)
    n = len(combined)

    def keep():
        return set(range(n)) - rm

    def pool_has(pred):
        return any(pred(combined[j]) for j in range(n))

    def kept_has(pred):
        return any(pred(combined[j]) for j in keep())

    def swap_same_tier(i_rm, i_kp):
        if tiers_by_idx[i_rm] != tiers_by_idx[i_kp]:
            return False
        rm.remove(i_rm)
        rm.add(i_kp)
        return True

    for _ in range(8):
        k = keep()
        chg = False

        if pool_has(lambda c: "动补" in c) and not kept_has(lambda c: "动补" in c):
            for i_rm in list(rm):
                if "动补" not in combined[i_rm]:
                    continue
                for i_kp in k:
                    if "动补" in combined[i_kp]:
                        continue
                    if swap_same_tier(i_rm, i_kp):
                        chg = True
                        break
                if chg:
                    break

        if chg:
            continue

        if (
            not pool_has(lambda c: "动补" in c)
            and pool_has(lambda c: "动" in c)
            and not kept_has(lambda c: "动" in c)
        ):
            for i_rm in list(rm):
                if "动" not in combined[i_rm]:
                    continue
                for i_kp in k:
                    if "动" in combined[i_kp]:
                        continue
                    if swap_same_tier(i_rm, i_kp):
                        chg = True
                        break
                if chg:
                    break

        if not chg:
            break

    return rm


def _dai_man_pick_remove_indices(combined, tiers_by_idx, remove_count):
    n = len(combined)
    combined_has_dongbu = any("动补" in combined[i] for i in range(n))
    combined_has_dong = any("动" in combined[i] for i in range(n))
    remaining = set(range(n))
    rm_list = []
    for _ in range(remove_count):
        best_key = None
        best_i = None
        for i in remaining:
            key = _dai_man_removal_sort_key(
                i,
                combined,
                tiers_by_idx,
                remaining,
                combined_has_dongbu=combined_has_dongbu,
                combined_has_dong=combined_has_dong,
            )
            if best_key is None or key < best_key:
                best_key = key
                best_i = i
        remaining.remove(best_i)
        rm_list.append(best_i)
    return _dai_man_repair_dongbu_dong(combined, tiers_by_idx, set(rm_list))


_SANHAO_GOING_SECOND_TRAP = "两栖后手魔陷"


def apply_going_second_sanhao(drawn_cards):
    """
    后手模式（enable going-second yes）：手牌中含「三号」的牌按张替换——
    若当前手牌已有「怠慢壶」则「三号」→「两栖后手魔陷」，否则「三号」→「怠慢壶」。
    多张三号从左到右依次判定（先转化的怠慢壶会影响后续三号）。
    开局阶段三号与本函数一同只结算一次；怠慢壶翻出保留的三号见 apply_going_second_sanhao_excavated_only。
    """
    changed = False
    for i in range(len(drawn_cards)):
        if "三号" not in drawn_cards[i]:
            continue
        has_dai_man = any("怠慢壶" in c for c in drawn_cards)
        repl = _SANHAO_GOING_SECOND_TRAP if has_dai_man else "怠慢壶"
        drawn_cards[i] = drawn_cards[i].replace("三号", repl)
        changed = True
    return changed


def apply_going_second_sanhao_excavated_only(
    drawn_cards, excav_kept, *, dai_man_was_used=False
):
    """
    仅对手牌中属于怠慢壶翻出且洗完仍留在手里的那些实例做三号替换（ multiset 对齐）。
    若此时手上已无怠慢壶但本局已发动过怠慢壶，则视为「已有怠慢壶」分支，三号→两栖后手魔陷。
    """
    rem = Counter(excav_kept)
    for i in range(len(drawn_cards)):
        c = drawn_cards[i]
        if "三号" not in c:
            continue
        if rem[c] <= 0:
            continue
        rem[c] -= 1
        has_pot_in_hand = any("怠慢壶" in x for x in drawn_cards)
        repl = (
            _SANHAO_GOING_SECOND_TRAP
            if (has_pot_in_hand or dai_man_was_used)
            else "怠慢壶"
        )
        drawn_cards[i] = c.replace("三号", repl)


def handle_sancai_draw(drawn_cards, card_pool):
    """
    若手牌中存在名字含「三才」的卡，则从卡组再随机抽最多 2 张，
    并在卡名末尾追加后缀「后置三才」（无括号，便于与起手本体区分）。
    返回是否在本阶段执行了三才结算（含卡组已空、未能实际抽牌的情形）。
    """
    if not any("三才" in c for c in drawn_cards):
        return False
    remaining_cards = get_remaining_cards(card_pool, drawn_cards)
    if not remaining_cards:
        return True
    n = min(2, len(remaining_cards))
    for c in draw_cards(remaining_cards, n):
        drawn_cards.append(c + _SANCAI_MARK)
    return True


def handle_dai_man_pot(drawn_cards, card_pool, n, *, used_sancai=False, used_sanhao=False):
    """
    怠慢壶：去掉一张壶后从卡组展示 n 张；洗回哪 n-1 张按优先级在
    **（先前手牌 ∪ 翻出堆）** 全体上选取——主档 tier 越小越早洗回；tier 9「其它」为贪心多步选取
    （裸其它最先洗回；两栖/后手洗回次于裸其它且在剩余池内向两类均衡贴近；动补与「仅动」尽量晚洗回，
    再以交换保证至少保留一张动补或一张动）；真废件与普通废件见 _dai_man_tier1_junk_keys；
    tier 5 两栖后手魔陷；洗回顺序档见 _dai_man_shuffle_tier 文档。
    调用前起手须已含「怠慢壶」。
    used_sancai / used_sanhao：怠慢壶前是否**曾经具备并将结算**三才/三号（三号仅在后手开启且手上有三号时）。
    仅在为 True 时，翻出堆中对应「三才」「三号」牌才适用 tier 1 优先洗回。

    返回值：(结算后的手牌列表, 打印用三元组, 洗完仍留在手里的翻出堆牌列表)。
    三元组为 None 表示未发动；否则为 (发动前手牌, 去掉壶且翻出 n 张尚未洗回的手牌视图, 洗完后的手牌)。
    """
    if not any("怠慢壶" in c for c in drawn_cards):
        return drawn_cards, None, []

    hand_before = list(drawn_cards)
    fake_g_ref_first_5 = hand_before[:draw_size]

    rm_idx = next(i for i, c in enumerate(drawn_cards) if "怠慢壶" in c)
    hand_minus_pot = drawn_cards[:rm_idx] + drawn_cards[rm_idx + 1 :]

    remaining_cards = get_remaining_cards(card_pool, hand_minus_pot)
    if not remaining_cards:
        triple = (hand_before, list(hand_minus_pot), list(hand_minus_pot))
        return hand_minus_pot, triple, []

    n_effective = min(max(int(n), 1), len(remaining_cards))
    new_cards = draw_cards(remaining_cards, n_effective)

    combined = list(hand_minus_pot) + list(new_cards)
    exc_start = len(hand_minus_pot)
    shape_counts = Counter(_strip_leading_post(c) for c in combined)

    tiers_by_idx = [
        _dai_man_shuffle_tier(
            combined[i],
            fake_g_ref_first_5,
            hand_before,
            shape_counts,
            is_excavated=(i >= exc_start),
            used_sancai=used_sancai,
            used_sanhao=used_sanhao,
        )
        for i in range(len(combined))
    ]

    remove_count = n_effective - 1
    rm_indices = _dai_man_pick_remove_indices(combined, tiers_by_idx, remove_count)
    after_hand = [c for j, c in enumerate(combined) if j not in rm_indices]
    excav_kept = [
        combined[i]
        for i in range(exc_start, len(combined))
        if i not in rm_indices
    ]

    mid_hand = list(combined)

    triple = (hand_before, mid_hand, after_hand)
    return after_hand, triple, excav_kept


def handle_pot(drawn_cards, card_pool):
    """
    处理抽到的壶，决定加入手卡的逻辑。
    逻辑与旧代码保持一致，仅在实现上做了性能优化。
    """
    # 如果手牌中有“金满壶”
    if any("金满壶" in card for card in drawn_cards):
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)

        # 修改 new_cards 中包含 "手坑" 的元素
        new_cards = [
            card.replace("手坑", "手后坑") if "手坑" in card else card
            for card in new_cards
        ]

        drawn_cards.extend(new_cards)
        return drawn_cards

    # 如果手牌中有“金谦壶”
    if any("金谦壶" in card for card in drawn_cards):
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, pot_card_number)

        has_blob = any("一滴" in card for card in new_cards)
        has_moving = any("动" in card for card in drawn_cards)
        has_recoup = any("补" in card for card in drawn_cards)
        has_trap = any("手坑" in card for card in drawn_cards)
        has_bugu_pa = any("补骨趴" in card for card in drawn_cards)
        has_self = any("本家" in card for card in drawn_cards)

        # 如果没有动卡，找动卡
        if not has_moving:
            for card in new_cards:
                if "动" in card:
                    drawn_cards.append(card)
                    return drawn_cards

        # 如果没有补卡，找补卡
        if not has_recoup:
            for card in new_cards:
                if "补" in card:
                    drawn_cards.append(card)
                    return drawn_cards

        # 如果没有本家，找本家（保留旧逻辑条件判断不变）
        if not has_moving:
            for card in new_cards:
                if "本家" in card:
                    drawn_cards.append(card)
                    return drawn_cards

        # 如果没有手坑，找手坑
        if not has_trap:
            for card in new_cards:
                if "手坑" in card:
                    modified_card = card.replace("手坑", "手后坑")
                    drawn_cards.append(modified_card)
                    return drawn_cards

        # 如果有动卡并且没有补骨趴，找补骨趴
        if has_moving and not has_bugu_pa:
            for card in new_cards:
                if "补骨趴" in card:
                    drawn_cards.append(card)
                    return drawn_cards

        # 如果没有符合条件的卡片，选择第一张卡并加上“后置”前缀
        fallback = new_cards[0]
        if "手坑" in fallback:
            fallback = fallback.replace("手坑", "手后坑")
        drawn_cards.append("后置" + fallback)

    # 如果手牌中有“强贪”
    if any("强贪" in card for card in drawn_cards):
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        remaining_cards = remaining_cards[10:]  # 删除 10 张卡片
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.append("后置" + new_cards[0])

    return drawn_cards


def zizou(drawn_cards, card_pool):
    """
    检测牌型中是否有大于等于1的主音和大于等于2的自奏。
    如果满足条件，则再抽两张牌。
    """
    main_tone_count = sum(1 for card in drawn_cards if "主音" in card)
    self_play_count = sum(1 for card in drawn_cards if "自奏" in card)

    if main_tone_count >= 1 and self_play_count >= 2:
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)

    return drawn_cards


def anchou(drawn_cards, card_pool):
    """
    码丽丝的暗抽。
    """
    main_tone_count = sum(1 for card in drawn_cards if "暗抽" in card)
    self_play_count = sum(1 for card in drawn_cards if "暗" in card)

    if main_tone_count >= 1 and self_play_count >= 2:
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)

    return drawn_cards


def jianshen(drawn_cards, card_pool):
    """
    检测牌型中符合见神启动的牌型。
    如果满足条件，则再抽两张牌。
    """
    main_tone_count = sum(1 for card in drawn_cards if "见神" in card)
    self_play_count = sum(1 for card in drawn_cards if "速攻" in card)
    xuanlan_count = sum(1 for card in drawn_cards if "本家" in card)

    if main_tone_count >= 1 and (self_play_count >= 2 or xuanlan_count >= 2):
        remaining_cards = get_remaining_cards(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)

    return drawn_cards


def simulate_draws(
    card_pool,
    conditions_list,
    enable_going_second=False,
    amphibian_merge_one_rules=(),
    dong_merge_rules=(),
    dai_man_pot_n=None,
):
    """环境变量 PROB_SIM_SEED：若为整数则静默固定 RNG（不改变打印内容）。"""
    _seed_rng_from_env()

    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        dai_man_compare = None
        initial_draw_size = draw_size + (1 if enable_going_second else 0)
        drawn_cards = draw_cards(card_pool, initial_draw_size)
        opening_first_5 = drawn_cards[:draw_size]

        # 后手 yes：仅看最初 5 张起手（第 6 张不参与）；1 张假 g 抽 1，两张及以上假 g 抽 2。
        fake_g_count = sum(1 for card in opening_first_5 if "假g" in card)
        fake_g_draw_times = 0
        if enable_going_second:
            if fake_g_count >= 2:
                fake_g_draw_times = 2
            elif fake_g_count >= 1:
                fake_g_draw_times = 1
        if fake_g_draw_times:
            drawn_cards = handle_fake_g_going_second(
                drawn_cards, card_pool, draw_times=fake_g_draw_times
            )

        drawn_cards = handle_pot(drawn_cards, card_pool)
        drawn_cards = zizou(drawn_cards, card_pool)
        drawn_cards = jianshen(drawn_cards, card_pool)
        drawn_cards = anchou(drawn_cards, card_pool)

        # 开局三才、三号 → 怠慢壶 → 再结算翻出保留的三才/三号。
        # 「已使用」以怠慢壶前的快照为准：仅此前手上也有过三才/三号，壶翻出重复卡才 tier1 洗回。
        used_sancai = any("三才" in c for c in drawn_cards)
        handle_sancai_draw(drawn_cards, card_pool)
        used_sanhao = False
        if enable_going_second:
            used_sanhao = any("三号" in c for c in drawn_cards)
            apply_going_second_sanhao(drawn_cards)

        excav_kept = []
        if dai_man_pot_n is not None:
            drawn_cards, dai_man_compare, excav_kept = handle_dai_man_pot(
                drawn_cards,
                card_pool,
                dai_man_pot_n,
                used_sancai=used_sancai,
                used_sanhao=used_sanhao,
            )
        dai_man_was_used = dai_man_compare is not None

        if any("三才" in c for c in excav_kept):
            handle_sancai_draw(drawn_cards, card_pool)
        if enable_going_second and any("三号" in c for c in excav_kept):
            apply_going_second_sanhao_excavated_only(
                drawn_cards, excav_kept, dai_man_was_used=dai_man_was_used
            )

        matched_condition = None
        for i, condition_set in enumerate(conditions_list):
            if check_conditions(
                drawn_cards,
                condition_set,
                amphibian_merge_one_rules,
                dong_merge_rules,
            ):
                matched_condition = condition_set
                condition_counts[i] += 1
                break

        if draw_num % num_show == 0:
            drawn_cards_snapshots.append(
                (draw_num, drawn_cards[:], matched_condition, dai_man_compare)
            )

    probabilities = {
        i: count / num_draws
        for i, count in condition_counts.items()
    }

    return probabilities, drawn_cards_snapshots


def simulate_and_report(
    card_pool,
    conditions_list,
    title,
    group_sizes,
    enable_going_second=False,
    amphibian_merge_one_rules=(),
    dong_merge_rules=(),
    dai_man_pot_n=None,
):
    """
    进行抽卡模拟，记录每 num_show 次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(
        card_pool,
        conditions_list,
        enable_going_second=enable_going_second,
        amphibian_merge_one_rules=amphibian_merge_one_rules,
        dong_merge_rules=dong_merge_rules,
        dai_man_pot_n=dai_man_pot_n,
    )

    report_drawn_cards(drawn_cards_snapshots, conditions_list)
    report_probabilities(probabilities, conditions_list, title, group_sizes)


def report_drawn_cards(drawn_cards_snapshots, conditions_list):
    """
    输出每 num_show 次抽卡的结果。
    """
    for item in drawn_cards_snapshots:
        draw_num, cards, matched_condition, dai_man_compare = item
        if matched_condition:
            condition_index = conditions_list.index(matched_condition) + 1
            print(f"第 {draw_num} 次抽卡结果: {cards}，符合条件情况: {condition_index}")
        else:
            print(f"第 {draw_num} 次抽卡结果: {cards}，没有匹配的条件")
        if dai_man_compare is not None:
            before_dm, mid_dm, after_dm = dai_man_compare
            print(f"  怠慢壶前手牌: {before_dm}")
            print(f"  怠慢壶翻出未洗回: {mid_dm}")
            print(f"  怠慢壶洗完手牌: {after_dm}")


def report_probabilities(probabilities, conditions_list, title, group_sizes):
    """
    输出每个条件的满足概率，并根据批注(# 开头的行)自动分组，
    打印到每个批注为止的累计概率。
    """
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0.0

    # 先逐个情况打印单独概率
    for i, prob in probabilities.items():
        condition_str = "，".join(
            [f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]]
        )
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob

    print(f"所有情况的总概率为: {total_probability:.2%}")
    print("\n累计概率汇总：")

    # 再根据 group_sizes 汇总每个批注下的累计概率（真正“从头累加”的累计制）
    group_start = 0
    cumulative = 0.0

    for idx, size in enumerate(group_sizes):
        group_end = group_start + size  # 不含 group_end
        if group_end > len(probabilities):
            group_end = len(probabilities)

        if group_end <= group_start:
            continue

        # 本组新增的概率
        group_prob = sum(
            probabilities[i] for i in range(group_start, group_end)
        )
        # 累加到前几组的总和
        cumulative += group_prob

        title_text = title[idx] if idx < len(title) else "无标题"
        print(
            f"前 {group_end} 种情况({title_text})的累计概率为: {cumulative:.2%}"
        )

        group_start = group_end
        if group_start >= len(probabilities):
            break

