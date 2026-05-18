import file_read
import probability

#总情况下一个小情况里的数量
def main():
    """
    主函数，负责协调整个流程。
    """
    enable_going_second = False
    try:
        # Windows 终端在不同编码下可能会把中文 prompt 显示成乱码，这里改为纯 ASCII 提示。
        ans = input("Enable going-second mode? (1=yes, 0/Enter=no): ").strip()
        enable_going_second = (ans not in ("", "0"))
    except EOFError:
        enable_going_second = False

    dai_man_pot_n = None
    # 定义文件路径
    first_document_path = "构筑与启动/耀圣狱神构筑.txt"
    second_document_path = "构筑与启动/耀圣狱神启动.txt"

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
    (
        card_pool,
        conditions_list,
        group_sizes,
        amphibian_merge_one_rules,
        dong_merge_rules,
    ) = file_read.parse_documents(first_document_content, second_document_content)

    if any("怠慢壶" in c for c in card_pool):
        try:
            raw_n = input(
                "Deck has 怠慢壶: enter pot reveal count n (draw n, shuffle back n-1): "
            ).strip()
            dai_man_pot_n = max(1, int(raw_n))
        except (EOFError, ValueError):
            dai_man_pot_n = 6

    # 进行抽卡模拟并输出结果
    probability.simulate_and_report(
        card_pool,
        conditions_list,
        title,
        group_sizes,
        enable_going_second=enable_going_second,
        amphibian_merge_one_rules=amphibian_merge_one_rules,
        dong_merge_rules=dong_merge_rules,
        dai_man_pot_n=dai_man_pot_n,
    )


if __name__ == "__main__":
    main()
