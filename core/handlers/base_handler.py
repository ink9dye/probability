# base_handler.py

from typing import Any, List, Optional

class BaseHandler:
    def load(self, source: str, is_path: bool = True) -> Any:
        raise NotImplementedError()

    def save(self, file_path: str, data: Any, titles: List[str] = None):
        raise NotImplementedError()
