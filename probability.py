import random
from collections import Counter


def draw_cards(card_pool, draw_count=5):
    """
    从卡池中随机抽取指定数量的卡片。

    :param card_pool: 包含所有卡片的列表
    :param draw_count: 每次抽取的卡片数量，默认为5
    :return: 抽取的卡片列表
    """
    if len(card_pool) < draw_count:
        raise ValueError("卡池中的卡片数量不足以抽取指定数量的卡片")

    # 使用 SystemRandom 提高随机性
    rand = random.SystemRandom()
    return rand.sample(card_pool, draw_count)



def check_conditions(drawn_cards, conditions):
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


def simulate_draws(card_pool, conditions_list, num_draws=200000, draw_size=5):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        drawn_cards = draw_cards(card_pool, draw_size)
        matched_condition = None

        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                matched_condition = (i + 1, condition_set)  # 记录符合的条件
                condition_counts[i] += 1
                break  # 一旦满足某个条件，跳出检查

        if draw_num % 20000 == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards, matched_condition))

    probabilities = {i: count / num_draws for i, count in condition_counts.items()}
    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list):
    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)
    report_drawn_cards(drawn_cards_snapshots)
    report_probabilities(probabilities, conditions_list)


def report_drawn_cards(drawn_cards_snapshots):
    for draw_num, cards, matched_condition in drawn_cards_snapshots:
        if matched_condition:
            condition_index, condition_set = matched_condition
            condition_str = "，".join([f"{part[0]} {part[1]} {part[2]}" for part in condition_set])
            print(f"第 {draw_num} 次抽卡结果: {cards}，符合条件 {condition_index}: {condition_str}")
        else:
            print(f"第 {draw_num} 次抽卡结果: {cards}，不符合任何条件")


def report_probabilities(probabilities, conditions_list):
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0
    for i, prob in probabilities.items():
        condition_str = "，".join([f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]])
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob

    print(f"所有情况的总概率为: {total_probability:.2%}")
