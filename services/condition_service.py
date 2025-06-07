# services/condition_service.py
from parsers.unified_loader import load_conditions
from typing import Union
import os
from services.local_db_service import LocalCardDB

db = LocalCardDB()

def get_conditions(source: Union[str, os.PathLike], is_path: bool = True):
    """
    加载并解析启动条件列表，支持路径或纯文本。
    """
    return load_conditions(source, is_path=is_path)



def validate_condition(expression: str, operator: str, value: int):
    """
    验证条件表达式中的字段或卡名是否存在于数据库中
    :param expression: 表达式（如 "炎" 或 "灰流丽 & 炎"）
    :param operator: 比较符
    :param value: 数值
    """
    keywords = [k.strip() for k in expression.split("&")]
    for keyword in keywords:
        # 如果不是卡名，则检查是否是有效字段
        if not any(keyword in name for name in db.get_all_cards().values()):
            if keyword not in db.get_all_keywords():
                print(f"⚠️ 警告：关键词 '{keyword}' 不在卡池中且不是已知字段")
