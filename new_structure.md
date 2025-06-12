概率/
概率/
├── main.py                      # 主程序入口（GUI 启动），真实用户使用的主入口
├── backend_main.py              # 后端流程测试入口：用于执行抽卡模拟流程（无 GUI）
├── ydk_main.py                  # YDK 工具测试入口：解析 YDK 内

### 📁 config/ 全局配置
│   └── settings.py              # 配置路径、API 参数等

### 📁 core/ 核心业务模型与引擎（Domain Core）
│   ├── __init__.py
│   │
│   ├── engine/                  # 核心模拟引擎
│   │   ├── probability_engine.py # 抽卡模拟主逻辑
│   ├── entity/                  # 实体模型
│   │   ├── card.py              # Card 模型类  
│   │   ├── condition.py         # Condition 模型类  
│   │   └── composite_condition.py # 复合条件实体  
│   │
│   ├── handlers/                 # 文件处理器
│   │   ├── init__.py
│   │   ├── base_handler.py        # 基础处理器
│   │   ├── condition_parser.py    # TXT 条件处理器
│   │   ├── deck_parser.py         # 卡组处理器
│   │   └── ydk_parser.py          # ydk处理器
├── repositories/               # 卡片数据访问
│   └── card_repository.py      # LocalCardDB 实现

### 📁 data/ 数据资源
│   ├── local_cards.csv          # 本地卡牌数据文件（ID-名称映射）
│   ├── 构筑/                    # 卡组构筑文件（YDK/TXT）
│   └── 启动/                   # 启动条件文件（TXT）

### 📁 service/ 服务层（SOA Services）
│   ├── simulation_service.py    # 模拟器业务逻辑
│   ├── handler_service.py        # 对应文件处理服务封装
│   ├── ydk_service.py           # YDK 相关服务
│   └── local_db_service.py      # 本地数据库服务

### 📁 gui/ 前端界面层（MVC: View + Controller）
│   ├── controller.py            # 控制器协调层，连接 UI 与业务逻辑
│   ├── main_window.py           # 主窗口容器，承载 Tab 页面切换
│   │
│   └── frames/                  # Tab 页面模块
│       ├── main_frame.py        # 主控面板：策略设置、模拟启动、日志展示
│       ├── deck_editor_frame.py # 卡组编辑器：加载/保存 TXT 卡组文件
│       ├── condition_editor_frame.py # 条件编辑器：编辑启动条件文本
│       └── card_editor_frame.py # 字段编辑器：管理卡牌 ID、名称及字段列表
│   │
│   └── widgets/                 # 可复用 UI 控件
│       ├── raw_text_editor.py   # 通用文本编辑控件，支持文件读写
│       └── base_editable_tree.py # 表格基类，提供搜索、过滤、右键菜单功能
│       └── editable_field_tree.py # 继承自 BaseEditableTree，用于字段编辑表格

### 📁 utils/ 工具层
│   ├── file_utils.py            # 路径处理、通用文件操作



### 📄 其他文件
│   ├── README.md                # 项目说明  
│   ├── requirements.txt         # Python 依赖列表  
│   ├── new_structure.md         # 结构说明文档  
│   └── TODO.md                 # 待办事项
