# 研究发现

## 问题定位
- 文件：`submodules/visualize/views/anomaly_view.py`
- 行号：第 72-75 行
- 相关函数：`display_layer1_market_overview`

## 数据结构分析
- `all_events_df` 由 `load_all_stress_events()` 加载
- 数据文件路径：`submodules/algorithm/CS6290-polymarket-anomaly-detection/results/activity_pipeline_batch/all_stress_events_{score_method}.csv`
- `market_file` 列格式：`{market_id}_YES`（例如：`572473_YES`）

## 解决方案
将 `market_file` 列处理为纯 market ID：
```python
# 提取 market_id（去掉 _YES 后缀）
if 'market_file' in top_events.columns:
    top_events['market_id'] = top_events['market_file'].str.split('_').str[0]
```

## 修改计划
1. 修改 `display_cols` 列表，将 `'market_file'` 替换为 `'market_id'`
2. 在显示前添加数据处理逻辑，从 `market_file` 提取 `market_id`
