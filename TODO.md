你提到得非常对！当前的 [TODO.md](file://E:\pythons\概率\TODO.md) 更像是一个 **功能清单**，但缺少了 **开发步骤、模块依赖顺序、优先级划分和迭代路线**。我们来为它加上 **开发计划与实施步骤**，使其成为一个真正能指导开发的文档。

---

# ✅ 优化后的 TODO.md（含开发步骤）




## 🧭 开发路线图

> 本项目目标：实现一个基于 Tkinter 的卡组概率模拟器，支持导入卡池文件、条件文件，并可视化显示抽卡结果与满足概率。

---

## 🚀 开发阶段规划

| 阶段 | 目标 | 状态 |
|------|------|------|
| Phase 1: 核心逻辑验证 | 完成文件解析、抽卡模拟、策略判断等核心模块 | ✅ 已完成 |
| Phase 2: GUI 界面搭建 | 使用 Tkinter 实现基础界面交互 | 🟡 待开始 |
| Phase 3: 模块整合 | 将逻辑模块与 GUI 结合，实现完整流程 | 🔳 待开发 |
| Phase 4: 图表展示 | 添加 matplotlib 支持，绘制概率柱状图/饼图 | 🔳 待开发 |
| Phase 5: 打包发布 | 使用 PyInstaller 打包为 EXE 并提供压缩包分发 | 🔳 待开发 |

---

## 🛠️ 开发步骤细化

### Step 1：确认并完善核心模块
- [x] 文件读取 ([file_read.py](file://E:\pythons\概率\file_read.py))
  - [x] 卡池解析（parse_first_document）
  - [x] 条件解析（parse_second_document）
- [x] 抽卡模拟 ([probability.py](file://E:\pythons\概率\probability.py))
  - [x] 随机抽卡逻辑
  - [x] 特殊卡牌策略处理
  - [x] 条件判断
  - [x] 多次模拟统计
- [x] YDK 解析模块 ([for_ydk.py](file://E:\pythons\概率\for_ydk.py))
  - [x] 提取 main / extra / side 区域
  - [x] 获取本地或 API 卡牌信息
  - [] 将异画的ydk写入，并且作为代码底层逻辑
  - [] 修改条件判断条件，支持&|运算
  - [] 修改条件文本的读取，使得#成为一次分组
✅ 输出物：
- 可独立运行的脚本（如 `python probability.py` 测试模拟流程）
- 单元测试覆盖主要函数

# TODO.md

## 🧭 项目目标

> 实现一个基于 Tkinter 的卡组概率模拟器，支持导入卡池文件、条件文件，并可视化显示抽卡结果与满足概率。

---

## 🚀 开发阶段规划

| 阶段 | 目标 | 状态 |
|------|------|------|
| Phase 1: 核心逻辑验证 | 完成文件解析、抽卡模拟、策略判断等核心模块 | ✅ 已完成 |
| Phase 2: GUI 界面搭建 | 使用 Tkinter 构建完整界面交互流程 | 🟡 待开始 |
| Phase 3: 模块整合 | 将逻辑模块与 GUI 结合，实现完整流程 | 🔳 待开发 |
| Phase 4: 图表展示 | 添加 matplotlib 支持，绘制概率柱状图/饼图 | 🔳 待开发 |
| Phase 5: 打包发布 | 使用 PyInstaller 打包为 EXE 并提供压缩包分发 | 🔳 待开发 |

---

## 🛠️ 开发步骤细化（Phase 2：GUI 构建）

### Step 2.1 创建主窗口类 `MainWindow`

#### 文件路径：
- `gui/main_window.py`

#### 功能要求：
- 继承 `tk.Tk`
- 设置窗口标题为 "YGO 卡组概率计算器"
- 设置窗口大小为 `800x600`
- 设置图标 (`icon.ico`)
- 添加菜单栏（包含“文件”、“工具”、“帮助”）
- 初始化页面容器（用于切换不同功能页）

#### 子任务分解：
- [ ] 创建类 `class MainWindow(tk.Tk):`
- [ ] 设置窗口基本属性（尺寸、标题、图标）
- [ ] 添加菜单栏：
  - “文件”菜单：打开卡池文件、打开条件文件、退出程序
  - “工具”菜单：启动文本修改工具界面
  - “帮助”菜单：关于、使用说明弹窗
- [ ] 使用 `ttk.Notebook` 或 `Frame` 切换页面
- [ ] 设置默认字体、样式（可选）

---

### Step 2.2 分模块开发 GUI 页面

#### 2.2.1 卡池设置页面 `CardPoolFrame`

##### 文件路径：
- `gui/card_pool_frame.py`

##### 功能要求：
- 显示“卡池文件路径”
- 提供“选择文件”按钮
- 显示已加载的卡池内容预览（Text 组件）
- 支持自动解析并缓存卡池数据

##### 子任务分解：
- [ ] 创建类 `CardPoolFrame(tk.Frame)`
- [ ] 添加 Label + Entry 显示文件路径
- [ ] 添加 Button 触发文件选择对话框（使用 `filedialog.askopenfilename()`）
- [ ] 添加 Text 组件显示卡池内容预览
- [ ] 绑定事件：选择文件后调用 [file_read.read_file()](file://E:\pythons\概率\file_read.py#L69-L78) 和 [file_read.parse_first_document()](file://E:\pythons\概率\file_read.py#L3-L30)
- [ ] 缓存卡池数据供后续使用

---

#### 2.2.2 条件设置页面 `ConditionFrame`

##### 文件路径：
- `gui/condition_frame.py`

##### 功能要求：
- 显示“条件文件路径”
- 提供“选择文件”按钮
- 显示条件列表预览（Table 或 Listbox）
- 支持多条件高亮或编号显示

##### 子任务分解：
- [ ] 创建类 `ConditionFrame(tk.Frame)`
- [ ] 添加 Label + Entry 显示文件路径
- [ ] 添加 Button 触发文件选择对话框
- [ ] 添加 Treeview 或 Listbox 展示条件列表
- [ ] 绑定事件：选择文件后调用 [file_read.read_file()](file://E:\pythons\概率\file_read.py#L69-L78) 和 [file_read.parse_second_document()](file://E:\pythons\概率\file_read.py#L33-L67)
- [ ] 缓存条件列表供后续使用

---

#### 2.2.3 模拟执行页面 `SimulationFrame`

##### 文件路径：
- `gui/simulation_frame.py`

##### 功能要求：
- 显示参数输入控件（num_draws, N, pot_card_number）
- 添加“开始模拟”按钮
- 添加日志输出区域（Text 组件）
- 支持暂停/停止模拟（可选）

##### 子任务分解：
- [ ] 创建类 `SimulationFrame(tk.Frame)`
- [ ] 添加 Label + Entry 控件用于配置参数
- [ ] 添加“开始模拟”按钮绑定事件处理函数
- [ ] 添加 Text 组件显示模拟过程日志
- [ ] 调用 [probability.simulate_and_report()](file://E:\pythons\概率\probability.py#L196-L206) 启动模拟
- [ ] 添加进度条（可选）

---

#### 2.2.4 结果展示页面 `ResultFrame`

##### 文件路径：
- `gui/result_frame.py`

##### 功能要求：
- 显示各条件满足概率（表格形式）
- 支持导出结果为 CSV 文件
- 可视化图表展示（后期扩展）

##### 子任务分解：
- [ ] 创建类 `ResultFrame(tk.Frame)`
- [ ] 使用 `Treeview` 表格组件展示每种情况的概率
- [ ] 添加“导出为 CSV”按钮
- [ ] 支持将结果保存至 `results/` 文件夹
- [ ] （可选）添加 Matplotlib 图表嵌入（见 Step 4）

---

### Step 2.3 控制器层开发 `Controller`

#### 文件路径：
- `gui/controller.py`

#### 功能要求：
- 管理各页面之间的状态流转
- 负责调用核心模块接口
- 处理用户输入并更新 UI

##### 子任务分解：
- [ ] 创建控制器类 `AppController`
- [ ] 在 `MainWindow` 中初始化控制器实例
- [ ] 注册各页面对象（如 `card_pool_frame`, `condition_frame`, `simulation_frame`, `result_frame`）
- [ ] 定义回调方法：
  - `on_select_card_pool_file()` → 更新卡池数据
  - `on_select_condition_file()` → 更新条件列表
  - `on_start_simulation()` → 启动模拟并跳转结果页
  - `on_export_results()` → 导出 CSV
- [ ] 添加异常提示弹窗（如文件格式错误、空文件等）

---

## 🔄 Step 3：模块整合（MVC 整合）

#### 文件路径：
- `main_window.py`（入口）
- `controller.py`（协调者）
- 各 Frame 类负责 View 层

##### 子任务分解：
- [ ] 引入 core 模块：
  - `import file_read`
  - `import probability`
- [ ] 在 controller 中封装模拟调用逻辑：
- [ ] 绑定按钮点击事件 → 触发模拟 → 更新结果页
- [ ] 添加日志记录机制（可选）

---

## 📊 Step 4：图表展示（可选）

#### 文件路径：
- `gui/chart_frame.py`
- `utils/chart_helper.py`

##### 功能要求：
- 使用 `matplotlib` 绘制柱状图 / 折线图
- 嵌入在 Tkinter 窗口中

##### 子任务分解：
- [ ] 安装依赖：`pip install matplotlib`
- [ ] 创建 `ChartFrame(tk.Frame)` 类
- [ ] 添加按钮触发图表绘制
- [ ] 使用 `FigureCanvasTkAgg` 将图表嵌入 Tkinter
- [ ] 支持切换视图模式（柱状图 vs 饼图）

---

## 📦 Step 5：打包为 EXE 并发布

#### 文件路径：
- `pyinstaller.spec`（打包配置）
- `README.txt`（说明文档）

##### 子任务分解：

#### T1 准备打包环境
- [ ] 安装 PyInstaller：`pip install pyinstaller`
- [ ] 安装 matplotlib（如含图表）：`pip install matplotlib`
- [ ] 安装 Pillow（如含图片）：`pip install pillow`

#### T2 添加资源文件
- [ ] 将以下资源放入 `resources/` 文件夹：
  - 示例卡池文件 `sample_cards.txt`
  - 示例条件文件 `sample_conditions.txt`
  - 图标文件 `icon.ico`
  - 图表资源（如有）

#### T3 编写 README.txt 使用说明
- [ ] 包含以下内容：
  - 程序简介
  - 如何导入卡池/条件文件
  - 参数说明
  - 使用注意事项
  - 版本信息

#### T4 编写打包命令
- [ ] 编写 spec 文件或直接使用命令行打包：
#### T5 制作压缩包
- [ ] 构建发布包内容：
  - `dist/main_window.exe`
  - `resources/` 文件夹
  - `README.txt`
  - `icon.ico`
- [ ] 推荐命名方式：`YGO_概率计算器_v1.0.zip`

---

## 📁 项目目录结构建议

