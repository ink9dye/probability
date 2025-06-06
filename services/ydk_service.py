# services/ydk_service.py
import os
from parsers.ydk_parser import parse_ydk_text
from services.local_db_service import LocalCardDB
from collections import defaultdict

def load_ydk_ids(ydk_content: str) -> tuple[list[str], list[str], list[str]]:
    """
    从 YDK 文本中解析出卡片 ID 三元组。
    """
    return parse_ydk_text(ydk_content)


def convert_ids_to_names(id_list: list[str], db: LocalCardDB) -> dict[str, int]:
    """
    将 ID 列表转换为 {卡名: 数量} 映射。
    """
    name_counter = defaultdict(int)
    for cid in id_list:
        name = db.get_card_name(cid)
        name_counter[name] += 1
    return dict(name_counter)


def export_to_txt(main_ids: list[str], extra_ids: list[str], side_ids: list[str],
                  db: LocalCardDB, output_file: str = "output.txt") -> None:
    """
    将 YDK 构筑导出为 TXT 卡表格式。
    """
    sections = {
        "#main": convert_ids_to_names(main_ids, db),
        "#extra": convert_ids_to_names(extra_ids, db),
        "#side": convert_ids_to_names(side_ids, db)
    }

    lines = []
    for section, card_map in sections.items():
        lines.append(section)
        for name, count in sorted(card_map.items()):
            lines.append(f"{name}，{count}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"✅ 已导出构筑到 {output_file}")
