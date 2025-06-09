以下是一个 Markdown 文档，**简明扼要地介绍你提到的 6 个核心 Python 文件及其主要函数名称与作用**。适用于项目文档、开发手册或团队协作参考。

---

# 📁 模块功能概览

## 1️⃣ [ydk_service.py](file://E:\pythons\概率\services\ydk_service.py)  
> **负责 YDK 文件解析、卡牌数据获取、本地数据库更新**

| 函数名 | 参数说明 | 功能描述 |
|--------|----------|----------|
| [extract_field(types: str)](file://E:\pythons\概率\services\ydk_service.py#L16-L56) | 类型字符串（如 `"【怪兽、效果】战士族/炎"`） | 提取字段信息（种族、属性等），用于构建条件判断 |
| `process_raw_data(card_id: str, data: dict)` | 卡片 ID + 原始数据 | 处理 API 返回的卡片数据，提取 name 和 field |
| [ensure_hand_traps_loaded()](file://E:\pythons\概率\services\ydk_service.py#L91-L121) | - | 确保手坑卡组已加载并添加“手坑”字段 |
| [fetch_card(card_id: str)](file://E:\pythons\概率\services\ydk_service.py#L124-L135) | 卡片 ID | 获取单张卡牌数据并处理 |
| [batch_fetch_missing(ids: List[str])](file://E:\pythons\概率\services\ydk_service.py#L138-L146) | 卡片 ID 列表 | 批量下载缺失的卡牌数据 |
| [load_ydk_file(...)](file://E:\pythons\概率\gui\frames\main_frame.py#L65-L69) | source, is_path, field_tag | 加载并解析 YDK 数据，返回卡牌名称列表 |
| [export_to_txt(...)](file://E:\pythons\概率\services\ydk_service.py#L190-L201) | main_ids, extra_ids, side_ids | 将卡组导出为 TXT 构筑文件 |

---

## 2️⃣ [deck_service.py](file://E:\pythons\概率\services\deck_service.py)
> **封装卡组加载服务层接口，统一调用入口**

| 函数名 | 参数说明 | 功能描述 |
|--------|----------|----------|
| [get_deck(...)](file://E:\pythons\概率\services\deck_service.py#L6-L35) | source, is_ydk, is_path | 加载卡池（支持文本/YDK格式、路径/纯文本） |

---

## 3️⃣ [controller.py](file://E:\pythons\概率\gui\controller.py)
> **GUI 控制器，协调视图与业务逻辑交互**

| 方法名 | 参数说明 | 功能描述 |
|--------|----------|----------|
| [load_ydk(...)](file://E:\pythons\概率\gui\controller.py#L19-L25) | source, is_path, field_tag | 加载 YDK 数据 |
| [export_current_deck(...)](file://E:\pythons\概率\gui\controller.py#L27-L31) | output_file | 导出当前卡组为 TXT 文件 |
| [load_deck_txt(...)](file://E:\pythons\概率\gui\controller.py#L34-L39) | source, is_path | 加载 TXT 卡组 |
| [load_condition_txt(...)](file://E:\pythons\概率\gui\controller.py#L42-L47) | source, is_path | 加载 TXT 条件文件 |
| [run_simulation(...)](file://E:\pythons\概率\gui\controller.py#L50-L60) | draw_size, num_draws | 运行模拟主流程 |
| [_get_cids_from_names(...)](file://E:\pythons\概率\gui\controller.py#L62-L64) | card_names | 根据卡名获取对应 ID |
| [add_field_to_cards(...)](file://E:\pythons\概率\gui\controller.py#L66-L67) | cids, field | 添加字段到指定卡组 |
| [update_card_field(...)](file://E:\pythons\概率\gui\controller.py#L69-L70) | cid, old_field, new_field | 更新某张卡的字段 |
| [remove_card_field(...)](file://E:\pythons\概率\gui\controller.py#L72-L73) | cid, field | 移除某张卡的字段 |
| [get_all_fields()](file://E:\pythons\概率\gui\controller.py#L75-L76) | - | 获取所有可用字段 |
| [search_cards_by_keyword(...)](file://E:\pythons\概率\gui\controller.py#L78-L80) | keyword | 根据关键词搜索卡牌 |
| [refresh_local_db()](file://E:\pythons\概率\gui\controller.py#L82-L83) | - | 刷新本地数据库缓存 |

---

## 4️⃣ [condition_service.py](file://E:\pythons\概率\services\condition_service.py)
> **启动条件加载服务层接口**

| 函数名 | 参数说明 | 功能描述 |
|--------|----------|----------|
| [get_conditions(...)](file://E:\pythons\概率\services\condition_service.py#L5-L9) | source, is_path | 加载并解析启动条件文件 |

---

## 5️⃣ [local_db_service.py](file://E:\pythons\概率\services\local_db_service.py)
> **本地 CSV 数据库操作，提供字段管理与查询能力**

| 类/方法名 | 参数说明 | 功能描述 |
|-----------|----------|----------|
| [LocalCardDB](file://E:\pythons\概率\services\local_db_service.py#L14-L180) | - | 初始化本地数据库对象 |
| [load_existing_data()](file://E:\pythons\概率\services\local_db_service.py#L22-L39) | - | 从 CSV 加载已有数据 |
| [refresh()](file://E:\pythons\概率\services\local_db_service.py#L41-L44) | - | 重新加载数据库 |
| [get_card_name(cid)](file://E:\pythons\概率\services\local_db_service.py#L47-L50) | cid | 获取卡牌名称 |
| [get_all_cards()](file://E:\pythons\概率\services\local_db_service.py#L52-L53) | - | 获取全部卡牌字典 |
| [has_field(cid, keyword)](file://E:\pythons\概率\services\local_db_service.py#L56-L57) | cid, keyword | 是否包含某个字段 |
| [get_card_fields(cid)](file://E:\pythons\概率\services\local_db_service.py#L59-L60) | cid | 获取该卡的所有字段 |
| [get_all_fields()](file://E:\pythons\概率\gui\controller.py#L75-L76) | - | 获取所有存在的字段标签 |
| [add_card_field(...)](file://E:\pythons\概率\services\local_db_service.py#L69-L78) | cid, field | 添加字段到卡牌 |
| [remove_card_field(...)](file://E:\pythons\概率\gui\controller.py#L72-L73) | cid, field | 移除卡牌字段 |
| [update_card_field(...)](file://E:\pythons\概率\gui\controller.py#L69-L70) | cid, old_field, new_field | 修改卡牌字段 |
| [update_cards_field(...)](file://E:\pythons\概率\services\local_db_service.py#L103-L121) | cids, new_field | 批量添加字段 |
| [save_new_cards(new_data)](file://E:\pythons\概率\services\local_db_service.py#L124-L154) | new_data | 保存新卡数据至 CSV |
| [_save_updated_fields(...)](file://E:\pythons\概率\services\local_db_service.py#L156-L180) | updated_cids | 保存字段变更 |

---

## 6️⃣ [simulation_service.py](file://E:\pythons\概率\services\simulation_service.py)
> **模拟运行服务层接口，执行抽卡测试与结果输出**

| 函数名 | 参数说明 | 功能描述 |
|--------|----------|----------|
| [run_simulation(...)](file://E:\pythons\概率\gui\controller.py#L50-L60) | card_pool, conditions, draw_size, num_draws | 主控流程：执行抽卡模拟并报告结果 |
| [report_snapshots(...)](file://E:\pythons\概率\services\simulation_service.py#L25-L31) | snapshots, conditions | 输出抽卡快照日志 |
| [summarize_results(...)](file://E:\pythons\概率\engine\probability_engine.py#L45-L70) | matched_indices, titles | 总结匹配情况与概率统计 |

---

# 📌 总结

| 文件 | 职责 |
|------|------|
| [ydk_service.py](file://E:\pythons\概率\services\ydk_service.py) | YDK 文件解析、卡牌数据获取、CSV 更新 |
| [deck_service.py](file://E:\pythons\概率\services\deck_service.py) | 卡组加载服务层接口 |
| [controller.py](file://E:\pythons\概率\gui\controller.py) | GUI 控制器，连接视图和业务逻辑 |
| [condition_service.py](file://E:\pythons\概率\services\condition_service.py) | 启动条件加载 |
| [local_db_service.py](file://E:\pythons\概率\services\local_db_service.py) | 本地 CSV 数据库读写、字段管理 |
| [simulation_service.py](file://E:\pythons\概率\services\simulation_service.py) | 抽卡模拟主流程及结果输出 |

---

📌 如需我为你生成完整的中文文档（含参数说明、使用示例、调用链图等），请告诉我 👇 我可以输出 [.md](file://E:\pythons\概率\TODO.md) 或 `.docx` 格式供你使用。