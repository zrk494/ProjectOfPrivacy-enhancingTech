# anomaly_view 重构任务计划

## 目标
重构 anomaly_view，采用三层下钻式可视化方案：
1. 第一层：全市场宏观概览（大盘视角）
2. 第二层：单市场事件汇总（事件视角）
3. 第三层：单事件微观诊断（切片视角）

维持 sniper_detection 部分不变，仅重构 Polymarket Anomaly Detection 部分。

## 阶段
| 阶段 | 状态 | 开始时间 | 完成时间 |
|------|------|----------|----------|
| 1. 分析需求和文档 | completed | 2026-03-28 | 2026-03-28 |
| 2. 检查语言配置文件 | completed | 2026-03-28 | 2026-03-28 |
| 3. 实现第一层：全市场宏观概览 | completed | 2026-03-28 | 2026-03-28 |
| 4. 实现第二层：单市场事件汇总 | completed | 2026-03-28 | 2026-03-28 |
| 5. 实现第三层：单事件微观诊断 | completed | 2026-03-28 | 2026-03-28 |
| 6. 集成三层视图并测试 | completed | 2026-03-28 | 2026-03-28 |

## 第一层：全市场宏观概览（大盘视角）
数据来源：`market_stress_summary_*.csv` 和 `all_stress_events_*.csv`

### 功能
1. Top 压力事件排行榜（数据表 Top-N Table）
   - 按 `peak_stress_score` 降序排列
   - 展示市场名称、发生时间、持续时长、总交易量
2. 市场健康度对比（条形图 Bar Chart）
   - 横轴：市场名称
   - 纵轴：`stress_events 数量`

## 第二层：单市场事件汇总（事件视角）
数据来源：单市场 `stress_events_enriched_*.csv`

### 功能
1. 事件归因分布（饼图/环形图 Pie Chart）
   - 使用 `dominant_driver` 字段
   - 展示 activity、liquidity、price_dislocation、mixed 事件比例
2. 事件气泡图/散点图（Scatter Plot）
   - 横轴：时间（`start_datetime`）
   - 纵轴：峰值异常分数（`peak_stress_score`）
   - 气泡大小：事件期间总交易量（`total_amount`）
   - 气泡颜色：主导驱动标签（`dominant_driver`）
3. 事件详情列表（Data Table）
   - 列出 `start_datetime`、`duration_minutes`、`max_spread` 等字段

## 第三层：单事件微观诊断（切片视角）
数据来源：`bucket_features_*.csv` 和 `bucket_scores_*.csv`

### 功能
使用共享 X 轴（时间轴）的多行折线图，用半透明背景色块高亮事件区间：

1. 综合压力评分图
   - 绘制 `stress_score` 折线
   - 画水平虚线代表异常阈值
2. 交易活跃度图（Activity）
   - 绘制 `trade_count`（柱状图）
   - 绘制 `amount_sum`（折线图）
3. 流动性状态图（Liquidity）
   - 绘制 `spread`（折线图）
   - 绘制 `total_depth`（面积图）
4. 价格走势图（Price）
   - 绘制 `midpoint`（折线图）

## 文件修改
- `config/language.py`：添加新的多语言字符串
- `views/anomaly_view.py`：重构 Polymarket Anomaly Detection 部分
- `data/data_loader.py`：已完成，无需修改
- `config/paths.py`：已完成，无需修改

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
