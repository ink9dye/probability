# ydk_handler.py

import os
import re


class YDKHandler:
    def __init__(self):
        self.section_markers = {
            'main': re.compile(r'^#main'),
            'extra': re.compile(r'^#extra'),
            'side': re.compile(r'^!side'),
            'comment': re.compile(r'^#')
        }

    def load(self, file_path: str, is_path: bool = True) -> dict:
        """加载 YDK 数据"""
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path

        main_ids, extra_ids, side_ids = self._parse_ydk_text(content)

        return {
            "main": main_ids,
            "extra": extra_ids,
            "side": side_ids
        }

    def save(self, file_path: str, data: dict, titles: list[str] = None):
        """保存 YDK 数据"""
        lines = ['#main']
        lines.extend(data.get("main", []))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _parse_ydk_text(self, text: str) -> tuple[list[str], list[str], list[str]]:
        """解析 YDK 文本"""
        main_ids, extra_ids, side_ids = [], [], []
        current_section = None

        lines = [line.strip() for line in text.strip().split('\n')]

        # 检查是否有任何 section 标记
        has_section_marker = any(
            line.startswith('#main') or
            line.startswith('#extra') or
            line.startswith('!side')
            for line in lines
        )

        if has_section_marker:
            for line in lines:
                if self.section_markers['main'].match(line):
                    current_section = 'main'
                elif self.section_markers['extra'].match(line):
                    current_section = 'extra'
                elif self.section_markers['side'].match(line):
                    current_section = 'side'
                elif self.section_markers['comment'].match(line):
                    continue
                elif line.isdigit():
                    if current_section == 'main':
                        main_ids.append(line)
                    elif current_section == 'extra':
                        extra_ids.append(line)
                    elif current_section == 'side':
                        side_ids.append(line)
        else:
            # 无标记时，将所有数字行视为 main 区域
            for line in lines:
                if line.isdigit():
                    main_ids.append(line)

        return main_ids, extra_ids, side_ids
