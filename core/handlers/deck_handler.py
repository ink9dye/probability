# deck_handler.py

import os
from core.handlers.base_handler import BaseHandler
from core.parsers.deck_parser import parse_deck_text
from core.writers.deck_writer import write_deck

from typing import List, Dict, Set, Optional, Union,Tuple


class DeckHandler(BaseHandler):
    def load(self, file_path: str, is_path: bool = True) -> list[str]:
        if is_path or os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = file_path
        return parse_deck_text(content)

    def save(self, file_path: str, data: list[str], titles: List[str] = None):
        write_deck(file_path, data)
