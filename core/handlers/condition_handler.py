# condition_handler.py

import os
import re


class ConditionHandler:
    def __init__(self):
        self.operator_table = {
            '=': '==', '==': '==', '等于': '==',
            '>': '>', '大于': '>',
            '<': '<', '小于': '<',
            '>=': '>=', '大于等于': '>=',
            '<=': '<=', '小于等于': '<=',
            '!=': '!=', '不等于': '!='
        }

    def load(self, file_path: str, is_path: True) -> tuple[list, list]:
        """加载条件数据"""
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path

        return self._parse_condition_text(content)

    def save(self, file_path: str, data: list, titles: list[str] = None):
        """保存条件数据"""
        lines = []
        titles = titles or [""] * len(data)

        if titles:
            lines.append(','.join(titles))

        for cond, title in zip(data, titles):
            if hasattr(cond, 'sub_conditions'):
                parts = []
                for sub_cond in cond.sub_conditions:
                    parts.extend([sub_cond.expression, sub_cond.operator, str(sub_cond.value)])
                lines.append(','.join(parts))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _normalize_operator(self, op: str) -> str:
        """标准化操作符"""
        return self.operator_table.get(op.strip(), op)

    def _parse_condition_text(self, text: str) -> tuple[list, list]:
        """解析条件文本"""
        result = []
        titles = []
        current_title = None

        for line in text.strip().split('\n'):
            line = line.strip()
            if not line:
                continue
            if line.startswith('#'):
                current_title = line.lstrip('#').strip()
                continue

            parts = re.split(r'[，,、．.]', line)
            if len(parts) % 3 != 0:
                print(f"️ 条件格式不正确: {line}")
                continue

            sub_conditions = []
            for i in range(0, len(parts), 3):
                expr = parts[i].strip()
                op = self._normalize_operator(parts[i + 1].strip())
                val = int(parts[i + 2].strip())

                sub_conditions.append({'expression': expr, 'operator': op, 'value': val})

            # 将该行所有子条件包装成一个组合条件
            result.append({'sub_conditions': sub_conditions})
            titles.append(current_title or "无标题")

        return result, titles
