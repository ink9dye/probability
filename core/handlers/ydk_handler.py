# ydk_handler.py

import os
from core.handlers.base_handler import BaseHandler
from core.parsers.ydk_parser import parse_ydk_text


class YDKHandler(BaseHandler):
    def load(self, file_path: str, is_path: bool = True) -> dict:
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path  # 直接使用字符串内容
        main, extra, side = parse_ydk_text(content)
        return {
            "main": main,
            "extra": extra,
            "side": side
        }

    def save(self, file_path: str, data: dict, titles: list[str] = None):
        lines = ['#main'] + data.get("main", [])
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
