# Visualize 模块架构与接口设计文档

本文档旨在阐述 `Visualize` 子模块的设计思想、内部架构流转，以及与 `Algorithm`（底层算法）子模块之间的数据契约（Interface Spec）。

## 1. 架构演进与设计原则

早期的可视化模块为一个庞大的单文件结构，随着需求增加，面临路径硬编码、代码耦合严重、性能瓶颈等问题。在 **Phase 2（代码重构阶段）**，我们将系统升级为标准的**分层架构**，并已完成所有开发阶段。

### 1.1 分层职责说明

- **配置层 (`config/`)**：
  - **核心痛点解决**：消除硬编码。`paths.py` 负责在运行时基于当前文件位置动态推断 `PROJECT_ROOT`，极大地增强了代码在不同操作系统和不同克隆路径下的鲁棒性。
  - **多语言支持**：通过 `language.py` 字典实现简单的 i18n 机制，通过 `st.session_state.language` 驱动视图层更新。
- **数据访问层 (`data/`)**：
  - 作为底层 CSV/JSON 文件和上层 UI 之间的防腐层。`data_loader.py` 只负责 I/O 操作；`data_processor.py` 负责在内存中进行数据类型转换（如日期解析）、排序和清洗。
- **视图层 (`views/`)**：
  - 采取积木式的设计，主入口 `app.py` 仅作为路由中心。实际的渲染逻辑被拆分到 `metadata_view`, `timeseries_view`, `trade_view`, `anomaly_view` 中，提升了代码的可读性和多人协作效率。
- **工具层 (`utils/`)**：
  - 提供通用工具函数，包括缓存管理、错误处理和 UI 组件，提高代码复用性。

## 2. 数据流与缓存策略

Polymarket 的逐笔交易数据（Order/Trade）可能非常庞大（高达三十多万条记录），直接渲染会导致前端假死。

**优化策略**：

1. **文件级缓存**：在 `data_loader.py` 的读取函数上广泛使用 `@st.cache_data`。Streamlit 会对函数参数和文件内容计算 Hash，仅在数据文件发生变更或应用首次启动时读取磁盘。
2. **前端分页与降采样**：图表展示采用 Plotly 进行渲染，结合 `st.dataframe` 的内置优化，避免在 DOM 中一次性生成过多节点。

## 3. 算法子模块集成规范 (Interface Spec)

`Visualize` 模块不直接执行计算密集的算法，而是通过**读取标准化输出文件**的方式与 `Algorithm` 模块进行异步解耦。

### 3.1 狙击手检测 (Sniper Detection - Type B)

- **数据来源目录**：`frontend_sniper_detection/`
- **核心契约文件**：
  1. **`stats/strict_sniper_candidates.csv`** (宏观候选列表)
     - 实际记录数：41 条。
     - 必需字段：`session_id` (主键), `num_trades`, `total_volume`, `max_trade`, `has_large_trade`, `first_side`, `last_side`, `anomaly_score`, `is_sniper`, `suspicious_rank`。
  2. **`detailed_cases.json`** (已验证案例详情)
     - 实际记录数：3 条（rank 2, 3, 4）。
     - 预期格式：包含 `rank`, `session_id`, `duration_seconds`, `anomaly_score`, `buy`, `sell`, `profit`, `image` 等字段。
  3. **`all_cases.json`** (所有候选案例)
     - 实际记录数：41 条。
  4. **`images/`** (可视化辅助)
     - 实际数量：7 张图片，以 `sniper_rank*.png` 命名的静态图表，直接用于 UI 渲染。

### 3.2 市场压力异常检测 (Market Stress - Type A)

- **数据来源目录**：`submodules/algorithm/CS6290-polymarket-anomaly-detection/results/`
- **核心契约文件**：
  1. **`stress_events_enriched_{score_method}.csv`**
     - 必需字段：`start_datetime`, `end_datetime`, `duration_minutes`, `peak_stress_score`, `total_amount`, `max_abs_midpoint_return`, `max_spread`, `min_total_depth`, `max_abs_depth_imbalance`, `snapshot_covered`, `num_snapshot_buckets`, `activity_component`, `liquidity_component`, `price_component`, `dominant_driver`。
  2. **`bucket_features_*.csv` / `bucket_scores_*.csv`**
     - 用于支持前端展示压力分数的随时间变化趋势图（如果需要下钻分析）。

## 4. 异常数据视图架构

### 4.1 视图概述

异常数据视图（`anomaly_view.py`）是 Visualize 模块的核心组件之一，负责展示两种类型的异常检测结果：

1. **市场压力异常检测（Type A - Market Stress）**：采用三层下钻式可视化方案
2. **狙击手检测（Type B - Sniper Detection）**：采用卡片式布局展示

### 4.2 市场压力异常检测架构（三层下钻式）

#### 4.2.1 设计理念

采用"从宏观到微观"（Top-Down）的三层下钻式可视化方案，帮助用户从全市场视角逐步深入到具体事件的微观分析。

#### 4.2.2 第一层：全市场宏观概览（大盘视角）

**数据来源**：
- `market_stress_summary_{score_method}.csv`：市场压力汇总数据
- `all_stress_events_{score_method}.csv`：所有压力事件总表

**展示内容**：
- Top 压力事件排行榜：按 `peak_stress_score` 降序排列，展示全市场最严重的异常事件
- 市场健康度对比：条形图展示各市场异常事件频率

**技术实现**：
- 使用 `load_market_stress_summary()` 和 `load_all_stress_events()` 加载数据
- 使用 Plotly 条形图 (`px.bar`) 可视化市场健康度
- 使用 Streamlit 数据表格展示 Top 事件

#### 4.2.3 第二层：单市场事件汇总（事件视角）

**数据来源**：
- `stress_events_enriched_{score_method}.csv`：单市场富化事件数据

**展示内容**：
- 事件归因分布：饼图展示 `dominant_driver` 分布（activity/liquidity/price_dislocation/mixed）
- 事件气泡图：时间轴上的事件分布，气泡大小表示交易量，颜色表示驱动因素
- 事件详情列表：展示事件的详细指标

**技术实现**：
- 使用 `load_polymarket_anomaly_data()` 加载单市场数据
- 使用 `process_anomaly_data()` 进行数据预处理
- 使用 Plotly 饼图 (`px.pie`) 和散点图 (`px.scatter`) 可视化
- 支持用户选择特定事件进入第三层

#### 4.2.4 第三层：单事件微观诊断（切片视角）

**数据来源**：
- `bucket_features_{score_method}.csv`：时间桶特征数据
- `bucket_scores_{score_method}.csv`：时间桶分数数据

**展示内容**：
- 四个对齐的子图，共享时间轴（X轴）：
  1. 综合压力评分图：`stress_score` 折线 + 异常阈值虚线
  2. 交易活跃度图：`trade_count` 柱状图 + `amount_sum` 折线图
  3. 流动性状态图：`spread` 折线图 + `total_depth` 面积图
  4. 价格走势图：`midpoint` 折线图
- 使用半透明背景色块高亮事件区间

**技术实现**：
- 使用 `load_bucket_features()` 和 `load_bucket_scores()` 加载时间桶数据
- 使用 `make_subplots()` 创建四行一列的子图布局
- 使用 `add_vrect()` 添加事件高亮区域
- 时间范围扩展：事件前后各 10 分钟

### 4.3 狙击手检测架构（卡片式布局）

#### 4.3.1 设计理念

采用"Detective Report"卡片式 UI 范式，通过分层展示和视觉反馈，帮助用户快速识别和理解狙击手行为。

#### 4.3.2 核心组件

**统计概览模块**：
- 狙击手候选总数
- 平均异常分数
- 已验证案例数量

**分数分布分析模块**：
- 使用 Plotly 直方图展示异常分数分布
- 横坐标：异常分数，纵坐标：频率

**已验证案例展示模块**：
- 卡片式布局，每个案例独立展示
- 卡片内容：案例排名、会话ID、持续时间、异常分数、获利情况
- 支持展开查看详细信息：
  - 买入操作详情（金额、价格、时间、交易哈希）
  - 卖出操作详情（金额、价格、时间、交易哈希）
  - 攻击窗口可视化图片

**狙击手候选列表模块**：
- 按可疑度排名排序
- 分页显示（每页 5 个候选）
- 风险等级颜色标识：
  - 高风险：红色（异常分数 < -0.6）
  - 中风险：橙色（-0.6 ≤ 异常分数 < -0.5）
  - 低风险：绿色（异常分数 ≥ -0.5）

#### 4.3.3 技术实现

**数据加载**：
- `load_sniper_detection_data()`：加载狙击手候选数据
- `load_sniper_detailed_cases()`：加载已验证案例数据

**状态管理**：
- 使用 Streamlit 会话状态 (`st.session_state`) 管理分页
- 分页参数：`sniper_page` 记录当前页码

**可视化组件**：
- 使用 Plotly 直方图 (`go.Histogram`) 展示分数分布
- 使用 Streamlit 容器 (`st.container`) 和 HTML 样式创建卡片
- 使用 `st.expander` 实现详情展开功能
- 使用 `st.image` 展示攻击窗口图片

**交互设计**：
- 分页控制：上一页/下一页按钮
- 详情展开：点击 "查看详情" 按钮
- 视觉反馈：根据异常分数和获利情况使用不同颜色

### 4.4 异常数据视图在整体架构中的位置

```
┌─────────────────────────────────────────────────────────┐
│                      app.py (路由层)                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              views/anomaly_view.py (视图层)               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  display_anomaly_view()                            │ │
│  │    ├── display_polymarket_anomaly_new() [三层下钻] │ │
│  │    └── display_sniper_detection_cards() [卡片式]   │ │
│  └────────────────────────────────────────────────────┘ │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────────────┐  ┌─────────────────────┐
│   data/data_loader  │  │   config/paths.py   │
│   (数据访问层)      │  │   (路径配置层)      │
└─────────────────────┘  └─────────────────────┘
```

### 4.5 技术选型说明

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| 可视化图表 | Plotly | 交互性强，支持复杂图表类型 |
| 布局框架 | Streamlit | 快速构建 Web 应用，内置组件丰富 |
| 状态管理 | Streamlit Session State | 简单易用，自动处理状态同步 |
| 数据处理 | Pandas | 强大的数据处理能力 |
| 缓存机制 | @st.cache_data | 自动缓存，提升性能 |

### 4.6 性能优化策略

1. **数据缓存**：所有数据加载函数使用 `@st.cache_data` 装饰器
2. **分页显示**：狙击手候选列表采用分页机制，减少单次渲染数据量
3. **条件渲染**：仅在数据存在时渲染相应组件
4. **懒加载**：详情信息仅在用户展开时加载
5. **前端优化**：使用 Plotly 的内置优化，避免 DOM 过载

## 5. UI 交互设计范式 (Detective Report)

在 `anomaly_view.py` 中，我们已实现名为 **"Detective Report"** 的卡片式 UI 范式，以统一不同类型异常的呈现体验：

- **视觉层级**：使用 `st.expander` 包裹单一异常事件，提供清晰的视觉层次。
- **危险程度标识**：基于 `anomaly_score` 或 `peak_stress_score` 动态渲染颜色标签（如 🔴 高风险, 🟡 中等风险）。
- **图文并茂**：对于狙击手事件，将基础数据表格与 `images/` 中的攻击窗口折线图并排显示（`st.columns`），提供直观的证据链。
- **交互溯源**：提供原始数据的展开查看功能，方便审核人员（如课程助教）验证算法结果。
- **排序与分页**：支持按时间、可疑度等维度排序，以及分页显示，提升用户体验。

## 6. 风险与后续优化

- **路径脆弱性**：当前仍依赖相对固定的目录结构。如果在部署服务器上目录结构发生变动，可能会导致数据读取失败。
- **实时性**：当前架构为离线静态数据分析。未来若需支持实时 Polymarket API 数据，需引入 `st.cache_resource` 维护 WebSocket 连接，并重构 `data_loader` 逻辑。
- **数据验证**：可进一步增强数据完整性校验，确保在数据缺失或格式错误时提供友好的错误提示。
- **测试覆盖**：建议添加单元测试和集成测试，提高代码质量和可靠性。