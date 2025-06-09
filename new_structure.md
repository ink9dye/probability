# ✅ 项目结构重组建议（基于 SOA + MVC + Entity 模型）
```
# 顶层结构
概率/
├── main.py
├── config/
│   └── settings.py                    # 配置路径、API参数等
├── data/
│   └── local_cards.csv              # 本地卡牌数据文件，仅用于字段定义、ID-名称映射等
├── entity/                            # ✅ 模型层
│   ├── card.py                        # Card 模型类
│   ├── condition.py                   # Condition 模型类
│   ├── composite_condition.py         # CompositeCondition 模型类
├── parsers/                           # 数据解析器模块（统一负责 YDK / TXT 构筑、条件的读取与转换）
│   ├── __init__.py
│   ├── card_pool_parser.py           # ✅ 解析卡组 TXT → List[str]（卡名）
│   ├── condition_parser.py           # ✅ 解析启动条件 TXT → List[Condition]（条件模型）
│   ├── ydk_parser.py                 # ✅ 解析 YDK 文本或文件 → Tuple[List[str], List[str], List[str]]
│   └── unified_loader.py             # ✅ 新增统一入口：支持文本/文件路径（YDK 或 构筑卡组/条件）
├── services/
│   ├── __init__.py
│   ├── simulation_service.py        # 抽卡模拟器逻辑
│   ├── deck_service.py              # 卡池加载服务（YDK/TXT 卡名加载）
│   ├── condition_service.py         # 启动条件解析与判断服务
│   ├── ydk_service.py               # YDK 卡组管理服务（解析 + 中文转换）
│   └── local_db_service.py          # 本地 CSV 卡牌数据库服务（缓存、刷新、字段匹配）
├── engine/                            # 模拟核心引擎
│   ├── __init__.py
│   ├── probability_engine.py         # 实现抽卡模拟主逻辑
│   └── strategy_rules.py             # 封装“壶”、“暗抽”、“自奏”等策略
├── gui/                               # 前端界面（MVC: View + Controller）
│   ├── frames/                       # 各个视图窗口
│   │   ├── main_frame.py             # 主控面板：加载卡组/条件、选择策略、运行模拟
│   │   ├── deck_editor_frame.py      # 卡组编辑器：加载并展示 YDK 内容、导出构筑
│   │   ├── condition_editor_frame.py # 条件编辑器：加载 JSON、表格展示表达式/操作符/值
│   │   ├── card_editor_frame.py      # 字段编辑器：搜索卡牌、查看字段、添加/修改/删除字段
│   │   └── strategy_creator_frame.py # 策略构建器：组合多条件逻辑、保存为 JSON/脚本
│   ├── widgets/                      # UI 组件库（可复用控件）
│   ├── controller.py                # Controller：协调界面交互与服务调用
│   └── main_window.py               # GUI 启动入口
├── utils/                             # 工具层
│   └── logger.py
├── test/                              # 测试模块
│   └── ...
├── 构筑
│   ├── ...  #卡组文件
├── 启动
│   ├── ...  #条件文件
├── modify_text.py                    # 文本工具模块
├── README.md
├── requirements.txt
├── new_structure.md
├── TODO.md

```

