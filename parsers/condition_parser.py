# condition_parser.py
import re
from entity.condition import Condition
from entity.composite_condition import CompositeCondition

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
