# services/ydk_service.py

from core.ydk_processor import parse_ydk, ydk_to_txt
from typing import List, Dict,Tuple

class YDKService:
    def parse_ydk(self, ydk_content: str) -> Tuple[List[str], List[str], List[str]]:
        """
        解析 YDK 内容，返回 (main_ids, extra_ids, side_ids)。
        """
        return parse_ydk(ydk_content)

    def ydk_to_txt(self, ydk_content: str, csv_file: str, output_file: str = "output.txt"):
        """
        将 YDK 文件中的 main、extra、side 卡组转换为中文版 txt 卡表。
        """
        ydk_to_txt(ydk_content, csv_file, output_file)
