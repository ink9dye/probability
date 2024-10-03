import file_read
import probability


def main():
    """
    主函数，负责协调整个流程。
    """
    # 定义文件路径
    first_document_path = "雨sf的刻魔莫忘构筑.txt"
    second_document_path = "刻魔莫忘启动.txt"

    # 读取文件内容
    first_document_content = file_read.read_file(first_document_path)
    second_document_content = file_read.read_file(second_document_path)

    # 如果有任何一个文件读取失败，则退出
    if not first_document_content or not second_document_content:
        return

    # 解析文档内容
    card_pool, conditions_list = file_read.parse_documents(first_document_content, second_document_content)

    # 进行抽卡模拟并输出结果
    probability.simulate_and_report(card_pool, conditions_list)


if __name__ == "__main__":
    main()
