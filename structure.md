### 项目目录结构

```
概率
├── .venv
├── config
│   └── settings.py  # 配置文件，存储全局配置项（如 API 地址、CSV 文件路径等）
├── core
│   ├── file_read.py  # 文件读取模块，负责解析卡池文件和条件文件
│   ├── interfaces.py  # 接口定义模块，定义核心功能的抽象接口
│   ├── probability.py  # 抽卡模拟模块，实现抽卡逻辑和条件判断
│   └── ydk_processor.py  # YDK 处理模块，处理 YDK 文件并转换为中文版 txt 卡表
├── data
│   └── local_cards.csv  # 本地卡牌数据文件，存储卡牌信息（id, name, field）
├── gui
│   ├── frames
│   │   ├── condition_frame.py  # 条件设置页面，用于选择和展示条件文件内容
│   │   ├── deck_frame.py  # 卡池设置页面，用于选择和展示卡池文件内容
│   │   ├── result_display_frame.py  # 结果展示页面，展示抽卡结果和满足概率
│   │   ├── simulation_run_frame.py  # 模拟执行页面，配置参数并启动模拟
│   │   └── strategy_config_frame.py  # 策略配置页面（具体功能待定）
│   ├── widgets
│   │   ├── progress_bar.py  # 进度条组件，用于显示模拟进度
│   │   └── table_view.py  # 表格视图组件，用于展示数据表格
│   ├── controller.py  # 控制器模块，管理各页面之间的状态流转和核心模块调用
│   └── main_window.py  # 主窗口类，构建整个 GUI 的基础框架
├── services
│   ├── condition_service.py  # 条件服务模块，提供条件相关的业务逻辑
│   ├── deck_service.py  # 卡池服务模块，提供卡池相关的业务逻辑
│   ├── simulation_service.py  # 模拟服务模块，封装抽卡模拟的业务逻辑
│   └── ydk_service.py  # YDK 服务模块，封装 YDK 相关的业务逻辑
├── test
│   └── ...  # 测试相关文件
├── utils
│   └── logger.py  # 日志记录模块，提供日志记录功能
├── 构筑与启动
│   ├── ...  # 构建和启动相关的文件（如示例卡池文件、条件文件等）
├── main.py  # 项目入口文件，协调整个流程
├── modify_text.py  # 文本修改工具模块（具体功能待定）
├── README.md  # 项目说明文档
├── requirements.txt  # 项目依赖文件，列出项目所需的所有 Python 包
├── structure.md  # 项目结构说明文档
├── TODO.md  # 待办事项清单，记录项目开发计划和任务
└── 我的架构.txt  # 项目架构设计文档
```


### 各个文件的作用

#### 根目录

- **`main.py`**：项目入口文件，负责协调整个流程，包括文件读取、解析、抽卡模拟等。
- **`README.md`**：项目说明文档，介绍项目的基本信息、使用方法等。
- **`requirements.txt`**：项目依赖文件，列出项目所需的所有 Python 包，便于环境搭建。
- **`TODO.md`**：待办事项清单，记录项目开发计划和任务，指导后续开发工作。
- **`structure.md`**：项目结构说明文档，描述项目的整体结构和各部分的功能。
- **`我的架构.txt`**：项目架构设计文档，详细描述项目的架构设计思路和实现方案。

#### [config](file://E:\pythons\概率\.venv\Lib\site-packages\uvicorn\config.py#L0-L0) 目录

- **[settings.py](file://E:\pythons\概率\config\settings.py)**：配置文件，存储全局配置项，如 API 地址、CSV 文件路径等，方便统一管理和修改。

#### [core](file://E:\pythons\概率\.venv\Lib\site-packages\pip\_vendor\idna\core.py#L0-L0) 目录

- **[file_read.py](file://E:\pythons\概率\core\file_read.py)**：文件读取模块，负责解析卡池文件和条件文件，提供文件读取和解析功能。
- **[interfaces.py](file://E:\pythons\概率\core\interfaces.py)**：接口定义模块，定义核心功能的抽象接口，如卡池解析接口、模拟引擎接口等，便于模块间的解耦和扩展。
- **[probability.py](file://E:\pythons\概率\core\probability.py)**：抽卡模拟模块，实现抽卡逻辑和条件判断，是项目的核心功能模块。
- **[ydk_processor.py](file://E:\pythons\概率\core\ydk_processor.py)**：YDK 处理模块，处理 YDK 文件并转换为中文版 txt 卡表，提供 YDK 相关的数据处理功能。

#### [data](file://E:\pythons\概率\.venv\Lib\site-packages\PyInstaller\archive\writers.py#L0-L0) 目录

- **[local_cards.csv](file://E:\pythons\概率\data\local_cards.csv)**：本地卡牌数据文件，存储卡牌信息（id, name, field），供项目使用。

#### `gui` 目录

- **`frames` 目录**：
  - **[condition_frame.py](file://E:\pythons\概率\gui\frames\condition_frame.py)**：条件设置页面，用于选择和展示条件文件内容，提供条件设置的用户界面。
  - **[deck_frame.py](file://E:\pythons\概率\gui\frames\deck_frame.py)**：卡池设置页面，用于选择和展示卡池文件内容，提供卡池设置的用户界面。
  - **[result_display_frame.py](file://E:\pythons\概率\gui\frames\result_display_frame.py)**：结果展示页面，展示抽卡结果和满足概率，提供结果展示的用户界面。
  - **[simulation_run_frame.py](file://E:\pythons\概率\gui\frames\simulation_run_frame.py)**：模拟执行页面，配置参数并启动模拟，提供模拟执行的用户界面。
  - **[strategy_config_frame.py](file://E:\pythons\概率\gui\frames\strategy_config_frame.py)**：策略配置页面（具体功能待定），可能用于配置特定的抽卡策略。
- **`widgets` 目录**：
  - **[progress_bar.py](file://E:\pythons\概率\gui\widgets\progress_bar.py)**：进度条组件，用于显示模拟进度，提供进度条 UI 组件。
  - **[table_view.py](file://E:\pythons\概率\gui\widgets\table_view.py)**：表格视图组件，用于展示数据表格，提供表格视图 UI 组件。
- **[controller.py](file://E:\pythons\概率\gui\controller.py)**：控制器模块，管理各页面之间的状态流转和核心模块调用，是 GUI 的核心控制层。
- **[main_window.py](file://E:\pythons\概率\gui\main_window.py)**：主窗口类，构建整个 GUI 的基础框架，是 GUI 的入口文件。

#### `services` 目录

- **[condition_service.py](file://E:\pythons\概率\services\condition_service.py)**：条件服务模块，提供条件相关的业务逻辑，如条件解析、条件判断等。
- **[deck_service.py](file://E:\pythons\概率\services\deck_service.py)**：卡池服务模块，提供卡池相关的业务逻辑，如卡池解析、卡池管理等。
- **[simulation_service.py](file://E:\pythons\概率\services\simulation_service.py)**：模拟服务模块，封装抽卡模拟的业务逻辑，提供模拟执行的相关功能。
- **[ydk_service.py](file://E:\pythons\概率\services\ydk_service.py)**：YDK 服务模块，封装 YDK 相关的业务逻辑，提供 YDK 数据处理的相关功能。

#### `test` 目录

- **`...`**：测试相关文件，包含单元测试、集成测试等，用于保证代码质量和功能正确性。

#### [utils](file://E:\pythons\概率\.venv\Lib\site-packages\fastapi\utils.py#L0-L0) 目录

- **[logger.py](file://E:\pythons\概率\utils\logger.py)**：日志记录模块，提供日志记录功能，便于调试和问题追踪。

#### `构筑与启动` 目录

- **`...`**：构建和启动相关的文件（如示例卡池文件、条件文件等），提供项目运行所需的示例数据和配置。

#### [modify_text.py](file://E:\pythons\概率\modify_text.py)

- **[modify_text.py](file://E:\pythons\概率\modify_text.py)**：文本修改工具模块（具体功能待定），可能用于对文本进行特定的修改或处理。

### 总结

- **[config](file://E:\pythons\概率\.venv\Lib\site-packages\uvicorn\config.py#L0-L0) 和 [settings.py](file://E:\pythons\概率\config\settings.py)**：负责项目的全局配置。
- **[core](file://E:\pythons\概率\.venv\Lib\site-packages\pip\_vendor\idna\core.py#L0-L0) 目录**：包含项目的核心业务逻辑模块，如文件读取、抽卡模拟、YDK 处理等。
- **`services` 目录**：封装具体的业务服务，提供更高层次的业务逻辑支持。
- **`gui` 目录**：构建项目的图形用户界面（GUI），包括各个功能页面和 UI 组件。
- **[data](file://E:\pythons\概率\.venv\Lib\site-packages\PyInstaller\archive\writers.py#L0-L0) 目录**：存储项目所需的数据文件，如本地卡牌数据。
- **[utils](file://E:\pythons\概率\.venv\Lib\site-packages\fastapi\utils.py#L0-L0) 目录**：提供通用的工具模块，如日志记录。
- **`test` 目录**：包含项目的测试相关文件，确保代码质量。

