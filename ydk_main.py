# ydk_main.py

from core.parsers.unified_loader import parse_ydk_text
from services.ydk_service import batch_fetch_missing, export_to_txt
from services.local_db_service import get_local_db

db = get_local_db()




def print_section(title: str, ids: list[str]):
    print(f"\n=== {title} ===")
    for idx, cid in enumerate(ids, 1):
        name = db.get_card_name(cid)
        print(f"{idx:2d}. [{cid}] {name}")

# 示例 YDK 内容（直接写入代码中）
ydk_content = """
#created by OURYGO
#main
91073013
93332803
92895501
92895501
78661338
78661338
91800273
9091064
9091064
9091064
91025875
92248362
92248362
92248362
28642461
28642461
28642461
55031170
93156774
93156774
93156774
29302858
29302858
29302858
29280200
29280200
29280200
14558128
14558128
14558128
23434538
23434538
32807848
54562327
54562327
54562327
53792930
80181649
35550352
60883493
#extra
90448280
90303227
61374414
49456901
40673853
27420823
35772782
34876719
2061963
77894049
74997493
48815792
29301450
28168628
28168628
!side

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
    db = get_local_db()  # 获取单例数据库
    print(f"当前数据库缓存大小: {len(db.id_attr_map)}")  # 查看已加载卡
    # 显示卡组详情
    print_section("主卡组", main_ids)
    print_section("额外卡组", extra_ids)
    print_section("副卡组", side_ids)

    # 导出 TXT 构筑
    output_path = "征服斗魂构筑.txt"
    export_to_txt(main_ids, extra_ids, side_ids, output_file=output_path)
