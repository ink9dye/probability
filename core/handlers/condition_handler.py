# condition_handler.py

import os
from core.handlers.base_handler import BaseHandler
from core.parsers.condition_parser import parse_condition_text
from core.writers.condition_writer import write_conditions


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
