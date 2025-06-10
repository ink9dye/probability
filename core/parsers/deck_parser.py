# parsers/deck_parser.py
import re

def parse_deck_text(text: str) -> list[str]:
    """
    解析卡池 TXT 文本：格式如“卡名，数量”，返回卡名（按数量展开）列表。
    忽略注释行（# 开头）
    """
    card_pool = []
    for line in text.strip().split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            name, count = re.split(r'[，,、．.]', line)
            card_pool.extend([name.strip()] * int(count.strip()))
        except ValueError as e:
            print(f"⚠️ 无法处理该行: {line} - {e}")
    return card_pool