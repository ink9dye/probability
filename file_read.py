import re


def parse_first_document(file_content):
    """
    解析第一个文档，生成卡池列表，并显示卡组总数。

    :param file_content: 文档内容字符串，每行包含卡片名称和数量。
    :return: 包含卡片的列表，卡片按照数量重复。
    """
    card_pool = []
    for line in file_content.strip().split('\n'):
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
    解析第二个文档，生成按行分组的条件列表。

    :param file_content: 文档内容字符串，每行包含多个条件信息。
    :return: 包含条件集合的列表，每个条件集合由卡片名称、操作符和目标值组成的元组列表。
    """
    conditions_list = []
    separator_pattern = r'[，,、．.]'  # 匹配中英文逗号、顿号、句号等分隔符

    for line in file_content.strip().split('\n'):
        parts = re.split(separator_pattern, line)
        line_conditions = []
        for i in range(0, len(parts), 3):
            if i + 2 < len(parts):
                try:
                    card_name = parts[i].strip()
                    operator = parts[i + 1].strip()
                    value = int(parts[i + 2].strip())
                    line_conditions.append((card_name, operator, value))
                except ValueError as e:
                    print(f"报错: {line} - {e}")
            else:
                print(f"输出情况: {line}")
        if line_conditions:
            conditions_list.append(line_conditions)

    return conditions_list

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
    conditions_list = parse_second_document(second_document_content)
    return card_pool, conditions_list
