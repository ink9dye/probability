# # writers/unified_writer.py
#
# from .deck_writer import write_deck
# from .condition_writer import write_conditions
#
#
# def write_data(file_path: str, data_type: str, data, titles: list[str] = None):
#     """
#     统一写入接口
#     :param file_path: 输出路径
#     :param data_type: 类型 ('deck' / 'condition')
#     :param data: 数据内容
#     :param titles: 标题行（可选）
#     """
#     if data_type == 'deck':
#         return write_deck(file_path, data)
#     elif data_type == 'condition':
#         return write_conditions(file_path, data, titles)
#     else:
#         raise ValueError(f"不支持的数据类型: {data_type}")
