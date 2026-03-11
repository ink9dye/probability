import random
from collections import Counter
import secrets
import time
draw_size=5
num_draws=200000
# 定义全局变量 N，用于每次输出累计概率的步长
num_show=10000
from main import N
# 定义全局变量 pot_card_number，控制壶抽取的数量
pot_card_number = 6

def draw_cards(card_pool, draw_count):
    """
    从卡池中随机抽取指定数量的卡片，使用加密安全的随机生成器，并通过引入系统熵源增加随机性。
    """
    if len(card_pool) < draw_count:
        raise ValueError("卡池中的卡片数量不足以抽取指定数量的卡片")

    # 使用加密安全的 SystemRandom 生成器
    rand = secrets.SystemRandom()

    # 引入更多熵源：当前时间的微秒数
    time_entropy = time.time_ns() % (10 ** 6)  # 微秒级别的熵
    rand.seed(time_entropy)  # 为生成器附加更多熵

    # 直接随机抽取卡片
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


def handle_pot(drawn_cards, card_pool):
    """
    处理抽到的壶，决定加入手卡的逻辑。
    """
    if any("金满壶" in card for card in drawn_cards):
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, 2)

        # 修改 new_cards 中包含 "手坑" 的元素
        new_cards = [card.replace("手坑", "手后坑") if "手坑" in card else card for card in new_cards]

        drawn_cards.extend(new_cards)  # 将新抽的牌加入手牌
        return drawn_cards

    # 如果手牌中有“金谦壶”
    if any("金谦壶" in card for card in drawn_cards):
        # 从剩余的卡中抽取指定数量的卡片（由全局变量 pot_card_number 控制）
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, pot_card_number)

        # 检查当前手牌中是否有特定的卡片
        has_blob = any("一滴" in card for card in new_cards)
        has_moving = any("动" in card for card in drawn_cards)  # 检查是否有"动"卡
        has_recoup = any("补" in card for card in drawn_cards)
        has_trap = any("手坑" in card for card in drawn_cards)
        has_bugu_pa = any("补骨趴" in card for card in drawn_cards)  # 检查是否有"补骨趴"
        has_self=any("本家" in card for card in drawn_cards)

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
        if "手坑" in new_cards[0]:
            new_cards[0] = new_cards[0].replace("手坑", "手后坑")
        drawn_cards.append("后置" + new_cards[0])

    # 如果手牌中有“强贪”
    if any("强贪" in card for card in drawn_cards):
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        # 删除10张卡片
        remaining_cards = remaining_cards[10:]
        # 抽取两张卡
        new_cards = draw_cards(remaining_cards, 2)
        # 加上“后置”前缀并加入手卡
        drawn_cards.append("后置" + new_cards[0])

    return drawn_cards  # 返回最终的手卡


def zizou(drawn_cards, card_pool):
    """
    检测牌型中是否有大于等于1的主音和大于等于2的自奏。
    如果满足条件，则再抽两张牌。
    """
    # 统计主音和自奏的数量
    main_tone_count = sum(1 for card in drawn_cards if "主音" in card)
    self_play_count = sum(1 for card in drawn_cards if "自奏" in card)

    # 如果满足条件，再抽两张牌
    if main_tone_count >= 1 and self_play_count >= 2:
        # 从剩余的卡中抽取两张新卡
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)  # 将新抽的牌加入手牌

    return drawn_cards

def anchou(drawn_cards, card_pool):
    """
    码丽丝的暗抽
    """
    # 统计主音和自奏的数量
    main_tone_count = sum(1 for card in drawn_cards if "暗抽" in card)
    self_play_count = sum(1 for card in drawn_cards if "暗" in card)

    # 如果满足条件，再抽两张牌
    if main_tone_count >= 1 and self_play_count >= 2:
        # 从剩余的卡中抽取两张新卡
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)  # 将新抽的牌加入手牌

    return drawn_cards

def jianshen(drawn_cards, card_pool):
    """
    检测牌型中符合见神启动的牌型
    如果满足条件，则再抽两张牌。
    """
    # 统计见神、速攻和绚岚的数量
    main_tone_count = sum(1 for card in drawn_cards if "见神" in card)
    self_play_count = sum(1 for card in drawn_cards if "速攻" in card)
    xuanlan_count = sum(1 for card in drawn_cards if "本家" in card)

    # 修改条件：有1张见神 AND (有2张速攻 OR 有2张绚岚)
    if main_tone_count >= 1 and (self_play_count >= 2 or xuanlan_count >= 2):
        # 从剩余的卡中抽取两张新卡
        remaining_cards = [card for card in card_pool if card not in drawn_cards]
        new_cards = draw_cards(remaining_cards, 2)
        drawn_cards.extend(new_cards)  # 将新抽的牌加入手牌

    return drawn_cards


def simulate_draws(card_pool, conditions_list):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        drawn_cards = draw_cards(card_pool, draw_size)
        drawn_cards = handle_pot(drawn_cards, card_pool)
        drawn_cards = zizou(drawn_cards, card_pool)  # 调用 zizou 函数
        drawn_cards = jianshen(drawn_cards, card_pool)  # 调用 jianshen函数
        drawn_cards = anchou(drawn_cards, card_pool)  # 调用 anchou 函数

        matched_condition = None
        for i, condition_set in enumerate(conditions_list):
            if check_conditions(drawn_cards, condition_set):
                matched_condition = condition_set  # 直接存储条件集合
                condition_counts[i] += 1
                break

        if draw_num % num_show == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards, matched_condition))

    probabilities = {i: count / num_draws for i, count in condition_counts.items()}
    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list,title):
    """
    进行抽卡模拟，记录每20000次的抽卡结果，并输出每个条件的满足概率。
    """
    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)

    # 输出每20000次抽卡的结果
    report_drawn_cards(drawn_cards_snapshots, conditions_list)

    # 输出每个条件的满足概率
    report_probabilities(probabilities, conditions_list,title)


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






def report_probabilities(probabilities, conditions_list,title):
    """
    输出每个条件的满足概率，并计算和输出每前N种情况的累计概率。
    """
    print("抽卡结束，满足条件的概率如下：")

    total_probability = 0  # 初始化总概率
    cumulative_probability = 0  # 用于累计前N个情况的概率
    cumulative_probabilities = []  # 用于存储每N种情况的累计概率

    # 遍历每个情况的满足概率
    for i, prob in probabilities.items():
        condition_str = "，".join([f"{part[0]} {part[1]} {part[2]}" for part in conditions_list[i]])
        print(f"情况{i + 1}: {condition_str} 的概率为 {prob:.2%}")
        total_probability += prob  # 累加每个情况的概率
        cumulative_probability += prob  # 累加前 N 种情况的概率

        # 当达到第 N、2N、3N...次时，输出累计概率，并保存到列表
        if (i + 1) % N == 0:
            print(f"前 {i + 1} 种情况的累计概率为: {cumulative_probability:.2%}")
            cumulative_probabilities.append(cumulative_probability)

    # 最后输出总的累计概率
    if len(probabilities) % N != 0:
        print(f"前 {len(probabilities)} 种情况的累计概率为: {cumulative_probability:.2%}")
        cumulative_probabilities.append(cumulative_probability)

    # 输出总概率
    print(f"所有情况的总概率为: {total_probability:.2%}")

    # 循环打印前 N、2N、3N...的累计概率
    print("\n累计概率汇总：")

    # 当累计概率只有一个时，直接输出
    if len(cumulative_probabilities) == 1:
        print(f"累计概率为: {cumulative_probabilities[0]:.2%}")
    else:
        # 循环输出每组的累计概率
        for i, prob in enumerate(cumulative_probabilities, start=1):
            title_text = title[i - 1] if i - 1 < len(title) else "无标题"
            print(f"前 {i * N} 种情况({title_text})的累计概率为: {prob:.2%}")
