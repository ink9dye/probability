# utils/file_utils.py

import os
from typing import Union

# 获取当前文件所在路径（file_utils.py）
UTILS_DIR = os.path.dirname(os.path.abspath(__file__))
# 推导项目根目录（假设 utils 在项目根目录下的子目录中）
PROJECT_ROOT = os.path.dirname(UTILS_DIR)


def ensure_directory(path: str) -> None:
    """
    确保目标路径存在，如果不存在则自动创建
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 已创建目录：{path}")


def resolve_path(*paths) -> str:
    """
    将路径片段拼接为绝对路径，并确保目录存在

    示例：
        resolve_path("构筑", "双子构筑.txt") → E:\pythons\概率\构筑\双子构筑.txt
        resolve_path("data", "local_cards.csv") → E:\pythons\概率\data\local_cards.csv
    """
    full_path = os.path.join(PROJECT_ROOT, *paths)
    dir_path = os.path.dirname(full_path)
    ensure_directory(dir_path)
    return full_path


def write_to_file(
        content: Union[str, list, dict],
        filename: str,
        *subdirs
) -> str:
    """
    写入内容到指定路径下的文件。

    参数：
        content: 要写入的内容（str/list/dict）
        filename: 文件名
        *subdirs: 子目录路径（如 "构筑", "data"）

    返回：
        实际写入的文件路径
    """
    # 处理完整路径情况
    if os.path.isabs(filename):  # 是完整路径
        file_path = filename
        dir_path = os.path.dirname(file_path)
    else:
        file_path = resolve_path(*subdirs, filename)
        dir_path = os.path.dirname(file_path)

    # 格式化内容
    if isinstance(content, list):
        content = "\n".join(content)
    elif isinstance(content, dict):
        lines = [f"{k}，{v}" for k, v in content.items()]
        content = "\n".join(lines)

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"✅ 文件已写入：{file_path}")
    return file_path
