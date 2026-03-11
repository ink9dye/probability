import secrets
from collections import Counter
from main import N

draw_size = 5
num_draws = 200000

# 定义全局变量 num_show，用于每次输出抽样结果的步长
num_show = 10000

# 定义全局变量 pot_card_number，控制壶抽取的数量
pot_card_number = 6

# 全局安全随机生成器：只创建一次
_rand = secrets.SystemRandom()


def draw_cards(card_pool, draw_count):
    """
    从卡池中随机抽取指定数量的卡片。
    使用系统安全随机源，不手动 seed。
    """
    if len(card_pool) < draw_count:
        raise ValueError("卡池中的卡片数量不足以抽取指定数量的卡片")

    return _rand.sample(card_pool, draw_count)


def check_conditions(drawn_cards, conditions):
    """
    检查抽取的卡片是否符合给定条件集合。
    """
    card_counts = Counter()

    for card in drawn_cards:
        for card_name, operator, value in conditions:
            if card_name in card:
                card_counts[card_name] += 1

    for card_name, operator, value in conditions:
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


def remove_drawn_from_pool(card_pool, drawn_cards):
    """
    从卡池中移除已抽到的卡。
    这里按“值”移除，与原逻辑保持一致。
    """
    drawn_set = set(drawn_cards)
    return [card for card in card_pool if card not in drawn_set]


def handle_pot(drawn_cards, card_pool):
    """
    处理抽到的壶，决定加入手卡的逻辑。
    """
    # 如果手牌中有“金满壶”
    if any("金满壶" in card for card in drawn_cards):
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)

        # 修改 new_cards 中包含 "手坑" 的元素
        new_cards = [
            card.replace("手坑", "手后坑") if "手坑" in card else card
            for card in new_cards
        ]

        drawn_cards.extend(new_cards)  # 将新抽的牌加入手牌
        return drawn_cards

    # 如果手牌中有“金谦壶”
    if any("金谦壶" in card for card in drawn_cards):
        # 从剩余的卡中抽取指定数量的卡片（由全局变量 pot_card_number 控制）
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, pot_card_number)

        # 检查当前手牌中是否有特定的卡片
        has_blob = any("一滴" in card for card in new_cards)   # 保留你的变量，虽然当前未参与判断
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

        # 如果没有本家，找本家
        if not has_self:
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
        fallback_card = new_cards[0]
        if "手坑" in fallback_card:
            fallback_card = fallback_card.replace("手坑", "手后坑")
        drawn_cards.append("后置" + fallback_card)

    # 如果手牌中有“强贪”
    if any("强贪" in card for card in drawn_cards):
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)

        # 删除10张卡片
        remaining_cards = remaining_cards[10:]

        # 抽取两张卡
        new_cards = draw_cards(remaining_cards, 2)

        # 你原代码只加入第一张，并加“后置”前缀；这里保持原逻辑
        drawn_cards.append("后置" + new_cards[0])

    return drawn_cards  # 返回最终的手卡


def zizou(drawn_cards, card_pool):
    """
    检测牌型中是否有大于等于1的主音和大于等于2的自奏。
    如果满足条件，则再抽两张牌。
    """
    main_tone_count = sum(1 for card in drawn_cards if "主音" in card)
    self_play_count = sum(1 for card in drawn_cards if "自奏" in card)

    if main_tone_count >= 1 and self_play_count >= 2:
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)

    return drawn_cards


def anchou(drawn_cards, card_pool):
    """
    码丽丝的暗抽
    """
    main_tone_count = sum(1 for card in drawn_cards if "暗抽" in card)
    self_play_count = sum(1 for card in drawn_cards if "暗" in card)

    if main_tone_count >= 1 and self_play_count >= 2:
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)
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

    # 有1张见神 AND (有2张速攻 OR 有2张本家)
    if main_tone_count >= 1 and (self_play_count >= 2 or xuanlan_count >= 2):
        remaining_cards = remove_drawn_from_pool(card_pool, drawn_cards)
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)

    return drawn_cards


def simulate_draws(card_pool, conditions_list):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        drawn_cards = draw_cards(card_pool, draw_size)
        drawn_cards = handle_pot(drawn_cards, card_pool)
        drawn_cards = zizou(drawn_cards, card_pool)
        drawn_cards = jianshen(drawn_cards, card_pool)
        drawn_cards = anchou(drawn_cards, card_pool)

        matched_condition = None
        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                matched_condition = condition_set
                condition_counts[i] += 1
                break

        if draw_num % num_show == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards[:], matched_condition))

    probabilities = {i: count / num_draws for i, count in condition_counts.items()}
    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list, title):
    """
    进行抽卡模拟，记录每 num_show 次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)

    # 输出每 num_show 次抽卡的结果
    report_drawn_cards(drawn_cards_snapshots, conditions_list)

    # 输出每个条件的满足概率
    report_probabilities(probabilities, conditions_list, title)


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


def report_probabilities(probabilities, conditions_list, title):
    """
    输出每个条件的满足概率，并计算和输出每前 N 种情况的累计概率。
    """
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0
    cumulative_probability = 0
    cumulative_probabilities = []

    for i, prob in probabilities.items():
        condition_str = "，".join(
            [f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]]
        )
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob
        cumulative_probability += prob

        # 当达到第 N、2N、3N...次时，输出累计概率，并保存到列表
        if (i + 1) % N == 0:
            print(f"前 {i + 1} 种情况的累计概率为: {cumulative_probability:.2%}")
            cumulative_probabilities.append(cumulative_probability)

    # 最后输出不足 N 的尾部累计概率
    if len(probabilities) % N != 0:
        print(f"前 {len(probabilities)} 种情况的累计概率为: {cumulative_probability:.2%}")
        cumulative_probabilities.append(cumulative_probability)

    print(f"所有情况的总概率为: {total_probability:.2%}")

    print("\n累计概率汇总：")

    if len(cumulative_probabilities) == 1:
        print(f"累计概率为: {cumulative_probabilities[0]:.2%}")
    else:
        for i, prob in enumerate(cumulative_probabilities, start=1):
            title_text = title[i - 1] if i - 1 < len(title) else "无标题"

            # 最后一组可能不是 i*N，而是实际总数
            if i * N < len(probabilities):
                count_text = i * N
            else:
                count_text = len(probabilities)

            print(f"前 {count_text} 种情况({title_text})的累计概率为: {prob:.2%}")