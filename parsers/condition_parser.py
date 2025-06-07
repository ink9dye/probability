# condition_parser.py
import re
from entity.condition import Condition


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


def parse_condition_text(text: str) -> tuple[list[list[Condition]], list[str]]:
    """
    解析启动条件 TXT 文本，返回二维条件组列表和对应的注释标题列表。
    每个 #注释 行作为后续条件组的 group_title 来源。
    """
    result: list[list[Condition]] = []
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

        group: list[Condition] = []
        conditions = []

        for i in range(0, len(parts), 3):
            name = parts[i].strip()
            op = normalize_operator(parts[i + 1].strip())
            value = int(parts[i + 2].strip())

            conditions.append((name, op, value))

        # 合并多个条件为一个 AND 组合条件
        expressions = [" & ".join(name for name, _, _ in conditions)]
        operators = [op for _, op, _ in conditions]
        values = [value for _, _, value in conditions]

        # 支持多个 AND 条件组合
        for expr, op, val in zip(expressions, operators, values):
            try:
                group.append(Condition(expr, op, val, group_title=current_title))
            except Exception as e:
                print(f"解析条件失败: {line} - {e}")

        if group:
            result.append(group)
            titles.append(current_title or "无标题")

    return result, titles
