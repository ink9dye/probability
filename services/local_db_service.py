# services/local_db_service.py
from core.repositories.card_repository import LocalCardDB

__db_instance = None


def get_local_db() -> LocalCardDB:
    global __db_instance
    if __db_instance is None:
        __db_instance = LocalCardDB()
    return __db_instance
