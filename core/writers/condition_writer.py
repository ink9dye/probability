# writers/condition_writer.py

from utils.file_utils import write_to_file


def write_conditions(file_path: str, conditions: list[list], titles: list[str] = None):
    """
    将条件数据写入指定文件（TXT 格式）
    :param file_path: 输出路径
    :param conditions: 条件二维列表（表达式, 操作符, 值）
    :param titles: 标题行（可选）
    """
    lines = []
    if titles:
        lines.append(','.join(titles))
    for cond in conditions:
        if len(cond) >= 3:
            lines.append(f"{cond[0]},{cond[1]},{cond[2]}")
    write_to_file(lines, file_path)
