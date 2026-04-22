import re


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
            card_name, count = re.split(r'[，,、．.]', line)
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

    :param file_content: 文档内容字符串，每行包含多个条件信息或批注。
    :return:
        conditions_list: 扁平的条件列表（每一行条件是一种情况）
        group_sizes: 每个批注(# 开头的行)下面包含的有效情况行数
    """
    conditions_list = []
    group_sizes = []
    current_group_index = -1

    separator_pattern = r'[，,、．.]'  # 匹配中英文逗号、顿号、句号等分隔符

    for raw_line in file_content.split('\n'):
        line = raw_line.strip()
        if not line:  # 跳过空行
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

    return conditions_list, group_sizes

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
    解析第一个和第二个文档，返回卡池列表和条件列表。
    """
    card_pool = parse_first_document(first_document_content)
    conditions_list, group_sizes = parse_second_document(second_document_content)
    return card_pool, conditions_list, group_sizes


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