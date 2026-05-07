import random
from collections import Counter

draw_size = 5
num_draws = 300000     # 经验上误差约在 0.1% 左右
num_show = 30000
pot_card_number = 6

_rng = random.Random()

# 「前缀-种类」：后缀固定为半角 -种类；度量为手牌中含该前缀的不同牌名种数（同名多张只算 1）
_KIND_SUFFIX = "-种类"


def _is_kind_condition(card_name):
    return card_name.endswith(_KIND_SUFFIX) and len(card_name) > len(_KIND_SUFFIX)


def _kind_prefix(card_name):
    return card_name[: -len(_KIND_SUFFIX)]


def _special_condition_value(card_name, drawn_cards):
    """
    返回保留条件名对应的度量；未知名返回 None，由调用方回退到普通子串计数。

    {前缀}-种类：牌名字符串包含「前缀」的不同牌名种数（用于避免两张同名牌计成两种）。
    """
    if _is_kind_condition(card_name):
        prefix = _kind_prefix(card_name)
        if not prefix:
            return None
        return len({c for c in drawn_cards if prefix in c})
    return None


def _skip_substring_count(card_name):
    """不参与「子串出现次数」累加的条件名。"""
    return _is_kind_condition(card_name)


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
    启动处理结束后，若手牌中存在包含“假g”的卡，则视为“抽到就抽一”（类似壶），
    从剩余卡组随机抽若干张，并以“后置”前缀加入手牌（不替换/不移除原“假g”卡）。
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


def check_conditions(drawn_cards, conditions):
    """
    检查抽取的卡片是否符合给定条件集合。
    普通项：统计手牌中「牌名字符串包含 card_name 子串」的张数。
    保留项：{前缀}-种类 — 见 _special_condition_value。
    """
    card_counts = Counter()

    for card in drawn_cards:
        for card_name, operator, value in conditions:
            if _skip_substring_count(card_name):
                continue
            if card_name in card:
                card_counts[card_name] += 1

    for card_name, operator, value in conditions:
        special = _special_condition_value(card_name, drawn_cards)
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


def simulate_draws(card_pool, conditions_list, enable_going_second=False):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        initial_draw_size = draw_size + (1 if enable_going_second else 0)
        drawn_cards = draw_cards(card_pool, initial_draw_size)
        # 后手第六抽（额外起手那张）不计入“假g 触发抽一”的判定：只看前 5 张起手。
        fake_g_count = sum(1 for card in drawn_cards[:draw_size] if "假g" in card)
        fake_g_draw_times = 0
        if enable_going_second:
            if fake_g_count >= 2:
                fake_g_draw_times = 2
            elif fake_g_count == 1:
                fake_g_draw_times = 1
        drawn_cards = handle_pot(drawn_cards, card_pool)
        drawn_cards = zizou(drawn_cards, card_pool)
        drawn_cards = jianshen(drawn_cards, card_pool)
        drawn_cards = anchou(drawn_cards, card_pool)
        if fake_g_draw_times:
            drawn_cards = handle_fake_g_going_second(
                drawn_cards, card_pool, draw_times=fake_g_draw_times
            )

        matched_condition = None
        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                matched_condition = condition_set
                condition_counts[i] += 1
                break

        if draw_num % num_show == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards[:], matched_condition))

    probabilities = {
        i: count / num_draws
        for i, count in condition_counts.items()
    }

    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list, title, group_sizes, enable_going_second=False):
    """
    进行抽卡模拟，记录每 num_show 次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(
        card_pool, conditions_list, enable_going_second=enable_going_second
    )

    report_drawn_cards(drawn_cards_snapshots, conditions_list)
    report_probabilities(probabilities, conditions_list, title, group_sizes)


def report_drawn_cards(drawn_cards_snapshots, conditions_list):
    """
    输出每 num_show 次抽卡的结果。
    """
    for draw_num, cards, matched_condition in drawn_cards_snapshots:
        if matched_condition:
            condition_index = conditions_list.index(matched_condition) + 1
            print(f"第 {draw_num} 次抽卡结果: {cards}，符合条件情况: {condition_index}")
        else:
            print(f"第 {draw_num} 次抽卡结果: {cards}，没有匹配的条件")


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

