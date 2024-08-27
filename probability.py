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
    return random.sample(card_pool, draw_count)


def check_conditions(drawn_cards, conditions):
    """
    检查抽取的卡片是否符合给定条件集合。

    :param drawn_cards: 抽取的卡片列表
    :param conditions: 一个条件集合，包含多个（卡片名称，操作符，值）元组
    :return: 是否满足条件集合的布尔值
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


def simulate_draws(card_pool, conditions_list, num_draws=2000, draw_size=5):
    """
    进行多次抽卡并计算每个条件集合的满足概率。

    :param card_pool: 包含所有卡片的列表
    :param conditions_list: 条件集合列表，每个集合表示一行条件
    :param num_draws: 抽卡次数，默认为500次
    :param draw_size: 每次抽取的卡片数量，默认为5张
    :return: 每个条件集合的满足概率，以及每100次抽卡的牌列表
    """
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        drawn_cards = draw_cards(card_pool, draw_size)

        if draw_num % 500 == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards))

        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                condition_counts[i] += 1
                break  # 一旦满足某个情况，跳出检查，避免重复计数

    probabilities = {i: count / num_draws for i, count in condition_counts.items()}
    return probabilities, drawn_cards_snapshots

def simulate_and_report(card_pool, conditions_list):
    """
    进行抽卡模拟，记录每100次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)

    # 输出每100次抽卡的结果
    report_drawn_cards(drawn_cards_snapshots)

    # 输出每个条件的满足概率
    report_probabilities(probabilities, conditions_list)


def report_drawn_cards(drawn_cards_snapshots):
    """
    输出每100次抽卡的结果。
    """
    for draw_num, cards in drawn_cards_snapshots:
        print(f"第 {draw_num} 次抽卡结果: {cards}")


def report_probabilities(probabilities, conditions_list):
    """
    输出每个条件的满足概率，并计算和输出所有情况的总概率。
    """
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0  # 初始化总概率

    # 输出每个情况的满足概率
    for i, prob in probabilities.items():
        condition_str = "，".join([f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]])
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob  # 累加每个情况的概率

    # 输出总概率
    print(f"所有情况的总概率为: {total_probability:.2%}")
