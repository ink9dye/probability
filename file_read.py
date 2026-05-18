import re

# 启动文件中「@规则」所用分隔符（与卡组行一致）
_SEPARATOR_PATTERN = r'[，,、．.]'

# @两栖齐现只算一张，牌名A，牌名B，… —— 所列卡池牌名均在同一手牌中至少各 1 张时：
# 计「两栖」「魔牌两栖」子串张数时，该组内凡名字含对应子串的张合并为只算 1；
# 「两栖-种类」中凡落在该组的不同牌名也合并为只算 1 种。（全局生效，不限分组标题）
RULE_AMPHIBIAN_MERGE_ONE = "两栖齐现只算一张"

# @齐现只算一张动，牌名A，牌名B，… —— 当所列卡池牌名均在同一手牌中至少各 1 张时：
# 统计启动条件里的「动」（子串名恰好为「动」）时，该组牌整体只贡献 1：含「动」子串的张若多张则合并为 1；
# 若该组内无任何张含「动」子串，则视为虚拟 1 张动（满足皇子+皇国、场地+签章等命名）。
RULE_DONG_MERGE = "齐现只算一张动"


def _parse_at_rule_line(line, amphibian_merge_one_rules, dong_merge_rules):
    """
    解析以 @ 开头的规则行；不识别的规则名打印警告。
    """
    body = line[1:].strip()
    if not body:
        print(f"规则行为空: {line}")
        return
    parts = [p.strip() for p in re.split(_SEPARATOR_PATTERN, body) if p.strip()]
    if len(parts) < 3:
        print(f"规则行至少需要「规则名 + 两张牌名」: {line}")
        return
    rule_name = parts[0]
    card_names = tuple(parts[1:])
    if rule_name == RULE_AMPHIBIAN_MERGE_ONE:
        amphibian_merge_one_rules.append(card_names)
    elif rule_name == RULE_DONG_MERGE:
        dong_merge_rules.append(card_names)
    else:
        print(f"未知 @ 规则类型「{rule_name}」: {line}")


def parse_first_document(file_content):
    """
    解析第一个文档，生成卡池列表，并显示卡组总数。
    忽略以#开头的文本行。

    :param file_content: 文档内容字符串，每行包含卡片名称和数量。
    :return: 包含卡片的列表，卡片按照数量重复。
    """
    card_pool = []
    for line in file_content.strip().split('\n'):
        line = line.strip()

        # 忽略以#开头的行
        if line.startswith('#'):
            continue

        try:
            # 按照不同的分隔符分割卡片名称和数量
            card_name, count = re.split(_SEPARATOR_PATTERN, line)
            card_pool.extend([card_name.strip()] * int(count.strip()))
        except ValueError as e:
            print(f"Error processing line: {line} - {e}")

    # 计算并显示卡组总数
    total_cards = len(card_pool)
    print(f"卡组总数: {total_cards}")

    return card_pool


def parse_second_document(file_content):
    """
    解析第二个文档，生成条件列表，并根据 # 批注自动分组。

    以 @ 开头的行：扩展规则（不计入条件分组）。当前支持：
      @两栖齐现只算一张，卡池牌名A，卡池牌名B，…
      @齐现只算一张动，卡池牌名A，卡池牌名B，…

    :param file_content: 文档内容字符串，每行包含多个条件信息或批注。
        条件为三字段一组：条件名，运算符，整数阈值；多条条件在同一行用逗号类分隔符串联。
        「前缀-种类」可用加号（+ 或 ＋）连接多项求和，例如：两栖-种类+后手-种类，大于等于，3
    :return:
        conditions_list: 扁平的条件列表（每一行条件是一种情况）
        group_sizes: 每个批注(# 开头的行)下面包含的有效情况行数
        amphibian_merge_one_rules: list[tuple[str, ...]]，两栖齐现只算一张规则列表
        dong_merge_rules: list[tuple[str, ...]]，齐现只算一张动规则列表
    """
    conditions_list = []
    group_sizes = []
    amphibian_merge_one_rules = []
    dong_merge_rules = []
    current_group_index = -1

    separator_pattern = _SEPARATOR_PATTERN

    for raw_line in file_content.split('\n'):
        line = raw_line.strip()
        if not line:  # 跳过空行
            continue

        if line.startswith('@'):
            _parse_at_rule_line(line, amphibian_merge_one_rules, dong_merge_rules)
            continue

        # 批注行，作为新的分组开始
        if line.startswith('#'):
            current_group_index += 1
            group_sizes.append(0)
            continue

        parts = re.split(separator_pattern, line)
        line_conditions = []
        if len(parts) % 3 != 0:  # 如果行的数据长度不符合预期，则打印并跳过
            print(f"输出情况（格式不符）: {line}")
            continue

        for i in range(0, len(parts), 3):
            try:
                card_name = parts[i].strip()
                operator = parts[i + 1].strip()
                value = int(parts[i + 2].strip())
                line_conditions.append((card_name, operator, value))
            except ValueError as e:
                print(f"报错: {line} - {e}")

        if line_conditions:
            conditions_list.append(line_conditions)
            # 将这一行计入当前批注分组
            if current_group_index >= 0:
                group_sizes[current_group_index] += 1
            else:
                # 处理在首个批注之前就有条件行的极端情况
                if not group_sizes:
                    group_sizes.append(0)
                    current_group_index = 0
                group_sizes[current_group_index] += 1

    return conditions_list, group_sizes, amphibian_merge_one_rules, dong_merge_rules

def read_file(file_path):
    """
    读取文件内容，并返回内容字符串。如果文件不存在，返回 None。
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")
        return None


def parse_documents(first_document_content, second_document_content):
    """
    解析第一个和第二个文档，返回卡池列表、条件列表、分组尺寸与 @ 规则。
    """
    card_pool = parse_first_document(first_document_content)
    conditions_list, group_sizes, amphibian_merge_one_rules, dong_merge_rules = (
        parse_second_document(second_document_content)
    )
    return (
        card_pool,
        conditions_list,
        group_sizes,
        amphibian_merge_one_rules,
        dong_merge_rules,
    )


def get_comment_lines(file_path):
    """
    读取文件并返回所有以 # 开头的注释行。

    :param file_path: 文档的文件路径。
    :return: 包含所有注释行的列表，每行以 # 开头。
    """
    comment_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 读取文件并逐行检查
            for line in f:
                if line.startswith('#'):  # 如果该行是注释行
                    comment_lines.append(line.strip())
    except FileNotFoundError:
        print(f"错误：找不到文件 {file_path}")

    return comment_lines