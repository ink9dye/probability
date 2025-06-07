# parsers/ydk_parser.py
import re

def parse_ydk_text(text: str) -> tuple[list[str], list[str], list[str]]:
    """
    解析 YDK 文本字符串，返回 main/extra/side 的卡片 ID 列表。
    如果没有 #main 等标记，则将所有数字行视为 main 区域。
    """
    main_ids, extra_ids, side_ids = [], [], []
    current = None

    lines = [line.strip() for line in text.strip().split('\n')]

    # 检查是否有任何标记 (#main / #extra / !side)
    has_section_marker = any(line.startswith('#main') or line.startswith('#extra') or line.startswith('!side') for line in lines)

    if has_section_marker:
        # 原有解析方式
        for line in lines:
            if line.startswith('#main'):
                current = 'main'
            elif line.startswith('#extra'):
                current = 'extra'
            elif line.startswith('!side'):
                current = 'side'
            elif line.startswith('#'):
                continue
            elif line.isdigit():
                if current == 'main':
                    main_ids.append(line)
                elif current == 'extra':
                    extra_ids.append(line)
                elif current == 'side':
                    side_ids.append(line)
    else:
        # 无标记时，将所有数字行视为 main 区域
        for line in lines:
            if line.isdigit():
                main_ids.append(line)

    return main_ids, extra_ids, side_ids

def clean_card_name(name: str) -> str:
    """
    清理卡牌名称中的中文引号、空格、单双引号等。
    示例："“K9案件”" → "K9案件"
    """
    return name.strip().strip('“”"\'')