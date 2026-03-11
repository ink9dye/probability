import file_read
import probability
N=8
#总情况下一个小情况里的数量
def main():
    """
    主函数，负责协调整个流程。
    """
    # 定义文件路径
    first_document_path = "构筑与启动/祈夏sf杀音构筑改版紧急喷气.txt"
    second_document_path = "构筑与启动/t0杀音启动.txt"

    # 读取文件内容
    #卡组
    first_document_content = file_read.read_file(first_document_path)
    #启动
    second_document_content = file_read.read_file(second_document_path)
    #标题
    title=file_read.get_comment_lines(second_document_path)

    # 如果有任何一个文件读取失败，则退出
    if not first_document_content or not second_document_content:
        return

    # 解析文档内容
    card_pool, conditions_list = file_read.parse_documents(first_document_content, second_document_content)

    # 进行抽卡模拟并输出结果
    probability.simulate_and_report(card_pool, conditions_list,title)


if __name__ == "__main__":
    main()
