"""
向后兼容层：旧脚本 `import file_read` 仍可用。
"""

from infrastructure.file_storage import read_text as read_file
from parsers.at_rules import RULE_AMPHIBIAN_MERGE_ONE, RULE_DONG_MERGE
from parsers.deck_txt import parse_deck as parse_first_document
from parsers.documents import parse_documents, parse_start_file
from parsers.start_txt import parse_start


def parse_second_document(file_content):
    conditions_list, group_sizes, amphibian, dong, _titles, sixth, dong_bu = parse_start(
        file_content
    )
    return conditions_list, group_sizes, amphibian, dong, sixth, dong_bu


def get_comment_lines(file_path):
    content = read_file(file_path)
    if content is None:
        return []
    return parse_start_file(content)
