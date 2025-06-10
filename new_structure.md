概率/
├── main.py                      # 主程序入口

### 📁 config/ 全局配置
│   └── settings.py              # 配置路径、API 参数等

### 📁 data/ 数据资源
│   ├── local_cards.csv          # 本地卡牌数据文件（ID-名称映射）
│   ├── 构筑/                    # 卡组构筑文件（YDK/TXT）
│   └── 启动/                   # 启动条件文件（TXT）

### 📁 core/ 核心业务模型与引擎（Domain Core）
│   ├── __init__.py
│   │
│   ├── entity/                  # 实体模型
│   │   ├── card.py              # Card 模型类  
│   │   ├── condition.py         # Condition 模型类  
│   │   └── composite_condition.py # 复合条件实体  
│   │
│   ├── parsers/                 # 解析器
│   │   ├── ydk_parser.py        # YDK 文件解析
│   │   ├── card_pool_parser.py  # TXT 卡组解析
│   │   ├── condition_parser.py  # 条件文件解析
│   │   └── unified_loader.py    # 统一解析入口
│   │
│   ├── writers/                 # 写入器
│   │   ├── deck_writer.py       # 写入卡组 TXT
│   │   ├── condition_writer.py  # 写入条件 TXT
│   │   └── unified_writer.py    # 统一写入接口
│   │
│   ├── engine/                  # 核心模拟引擎
│   │   ├── probability_engine.py # 抽卡模拟主逻辑
│   │   └── strategy_rules.py    # 策略规则封装
├── repositories/               # 卡片数据访问
│   └── card_repository.py      # LocalCardDB 实现

### 📁 service/ 服务层（SOA Services）
│   ├── simulation_service.py    # 模拟器业务逻辑
│   ├── parser_service.py        # 解析服务封装
│   ├── writer_service.py        # 写入服务封装
│   ├── ydk_service.py           # YDK 相关服务
│   └── local_db_service.py      # 本地数据库服务



### 📁 gui/ 前端界面层（MVC: View + Controller）
│   ├── controller.py            # 控制器协调层
│   ├── main_window.py           # 主窗口容器
│   │
│   └── frames/                 # Tab 页面
│       ├── main_frame.py        # 主控面板  
│       ├── deck_editor_frame.py # 卡组编辑器  
│       ├── condition_editor_frame.py # 条件编辑器  
│       └── card_editor_frame.py # 字段编辑器  

│   └── widgets/                # 可复用 UI 控件
│       ├── raw_text_editor.py
│       └── base_editable_tree.py

### 📁 utils/ 工具层
│   ├── file_utils.py            # 路径处理、通用文件操作
│   └── logger.py               # 日志工具模块

### 📁 test/ 测试模块
│   ├── unit/
│   │   ├── test_deck_parser.py
│   │   ├── test_ydk_service.py
│   │   └── test_simulation.py
│   └── integration/
│       └── test_gui_flow.py

### 📄 其他文件
│   ├── modify_text.py           # 文本处理工具  
│   ├── README.md                # 项目说明  
│   ├── requirements.txt         # Python 依赖列表  
│   ├── new_structure.md         # 结构说明文档  
│   └── TODO.md                 # 待办事项
