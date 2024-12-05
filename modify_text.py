import sys


def modify_text():
    """
    提供加或改的选项，执行相应操作。
    """
    # 打印选项
    print("请选择操作：")
    print("1. 加：将A中的每一行末尾加上B")
    print("2. 改：将A中的B部分替换成C")

    # 获取用户选择
    choice = input("请输入1或2进行选择：")

    if choice == '1':
        # 选择加
        print("请输入文本A（每一行结束后按Enter键，输入完毕后输入'END'结束输入）：")

        # 使用列表收集每一行输入，直到输入'END'
        text_a = []
        while True:
            line = input()  # 获取每一行
            if line.strip() == "END":
                break
            text_a.append(line)

        # 获取文本B
        print("请输入文本B：")
        text_b = input()  # 获取文本B

        # 将文本A的每一行加上文本B
        result = []
        for line in text_a:
            result.append(line.strip() + text_b)

        # 打印结果
        print("\n修改后的文本A：")
        print("\n".join(result))

    elif choice == '2':
        # 选择改
        print("请输入文本A（每一行结束后按Enter键，输入完毕后输入'END'结束输入）：")

        # 使用列表收集每一行输入，直到输入'END'
        text_a = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            text_a.append(line)

        # 获取替换的文本B和C
        print("请输入要替换的文本B：")
        text_b = input()
        print("请输入替换成的文本C：")
        text_c = input()

        # 替换文本A中的B为C
        result = []
        for line in text_a:
            result.append(line.replace(text_b, text_c))

        # 打印结果
        print("\n修改后的文本A：")
        print("\n".join(result))

    else:
        print("无效的选择，请输入1或2。")


if __name__ == "__main__":
    modify_text()