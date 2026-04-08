# 任务规划 - Market ID 显示修复

## 目标
修复 `anomaly_view.py` 中 Top 压力事件排行榜的显示问题：将 `market_file` 列从 `572473_YES` 格式改为只显示 market ID（如 `572473`）。

## 问题分析
- 文件位置：`submodules/visualize/views/anomaly_view.py` 第 73-74 行
- 当前代码：
  ```python
  display_cols = ['market_file', 'start_datetime', 'duration_minutes', 'total_amount', 'peak_stress_score']
  existing_cols = [c for c in display_cols if c in top_events.columns]
  ```
- 问题：`market_file` 列显示的是 `{market_id}_YES` 格式，但用户只需要 market ID

## 解决方案
1. 在显示前处理 `market_file` 列，提取纯数字 ID
2. 或者添加一个新的 `market_id` 列用于显示

## 阶段

### 阶段 1: 代码修改
- [x] 修改 `display_layer1_market_overview` 函数
- [x] 提取 `market_file` 中的纯数字 ID
- [x] 重命名列为 `market_id` 以更好地反映内容

### 阶段 2: 测试验证
- [ ] 验证修改后的显示效果
- [ ] 确保不破坏其他功能

## 决策记录
- 选择方案：在 DataFrame 显示前处理数据，提取 market_id
- 实现方式：使用字符串分割提取 `_` 前的部分
