def parse_first_document(file_content):
    card_pool = []
    for line in file_content.strip().split('\n'):
        # 去掉多余空格，并按逗号分割
        card_name, count = line.split('，')
        card_pool.extend([card_name] * int(count))
    return card_pool