import random
from collections import Counter
from main import N

draw_size = 5
num_draws = 200000     # 推荐值，误差 ~0.1% 级别

num_show = 10000
pot_card_number = 6

_rng = random.Random()


ALL_KEYWORDS = [
    "金满壶",
    "金谦壶",
    "强贪",
    "动",
    "补",
    "本家",
    "手坑",
    "手后坑",
    "补骨趴",
    "主音",
    "自奏",
    "暗抽",
    "暗",
    "见神",
    "速攻",
]


def init_keyword_counts():
    return {k: 0 for k in ALL_KEYWORDS}


def add_card_to_keyword_counts(card, keyword_counts):
    for kw in ALL_KEYWORDS:
        if kw in card:
            keyword_counts[kw] += 1


def add_cards_to_keyword_counts(cards, keyword_counts):
    for c in cards:
        add_card_to_keyword_counts(c, keyword_counts)


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


def simulate_single_game(card_pool, conditions_list):
    """
    单局模拟：使用“洗牌 + 指针”的方式在同一副牌堆上不放回抽牌，
    逻辑保持与原先 handle_pot / zizou / anchou / jianshen 完全一致。
    """
    # 1. 复制并洗牌
    deck = card_pool[:]
    _rng.shuffle(deck)
    pos = 0

    # 2. 初始化关键字计数
    keyword_counts = init_keyword_counts()

    # 3. 首抽
    drawn_cards = deck[pos:pos + draw_size]
    pos += draw_size
    add_cards_to_keyword_counts(drawn_cards, keyword_counts)

    # 4. 壶相关效果（按照原代码的优先级：金满壶 > 金谦壶 > 强贪）
    has_jinman = keyword_counts.get("金满壶", 0) > 0
    has_jinqian = keyword_counts.get("金谦壶", 0) > 0
    has_qiangtan = keyword_counts.get("强贪", 0) > 0

    if has_jinman:
        # 金满壶：从剩余牌堆顶再摸 2 张，手坑 -> 手后坑
        new_cards = deck[pos:pos + 2]
        pos += 2

        processed = []
        for c in new_cards:
            if "手坑" in c:
                nc = c.replace("手坑", "手后坑")
            else:
                nc = c
            processed.append(nc)
            add_card_to_keyword_counts(nc, keyword_counts)

        drawn_cards.extend(processed)

    elif has_jinqian:
        # 金谦壶：从剩余牌堆顶看 pot_card_number 张，根据原逻辑优先级挑 1 张
        new_cards = deck[pos:pos + pot_card_number]
        pos += pot_card_number

        has_moving = keyword_counts.get("动", 0) > 0
        has_recoup = keyword_counts.get("补", 0) > 0
        has_trap = keyword_counts.get("手坑", 0) > 0 or keyword_counts.get("手后坑", 0) > 0
        has_bugu = keyword_counts.get("补骨趴", 0) > 0
        has_self = keyword_counts.get("本家", 0) > 0

        chosen = None

        if not has_moving:
            for c in new_cards:
                if "动" in c:
                    chosen = c
                    break

        if chosen is None and not has_recoup:
            for c in new_cards:
                if "补" in c:
                    chosen = c
                    break

        if chosen is None and not has_self:
            for c in new_cards:
                if "本家" in c:
                    chosen = c
                    break

        if chosen is None and not has_trap:
            for c in new_cards:
                if "手坑" in c:
                    chosen = c.replace("手坑", "手后坑")
                    break

        if chosen is None and has_moving and not has_bugu:
            for c in new_cards:
                if "补骨趴" in c:
                    chosen = c
                    break

        if chosen is None and new_cards:
            fallback = new_cards[0]
            if "手坑" in fallback:
                fallback = fallback.replace("手坑", "手后坑")
            chosen = "后置" + fallback

        if chosen is not None:
            drawn_cards.append(chosen)
            add_card_to_keyword_counts(chosen, keyword_counts)

    elif has_qiangtan:
        # 强贪：跳过 10 张（除外），再摸 2 张，手上只加 1 张（加“后置”前缀）
        pos += 10
        new_cards = deck[pos:pos + 2]
        pos += 2
        if new_cards:
            chosen = "后置" + new_cards[0]
            drawn_cards.append(chosen)
            add_card_to_keyword_counts(chosen, keyword_counts)

    # 5. 追加抽卡：自奏 / 暗抽 / 见神，保持原有条件和顺序
    if keyword_counts.get("主音", 0) >= 1 and keyword_counts.get("自奏", 0) >= 2:
        extra = deck[pos:pos + 2]
        pos += 2
        drawn_cards.extend(extra)
        add_cards_to_keyword_counts(extra, keyword_counts)

    if keyword_counts.get("暗抽", 0) >= 1 and keyword_counts.get("暗", 0) >= 2:
        extra = deck[pos:pos + 2]
        pos += 2
        drawn_cards.extend(extra)
        add_cards_to_keyword_counts(extra, keyword_counts)

    js = keyword_counts.get("见神", 0)
    fast = keyword_counts.get("速攻", 0)
    home = keyword_counts.get("本家", 0)
    if js >= 1 and (fast >= 2 or home >= 2):
        extra = deck[pos:pos + 2]
        pos += 2
        drawn_cards.extend(extra)
        add_cards_to_keyword_counts(extra, keyword_counts)

    # 6. 检查条件列表，按优先级找到第一个匹配的情况
    matched_index = None
    matched_condition = None

    for i, cond in enumerate(conditions_list):
        if check_conditions(drawn_cards, cond):
            matched_index = i
            matched_condition = cond
            break

    return matched_index, matched_condition, drawn_cards


def simulate_draws(card_pool, conditions_list):
    condition_counts = {i: 0 for i in range(len(conditions_list))}
    drawn_cards_snapshots = []

    for draw_num in range(1, num_draws + 1):
        matched_index, matched_condition, drawn_cards = simulate_single_game(card_pool, conditions_list)

        if matched_index is not None:
            condition_counts[matched_index] += 1

        if draw_num % num_show == 0:
            drawn_cards_snapshots.append((draw_num, drawn_cards[:], matched_condition))

    probabilities = {
        i: count / num_draws
        for i, count in condition_counts.items()
    }

    return probabilities, drawn_cards_snapshots


def simulate_and_report(card_pool, conditions_list, title):

    probabilities, drawn_cards_snapshots = simulate_draws(card_pool, conditions_list)

    report_drawn_cards(drawn_cards_snapshots, conditions_list)

    report_probabilities(probabilities, conditions_list, title)


def report_drawn_cards(drawn_cards_snapshots, conditions_list):

    for draw_num, cards, matched_condition in drawn_cards_snapshots:

        if matched_condition:

            idx = conditions_list.index(matched_condition) + 1

            print(f"第 {draw_num} 次抽卡结果: {cards}，符合条件情况: {idx}")

        else:

            print(f"第 {draw_num} 次抽卡结果: {cards}，没有匹配的条件")


def report_probabilities(probabilities, conditions_list, title):

    print("抽卡结束，满足条件的概率如下：")

    total = 0
    cumulative = 0
    cumulative_list = []

    for i, prob in probabilities.items():

        cond_str = "，".join(
            [f"{p[0]} {p[1]} {p[2]}" for p in conditions_list[i]]
        )

        print(f"情况{i+1}: {cond_str} 的概率为 {prob:.2%}")

        total += prob
        cumulative += prob

        if (i + 1) % N == 0:

            print(f"前 {i+1} 种情况的累计概率为: {cumulative:.2%}")

            cumulative_list.append(cumulative)

    if len(probabilities) % N != 0:

        print(f"前 {len(probabilities)} 种情况的累计概率为: {cumulative:.2%}")

        cumulative_list.append(cumulative)

    print(f"所有情况的总概率为: {total:.2%}")

    print("\n累计概率汇总：")

    if len(cumulative_list) == 1:

        print(f"累计概率为: {cumulative_list[0]:.2%}")

    else:

        for i, prob in enumerate(cumulative_list, start=1):

            title_text = title[i-1] if i-1 < len(title) else "无标题"

            count_text = min(i * N, len(probabilities))

            print(f"前 {count_text} 种情况({title_text})的累计概率为: {prob:.2%}")

