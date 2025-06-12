# condition_handler.py

import os,re
from core.handlers.base_handler import BaseHandler
from core.entity.composite_condition import CompositeCondition
from core.entity.condition import Condition
from utils.file_utils import write_to_file
def normalize_operator(op: str) -> str:
    """兼容各种操作符表达形式（含中英文、符号写法）"""
    table = {
        '=': '==', '==': '==', '等于': '==',
        '>': '>', '大于': '>',
        '<': '<', '小于': '<',
        '>=': '>=', '大于等于': '>=',
        '<=': '<=', '小于等于': '<=',
        '!=': '!=', '不等于': '!='
    }
    return table.get(op.strip(), op)



def parse_condition_text(text: str) -> tuple[list[CompositeCondition], list[str]]:
    result: list[CompositeCondition] = []
    titles: list[str] = []
    current_title: str | None = None

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
            op = normalize_operator(parts[i + 1].strip())
            val = int(parts[i + 2].strip())

            sub_conditions.append(Condition(expr, op, val))

        # 将该行所有子条件包装成一个 CompositeCondition
        composite_cond = CompositeCondition(sub_conditions)
        result.append(composite_cond)
        titles.append(current_title or "无标题")

    return result, titles


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


class ConditionHandler(BaseHandler):
    def load(self, file_path: str, is_path: bool = True) -> tuple[list, list]:
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path
        return parse_condition_text(content)

    def save(self, file_path: str, data: list, titles: list[str] = None):
        conditions = []
        titles = titles or [""] * len(data)
        for cond, title in zip(data, titles):
            conditions.append([cond.expression, cond.operator, str(cond.value)])
        write_conditions(file_path, conditions, titles)
