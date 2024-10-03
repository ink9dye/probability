import random
from collections import Counter


def draw_cards(card_pool, draw_count=5):
    """
    从卡池中随机抽取指定数量的卡片。
    """
    if len(card_pool) < draw_count:
        raise ValueError("卡池中的卡片数量不足以抽取指定数量的卡片")

    # 使用 SystemRandom 提高随机性
    rand = random.SystemRandom()
    return rand.sample(card_pool, draw_count)


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


# 定义全局变量 pot_card_number，控制壶抽取的数量
pot_card_number = 3

def handle_pot(drawn_cards, card_pool):
    """
    处理抽到的壶，决定加入手卡的逻辑。
    """
    if any("壶" in card for card in drawn_cards):
        # 从剩余的卡中抽取指定数量的卡片（由全局变量 pot_card_number 控制）
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, pot_card_number)

        has_moving = any("动" in card for card in drawn_cards)  # 检查是否有"动"卡
        has_bugu_pa = any("补骨趴" in card for card in drawn_cards)  # 检查是否有"补骨趴"

        if not has_moving:  # 无动，找动
            for card in new_cards:
                if "动" in card:
                    drawn_cards.append(card)
                    return drawn_cards

        if has_moving and not has_bugu_pa:  # 有动，无补骨趴，找补骨趴
            for card in new_cards:
                if "补骨趴" in card:
                    drawn_cards.append(card)
                    return drawn_cards
        # if has_moving and has_bugu_pa:  # 有动且有补骨趴，找手坑并加后置前缀
        #     for card in new_cards:
        #         if "系统外" in card:
        #             drawn_cards.append(card)
        #             return drawn_cards
        if has_moving and has_bugu_pa:  # 有动且有补骨趴，找手坑并加后置前缀
            for card in new_cards:
                if "手坑" in card:
                    selected_card = card.replace("手坑", "手后坑")
                    drawn_cards.append("后置" + selected_card)
                    return drawn_cards


        # 如果没有符合条件的，选第一张卡并加上“后置”前缀
        drawn_cards.append("后置" + new_cards[0])
        return drawn_cards

    return drawn_cards  # 如果没有“壶”，返回原始手卡


def simulate_draws(card_pool, conditions_list, num_draws=200000, draw_size=5):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        drawn_cards = draw_cards(card_pool, draw_size)
        drawn_cards = handle_pot(drawn_cards, card_pool)

        matched_condition = None
        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                matched_condition = condition_set  # 直接存储条件集合
                condition_counts[i] += 1
                break

        if draw_num % 20000 == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards, matched_condition))

    probabilities = {i: count / num_draws for i, count in condition_counts.items()}
    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list):
    """
    进行抽卡模拟，记录每20000次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)

    # 输出每20000次抽卡的结果
    report_drawn_cards(drawn_cards_snapshots, conditions_list)

    # 输出每个条件的满足概率
    report_probabilities(probabilities, conditions_list)


def report_drawn_cards(drawn_cards_snapshots, conditions_list):
    """
    输出每20000次抽卡的结果。
    """
    for draw_num, cards, matched_condition in drawn_cards_snapshots:
        if matched_condition:
            condition_index = conditions_list.index(matched_condition) + 1  # 找到符合的条件情况的索引
            print(f"第 {draw_num} 次抽卡结果: {cards}，符合条件情况: {condition_index}")
        else:
            print(f"第 {draw_num} 次抽卡结果: {cards}，没有匹配的条件")




# 定义全局变量 N，用于每次输出累计概率的步长
N = 5  # 例如每次统计前5种情况的累计概率

def report_probabilities(probabilities, conditions_list):
    """
    输出每个条件的满足概率，并计算和输出每前N种情况的累计概率。
    """
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0  # 初始化总概率
    cumulative_probability = 0  # 用于累计前N个情况的概率

    # 遍历每个情况的满足概率
    for i, prob in probabilities.items():
        condition_str = "，".join([f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]])
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob  # 累加每个情况的概率
        cumulative_probability += prob  # 累加前 N 种情况的概率

        # 当达到第 N、2N、3N...次时，输出累计概率
        if (i + 1) % N == 0:
            print(f"前 {i + 1} 种情况的累计概率为: {cumulative_probability:.2%}")

    # 最后输出总的累计概率
    if len(probabilities) % N != 0:
        print(f"前 {len(probabilities)} 种情况的累计概率为: {cumulative_probability:.2%}")

    # 输出总概率
    print(f"所有情况的总概率为: {total_probability:.2%}")