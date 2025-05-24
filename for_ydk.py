import re
import requests
import time
import os
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor
import csv
from collections import defaultdict,Counter


# 配置参数
API_BASE = "https://ygocdb.com/api/v0/card/"
CSV_FILE = "local_cards.csv"
CSV_HEADERS = ["id", "name_cn", "field"]



# --------------------------
# 本地数据管理模块
# --------------------------
class LocalCardDB:
    def __init__(self):
        self.existing_ids = set()
        self.id_name_map = {}
        self.load_existing_data()

    def load_existing_data(self):
        """加载本地已有数据"""
        if os.path.exists(CSV_FILE):
            with open(CSV_FILE, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    card_id = row.get('id')
                    name_cn = row.get('name_cn')
                    if card_id:
                        self.existing_ids.add(card_id)
                        if name_cn:
                            self.id_name_map[card_id] = name_cn

    def save_new_cards(self, new_data: List[Dict]):
        filtered_data = []
        for item in new_data:
            cid = item.get('id')
            if cid and cid not in self.existing_ids:
                filtered_data.append(item)
                self.existing_ids.add(cid)
                self.id_name_map[cid] = item['name_cn']

        if not filtered_data:
            return

        file_exists = os.path.exists(CSV_FILE)
        with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerows(filtered_data)

    def get_card_name(self, card_id: str) -> str:
        """获取卡牌名称（带缓存）"""
        return self.id_name_map.get(card_id, "未知卡牌")


# --------------------------
# YDK解析模块
# --------------------------
def parse_ydk(ydk_text: str) -> Tuple[List[str], List[str], List[str]]:
    """返回 (main_ids, extra_ids, side_ids)"""
    main_ids = []
    extra_ids = []
    side_ids = []

    current_section = None
    for line in ydk_text.split('\n'):
        line = line.strip()
        if not line:
            continue

        # 检测区域标记
        if line.startswith('#main'):
            current_section = 'main'
        elif line.startswith('#extra'):
            current_section = 'extra'
        elif line.startswith('!side'):
            current_section = 'side'
        # 忽略注释行
        elif line.startswith('#'):
            continue
        # 处理卡牌ID
        elif current_section and re.match(r'^\d+$', line):
            if current_section == 'main':
                main_ids.append(line)
            elif current_section == 'extra':
                extra_ids.append(line)
            elif current_section == 'side':
                side_ids.append(line)

    return main_ids, extra_ids, side_ids


# --------------------------
# 数据处理模块
# --------------------------
def extract_field(types: str) -> str:
    """
    从 types 字段中提取有意义的关键词，如：
        "[怪兽|通常] 龙/光" → "怪兽、龙、光"
        "[魔法|永续]"       → "魔法"
        "[陷阱|反击]"       → "陷阱"
    """
    if not types or not types.startswith('['):
        return ""

    try:
        # 只保留第一部分，如 "[怪兽|通常]"
        main_part = types.split(']')[0].strip('[')
        categories = main_part.split('|')

        # 获取可能包含的种族、属性等信息（比如“龙/光”）
        extra_parts = []
        for part in types.split(']')[1:]:
            for sub_part in re.split(r'[ /、，]', part):
                word = sub_part.strip()
                if word and len(word) <= 3:  # 简单过滤掉描述性语句
                    extra_parts.append(word)

        combined = list(set(categories + extra_parts))
        return '、'.join([word for word in combined if word])
    except Exception as e:
        print(f"Error extracting field from '{types}': {e}")
        return ""


def process_raw_data(card_id: str, data: dict) -> Dict:
    text_section = data.get("text", {})
    name = text_section.get("name", "")
    types = text_section.get("types", "")

    field_parts = extract_field(types).split('、')

    # 添加 name 到 field 中（这里可以根据需要过滤掉一些无意义的词）
    if name:
        field_parts.append(name)

    # 去重并返回
    return {
        "id": card_id,
        "name_cn": name,
        "field": '、'.join(sorted(set(field_parts), key=field_parts.index))  # 保持顺序去重
    }


# --------------------------
# 智能请求模块
# --------------------------
def fetch_card(card_id: str, db: LocalCardDB) -> Dict:
    """优先使用本地数据"""
    if card_id in db.existing_ids:
        return None

    try:
        response = requests.get(
            f"{API_BASE}{card_id}",
            headers={"User-Agent": "YGO-LocalDB/1.0"},
            timeout=10
        )
        response.raise_for_status()
        return process_raw_data(card_id, response.json())
    except Exception as e:
        print(f"Error fetching {card_id}: {str(e)}")
        return None


# --------------------------
# 批量处理模块
# --------------------------
def batch_process(card_ids: List[str], db: LocalCardDB) -> List[Dict]:
    """处理需要更新的卡牌"""
    # 去重处理并过滤已存在ID
    unique_new_ids = [cid for cid in set(card_ids) if cid not in db.existing_ids]
    if not unique_new_ids:
        return []

    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch_card, cid, db): cid for cid in unique_new_ids}

        for future in futures:
            if result := future.result():
                results.append(result)
                time.sleep(0.5)  # 礼貌性延迟

    return results




def ydk_to_txt(ydk_content: str, csv_file: str, output_file: str = "output.txt"):
    """
    将 ydk 文件中的 main、extra、side 卡组转换为中文版 txt 卡表。
    每个部分以 #main、#extra、#side 开头。
    """

    # 1️⃣ 加载 CSV 数据（id -> name_cn）
    id_to_name = {}
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                card_id = row.get('id')
                name_cn = row.get('name_cn')
                if card_id and name_cn:
                    id_to_name[card_id] = name_cn
    except Exception as e:
        print(f"❌ 加载 {csv_file} 失败：{e}")
        return

    # 2️⃣ 解析 YDK 内容，提取 main、extra、side 中的卡牌 ID
    sections = {'main': [], 'extra': [], 'side': []}
    current_section = None

    for line in ydk_content.strip().split('\n'):
        line = line.strip()
        if line.startswith('#main'):
            current_section = 'main'
        elif line.startswith('#extra'):
            current_section = 'extra'
        elif line.startswith('!side'):
            current_section = 'side'
        elif line.isdigit():
            if current_section in sections:
                sections[current_section].append(line)

    # 3️⃣ 映射为中文名并统计数量
    result_lines = []

    for section_name, card_ids in sections.items():
        name_counter = defaultdict(int)
        missing_ids = []

        for card_id in card_ids:
            name = id_to_name.get(card_id)
            if name:
                name_counter[name] += 1
            else:
                missing_ids.append(card_id)

        # 排序并添加到结果中
        sorted_names = sorted(name_counter.items(), key=lambda x: x[0])
        result_lines.append(f"#{section_name}")
        for name, count in sorted_names:
            result_lines.append(f"{name}，{count}")

        if missing_ids:
            print(f"⚠️ [{section_name}] 以下 ID 在 local_cards.csv 中找不到对应中文名：{missing_ids}")

    # 4️⃣ 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(result_lines))

    print(f"✅ 成功导出 {len(result_lines)} 行到 {output_file}")


# --------------------------
# 主流程
# --------------------------
if __name__ == "__main__":
    # 初始化本地数据库
    card_db = LocalCardDB()
    print(extract_field("[怪兽|通常] 龙/光"))  # 输出：怪兽、龙、光
    print(extract_field("[魔法|永续]"))  # 输出：魔法
    print(extract_field("[陷阱|反击]"))  # 输出：陷阱

    # 示例YDK内容
    ydk_content = """
    #created by OURYGO
#main
101301005
40366667
40366667
42141493
40366667
87209160
35618217
35618217
14152693
50546208
101301005
101301005
42141493
101301006
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
47705572
35726888
35726888
48444114
48444114
48444114
81439173
87931906
24224830
24224830
57103969
57103969
57103969
101301053
101301053
101301053
13935001
#extra
101301030
101301030
24550676
88753594
51777272
101301031
101301031
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

    # 解析YDK内容
    main_ids, extra_ids, side_ids = parse_ydk(ydk_content)
    print(f"解析到卡牌分布: main[{len(main_ids)}], extra[{len(extra_ids)}], side[{len(side_ids)}]")

    # 获取所有需要处理的ID
    all_ids = main_ids + extra_ids + side_ids
    print(f"总卡牌数量（含重复）: {len(all_ids)}")
    print(f"唯一卡牌数量: {len(set(all_ids))}")

    # 获取新数据
    new_data = batch_process(all_ids, card_db)
    if new_data:
        card_db.save_new_cards(new_data)
        print(f"新增存储 {len(new_data)} 条记录到 {CSV_FILE}")


    # 显示分类结果
    def print_section(title: str, ids: List[str]):
        print(f"\n=== {title} ===")
        for idx, cid in enumerate(ids, 1):
            print(f"{idx:2d}. [{cid}] {card_db.get_card_name(cid)}")

    print_section("主卡组", main_ids)
    print_section("额外卡组", extra_ids)
    print_section("副卡组", side_ids)

    ydk_to_txt(ydk_content, "local_cards.csv", "我的构筑.txt")