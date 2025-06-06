# utils/text_utils.py
def extract_comment_lines(path: str) -> list[str]:
    """
    提取文件中以 # 开头的注释行（用于标题说明）
    """
    comments = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith('#'):
                comments.append(line.strip())
    return comments
