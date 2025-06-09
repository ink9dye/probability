# ✅ 项目结构重组建议（基于 SOA + MVC + Entity 模型）

<details>
<summary><strong>概率/</strong></summary>

- `main.py`：主控入口脚本  

### 📁 config/ 配置与工具
- `settings.py`：配置路径、API 参数等

### 📁 data/ 数据资源
- `local_cards.csv`：本地卡牌数据文件，仅用于字段定义、ID-名称映射等

### 📁 entity/ 模型层（Entity / Domain Models）
- `card.py`：Card 模型类  
- `condition.py`：Condition 模型类  
- `composite_condition.py`：CompositeCondition 模型类  

### 📁 parsers/ 数据解析器（Parser / Loader）
- `__init__.py`  
- `card_pool_parser.py`：解析卡组 TXT → `List[str]`（卡名）  
- `condition_parser.py`：解析启动条件 TXT → `List[Condition]`（条件模型）  
- `ydk_parser.py`：解析 YDK 文件 → `Tuple[List[str], List[str], List[str]]`  
- `unified_loader.py`：统一入口，支持路径/文本解析（卡组/条件）

### 📁 services/ 服务层（SOA Services）
- `__init__.py`  
- `simulation_service.py`：抽卡模拟器逻辑  
- `parser_service.py`：封装解析服务接口  
- `ydk_service.py`：YDK 卡组服务（解析+中文转换）  
- `local_db_service.py`：本地卡池字段匹配、缓存、刷新服务

### 📁 repositories/ 数据访问层（DAO / Repository）
- `card_repository.py`：LocalCardDB 实现

### 📁 engine/ 模拟核心引擎
- `__init__.py`  
- `probability_engine.py`：抽卡模拟主逻辑  
- `strategy_rules.py`：封装策略规则（如“壶”、“暗抽”、“自奏”等）

### 📁 gui/ 前端界面层（MVC: View + Controller）
#### 📁 frames/
- `main_frame.py`：主控面板  
- `deck_editor_frame.py`：卡组编辑器  
- `condition_editor_frame.py`：条件编辑器  
- `card_editor_frame.py`：字段编辑器  
- `strategy_creator_frame.py`：策略构建器  

#### 📁 widgets/
- 可复用 UI 控件集合

- `controller.py`：控制器，协调 GUI 与服务交互  
- `main_window.py`：GUI 启动入口

### 📁 utils/ 工具层
- `logger.py`：日志工具模块

### 📁 test/ 测试模块
- `...`：单元测试、集成测试脚本

### 📁 构筑/
- 卡组构筑文件（YDK/TXT）

### 📁 启动/
- 启动条件文件（JSON/TXT）

### 📄 其他文件
- `modify_text.py`：文本处理工具  
- `README.md`：项目说明  
- `requirements.txt`：Python 依赖列表  
- `new_structure.md`：结构说明文档  
- `TODO.md`：待办事项

</details>