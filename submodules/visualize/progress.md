# 进度日志

## 2026-03-28
### 任务启动
- 创建规划文件系统
- 分析代码问题

### 问题理解
- 用户希望 Top 压力事件排行榜中显示 market ID 而不是 `market_file`
- 当前 `market_file` 格式：`572473_YES`
- 期望显示：`572473`

### 代码修改完成
- 修改了 `anomaly_view.py` 第 71-77 行
- 添加了从 `market_file` 提取 `market_id` 的逻辑
- 将 `display_cols` 中的 `'market_file'` 替换为 `'market_id'`

### 修改内容
```python
# 从 market_file 提取 market_id（去掉 _YES 后缀）
if 'market_file' in top_events.columns:
    top_events['market_id'] = top_events['market_file'].str.split('_').str[0]
display_cols = ['market_id', 'start_datetime', 'duration_minutes', 'total_amount', 'peak_stress_score']
```

### 状态
- [x] 阶段 1: 代码修改 - 已完成
- [ ] 阶段 2: 测试验证 - 待进行
