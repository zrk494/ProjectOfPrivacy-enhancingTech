# anomaly_view 重构进度日志

## 2026-03-28
- 开始任务：anomaly_view 重构
- 读取 detailedplan.md 文档，理解三层下钻式可视化方案
- 分析当前 anomaly_view.py 代码结构
- 创建 task_plan.md、findings.md、progress.md 规划文件
- 更新 config/language.py，添加新的多语言字符串
- 重构 views/anomaly_view.py，实现三层下钻式可视化方案：
  - 第一层：全市场宏观概览（Top 压力事件排行榜 + 市场健康度对比条形图）
  - 第二层：单市场事件汇总（事件归因分布饼图 + 事件气泡图 + 事件详情列表）
  - 第三层：单事件微观诊断（4个对齐的时间序列子图：综合压力评分、交易活跃度、流动性状态、价格走势）
- 保持 sniper_detection 部分不变
