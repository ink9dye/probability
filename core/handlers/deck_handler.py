# deck_handler.py

import os
import re
from typing import List, Dict, Set, Optional, Union, Tuple
from collections import Counter


class DeckHandler:
    def __init__(self):
        self.comment_pattern = re.compile(r'^\s*#')
        self.split_pattern = re.compile(r'[，,、．.]')

    def load(self, file_path: str, is_path: bool = True) -> list[str]:
        """加载卡组数据"""
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path

        return self._parse_deck_text(content)

    def save(self, file_path: str, data: list[str], titles: List[str] = None):
        """保存卡组数据"""
        # 先统计卡片数量
        counter = Counter(data)

        # 构建输出行
        lines = [f"{card},{count}" for card, count in counter.items()]

        # 写入文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _parse_deck_text(self, text: str) -> list[str]:
        """解析卡组文本"""
        card_pool = []

        for line in text.strip().split('\n'):
            line = line.strip()

            # 跳过空行和注释行
            if not line or self.comment_pattern.match(line):
                continue

            try:
                # 分割卡名和数量
                parts = self.split_pattern.split(line)
                if len(parts) < 2:
                    print(f"无法处理该行: {line} - 格式不正确")
                    continue

                name = parts[0].strip()
                count = int(parts[1].strip())

                # 将卡名按数量展开
                card_pool.extend([name] * count)
            except (ValueError, IndexError) as e:
                print(f"无法处理该行: {line} - {e}")

        return card_pool
