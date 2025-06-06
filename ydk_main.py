# ydk_main.py

from parsers.ydk_parser import parse_ydk_text
from services.ydk_service import batch_fetch_missing, export_to_txt
from services.local_db_service import LocalCardDB
import os

# 初始化数据库
db = LocalCardDB()

# 示例 YDK 内容（直接写入代码中）
ydk_content = """
#created by OURYGO
#main
47705572
87209160
35618217
35618217
14152693
50546208
8379983
8379983
8379983
42141493
42141493
35763582
83190280
48427163
14558127
14558127
14558127
23434538
23434538
11317977
11317977
11317977
24094655
35726888
35726888
48444114
48444114
48444114
81439173
87931906
24224830
24224830
2344618
2344618
2344618
57103969
57103969
57103969
40366667
40366667
40366667
13935001
#extra
54701958
54701958
24550676
88753594
51777272
81196066
81196066
96381979
90590304
66011101
8809344
4280259
29301450
50277355
60303245
!side
34267821
34267821
84192580
84192580
42141493
59438931
94145022
94145022
18144508
58570206
58570206
58570206
100240005
100240005
23002292
"""

if __name__ == "__main__":
    # 解析 YDK 内容
    main_ids, extra_ids, side_ids = parse_ydk_text(ydk_content)
    print(f"解析到卡牌分布: main[{len(main_ids)}], extra[{len(extra_ids)}], side[{len(side_ids)}]")

    # 获取所有卡牌 ID（含重复）
    all_ids = main_ids + extra_ids + side_ids
    print(f"总卡牌数量（含重复）: {len(all_ids)}")
    print(f"唯一卡牌数量: {len(set(all_ids))}")

    # 自动补全缺失卡牌
    batch_fetch_missing(all_ids)

    # 显示卡组详情
    def print_section(title: str, ids: list[str]):
        print(f"\n=== {title} ===")
        for idx, cid in enumerate(ids, 1):
            name = db.get_card_name(cid)
            print(f"{idx:2d}. [{cid}] {name}")

    print_section("主卡组", main_ids)
    print_section("额外卡组", extra_ids)
    print_section("副卡组", side_ids)

    # 导出 TXT 构筑
    output_path = "我的构筑.txt"
    export_to_txt(main_ids, extra_ids, side_ids, output_file=output_path)
