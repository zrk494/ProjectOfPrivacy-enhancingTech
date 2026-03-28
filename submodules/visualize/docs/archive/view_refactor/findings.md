# anomaly_view 重构发现

## detailedplan.md 分析

### 三层下钻式可视化方案
1. **第一层：全市场宏观概览**
   - 数据来源：market_stress_summary_*.csv 和 all_stress_events_*.csv
   - 展示：Top 压力事件排行榜、市场健康度对比条形图

2. **第二层：单市场事件汇总**
   - 数据来源：单市场 stress_events_enriched_*.csv
   - 展示：事件归因分布饼图、事件气泡图、事件详情列表

3. **第三层：单事件微观诊断**
   - 数据来源：bucket_features_*.csv 和 bucket_scores_*.csv
   - 展示：4个对齐的子图（综合压力评分、交易活跃度、流动性状态、价格走势）

## 当前代码状态
- `anomaly_view.py` 包含旧版实现，使用卡片式展示
- `sniper_detection` 部分需要保持不变
- `data_loader.py` 和 `paths.py` 已更新，支持新文件
