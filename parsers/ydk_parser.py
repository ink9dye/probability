# parsers/ydk_parser.py
import re

def parse_ydk_text(text: str) -> tuple[list[str], list[str], list[str]]:
    """
    解析 YDK 文本字符串，返回 main/extra/side 的卡片 ID 列表。
    """
    main_ids, extra_ids, side_ids = [], [], []
    current = None
    for line in text.strip().split('\n'):
        line = line.strip()
        if line.startswith('#main'):
            current = 'main'
        elif line.startswith('#extra'):
            current = 'extra'
        elif line.startswith('!side'):
            current = 'side'
        elif line.startswith('#') or not line:
            continue
        elif current and line.isdigit():
            if current == 'main':
                main_ids.append(line)
            elif current == 'extra':
                extra_ids.append(line)
            elif current == 'side':
                side_ids.append(line)
    return main_ids, extra_ids, side_ids