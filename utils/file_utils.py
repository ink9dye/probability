# ✅ 改造后的 utils/file_utils.py

import os
from typing import Union

# 假设 settings 中定义了路径常量
from config.settings import PROJECT_ROOT

UTILS_DIR = os.path.dirname(os.path.abspath(__file__))



def ensure_directory(path: str) -> None:
    """
    确保目标路径存在，如果不存在则自动创建
    """
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"📁 已创建目录：{path}")


def resolve_path(*paths) -> str:
    """
    拼接路径为绝对路径并确保中间目录存在。
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
    写入内容到文件。
    """
    file_path = resolve_path(*subdirs, filename)

    if isinstance(content, list):
        content = "\n".join(content)
    elif isinstance(content, dict):
        lines = [f"{k}，{v}" for k, v in content.items()]
        content = "\n".join(lines)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"文件已写入：{file_path}")
    return file_path