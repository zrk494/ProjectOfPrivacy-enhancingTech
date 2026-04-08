# Polymarket 市场压力异常检测管线

## 1. 项目概述

本项目构建了一个面向 Polymarket YES-side 市场的**市场压力异常检测管线（market stress detection pipeline）**。

我们的目标**不是**预测市场最终结果是否为真，也**不是**直接预测价格涨跌。  
我们的目标是识别**异常市场压力事件（market stress events）**：也就是市场在短时间内出现了显著异常的交易活跃度、流动性恶化或价格偏移现象。

整个系统使用两类数据：

- **Trade 数据**：逐笔交易记录
- **Timeseries / Snapshot 数据**：市场状态快照，例如 midpoint、spread、depth、imbalance 等

系统会先把原始数据聚合到固定时间桶中，然后计算异常特征，对每个时间桶打分，再把相邻异常时间桶合并成事件，最后用 snapshot 特征对事件进行补充解释和归因分析。

---

## 2. Threat Model（威胁模型）

### 2.1 我们关注的异常行为是什么？

我们关注的是**市场压力异常事件**，即市场在短时间内表现出明显扰动或不稳定状态。

这些事件可能与以下情况有关：

- 交易活动突然异常升高
- 流动性突然恶化
- 短时价格发生异常偏移
- 对新闻、谣言、群体行为或潜在操纵行为的剧烈反应

### 2.2 我们的攻击者 / 风险假设是什么？

我们**不假设**能够仅凭数据直接证明某个参与者具有恶意操纵意图。

我们的威胁模型是：

> 大户、机器人、外部冲击或其他异常因素，可能会在市场中制造短时间的异常压力，并在交易活跃度、流动性状态和短时价格行为上留下可测量的痕迹。

换句话说，我们希望识别以下几类高风险异常：

- **Activity shock（交易活跃度冲击）**：短时间内 trade count、交易金额、平均单笔交易额异常升高
- **Liquidity shock（流动性冲击）**：spread 明显扩大、总深度下降、订单簿失衡加剧
- **Price dislocation shock（价格偏移冲击）**：midpoint 在短时间内发生异常波动

这些信号本身并不直接证明市场操纵，但能够帮助我们定位**值得进一步检查的异常时间段**。

### 2.3 我们最终要检测什么？

我们要检测的是**市场压力异常事件（market stress events）**，定义为：

> 某一连续时间窗口内，时间桶级别的 stress score 相对于该市场近期历史显著偏高，并超过异常阈值。

同时，我们还希望进一步判断每个异常事件主要由什么驱动：

- **activity-driven**：交易活跃度主导
- **liquidity-driven**：流动性异常主导
- **price-dislocation-driven**：价格偏移主导
- **mixed**：多种因素共同驱动

---

## 3. 我们的检测目标

本项目试图回答的问题是：

> Polymarket 市场在什么时候进入了“统计意义上的异常压力状态”？

更具体地说，我们要识别那些在以下维度上表现异常的时间窗口：

### 1）交易活跃度异常
例如：
- 单位时间内成交笔数过多
- 单位时间内成交金额过大
- 平均单笔交易额异常大

### 2）流动性异常
例如：
- spread 异常扩大
- total depth 明显下降
- order book imbalance 显著失衡

### 3）价格行为异常
例如：
- midpoint 在短时间内出现异常偏移

我们不仅希望标记单个异常点，还希望把相邻异常点合并成**事件级别（event-level）**的异常区间，因为真实市场压力通常不是单点发生，而是具有持续性的短时间过程。

---

## 4. 整体流程概览

整个异常检测流程可以分为六个阶段：

1. **将逐笔交易聚合到固定时间桶**
2. **将 snapshot / timeseries 数据聚合到同样的时间桶**
3. **融合 trade 特征和 snapshot 特征**
4. **对每个时间桶计算 stress score**
5. **标记异常时间桶并合并成事件**
6. **对事件进行补充解释和归因分析**

---

## 5. 逐步流程解释

### Step 1. Trade 数据聚合

#### 输入
单个市场的原始逐笔交易记录，通常包含：
- timestamp
- size / amount
- price
- side 或相关字段（视原始数据格式而定）

#### 我们做什么
我们将原始 trade 数据聚合为固定长度的时间桶（当前使用 **60 秒**）。

对每个时间桶，我们计算如下交易特征：

- `trade_count`：该时间桶内的成交笔数
- `amount_sum`：该时间桶内的成交总金额
- `avg_trade_size`：该时间桶内的平均单笔成交额

#### 为什么这样做
原始逐笔数据过于细碎、噪声大，不适合直接做事件检测。  
时间桶聚合可以把市场短时行为表示成统一粒度的序列，便于后续建模。

---

### Step 2. Snapshot / Timeseries 数据聚合

#### 输入
同一市场的周期性快照 / timeseries 数据。

这类数据描述的是市场状态，例如：

- midpoint
- spread
- bid depth
- ask depth
- total depth
- order-book imbalance

#### 我们做什么
我们把 snapshot 数据也聚合到和 trade 相同的时间桶中，并提取或保留如下特征：

- `midpoint`
- `spread`
- `total_depth`
- `depth_imbalance`
- `midpoint_return`

#### 为什么这样做
如果只看 trade 数据，我们只能知道市场是否“热闹”，却不知道市场是否正在“变脆弱”。

snapshot 特征可以补充说明市场在订单簿层面是否出现：

- 流动性变差
- 点差扩大
- 深度下降
- 盘口失衡

---

### Step 3. 特征融合（Feature Fusion）

#### 我们做什么
把 trade 聚合表和 snapshot 聚合表按 bucket 对齐并合并，得到一个融合后的 bucket-level dataframe。

每一行时间桶都同时包含：

- **交易活跃度特征**
- **流动性 / 价格特征**

#### 为什么这样做
一个市场压力事件可能由不同机制驱动：

- 交易量突然爆发
- 流动性突然恶化
- 价格突然偏移
- 或者多种因素共同作用

因此必须把多个维度的信号放在同一个表里统一分析。

---

### Step 4. 时间桶级别打分（Bucket-Level Stress Scoring）

这是整个检测流程的核心。

#### 4.1 局部历史基线思想

对于每个特征，我们都不是直接看“绝对值大不大”，而是把当前 bucket 和其近期历史窗口进行比较。

核心问题是：

> 当前这个时间桶，相对于它自己最近的一段市场状态，是否异常？

这样做的好处是：

- 不同市场规模不同
- 不同市场流动性不同
- 不能用统一绝对阈值强行比较

#### 4.2 特征 z-score

我们对多个特征计算 rolling 异常分数（z-style standardized score）。

##### 交易活跃度相关
- `z_trade_count`
- `z_amount_sum`
- `z_avg_trade_size`

##### 流动性相关
- `z_spread`
- `z_depth_drop`
- `z_abs_depth_imbalance`

##### 价格相关
- `z_abs_midpoint_return`

#### 4.3 组合 stress score

我们将这些维度的异常强度组合成一个统一的 **stress score**。

直观理解如下：

- 交易活跃度越异常，stress 越高
- 流动性越恶化，stress 越高
- 价格偏移越大，stress 越高

于是每个 bucket 都会得到：

- `stress_score`
- `is_stress_anomaly`

#### 4.4 异常阈值

我们并不是对所有市场使用同一个固定绝对阈值。  
我们采用的是**分位数阈值**，也就是在每个市场内部，选出 stress score 最极端的一部分时间桶作为异常桶。

这样能更好适应不同市场之间的异质性。

---

### Step 5. 事件构建（Event Construction）

#### 问题
真实的市场压力通常会持续一小段时间，而不是只出现在一个孤立时间桶里。  
如果只标记单点异常，那么结果会很碎，不利于解释。

#### 我们做什么
我们把**连续的异常 bucket** 合并成一个完整的 **stress event**。

每个 event 至少包含：

- `start_datetime`
- `end_datetime`
- `duration_minutes`
- `peak_stress_score`
- `total_amount`

#### 为什么这样做
这样可以把“点异常”提升为“事件异常”，更符合金融市场真实的短时冲击过程，也更适合后续做案例分析和可视化。

---

### Step 6. 事件补充解释（Event Enrichment）

检测出 event 之后，我们再利用其对应时间窗口内的 snapshot 信息进行补充分析。

#### 示例字段
对于每个事件，我们可以汇总：

- `max_abs_midpoint_return`
- `max_spread`
- `min_total_depth`
- `max_abs_depth_imbalance`
- `snapshot_covered`
- `num_snapshot_buckets`

#### 为什么这样做
这样我们不仅能说：

> 这里发生了异常

还能进一步说：

> 这个异常期间，spread 是否扩大了？  
> depth 是否下跌了？  
> midpoint 是否明显波动了？  
> 盘口是否出现了严重失衡？

---

## 6. 归因分析（Driver Attribution）

在事件检测完成后，我们进一步对每个事件进行归因，把其拆解为三类驱动成分。

### 6.1 Activity component
衡量事件中交易活跃度异常的强度，基于：

- trade count
- traded amount
- average trade size

### 6.2 Liquidity component
衡量事件中流动性异常的强度，基于：

- spread
- depth drop
- depth imbalance

### 6.3 Price component
衡量事件中价格偏移异常的强度，基于：

- absolute midpoint return

### 6.4 主导驱动标签（Dominant Driver）

我们给每个事件分配一个主导驱动标签：

- **activity**：交易活跃度主导
- **liquidity**：流动性恶化主导
- **price_dislocation**：价格偏移主导
- **mixed**：没有单一因素明显主导

### 为什么这样做
这样可以增强可解释性。  
我们不只是说：

> 这个事件异常

而是可以进一步说：

> 这个事件主要是交易活跃度驱动的  
> 或者  
> 这个事件主要是流动性恶化驱动的

---

## 7. 管线输出内容

对于每个市场，系统会输出：

### 时间桶级输出
- 融合后的特征表
- bucket-level score 表
- anomaly flag 表

### 事件级输出
- 合并后的 stress events
- enriched 事件总结表
- driver attribution 标签

### 批处理输出
在 batch 模式下，还会输出：

- 每个市场一行的 summary 表
- 所有市场的 stress events 总表

---

## 8. 如何理解检测结果

一个被检测到的 stress event **不等于** 证明了市场操纵。

它真正表示的是：

> 相对于该市场自身近期历史，这段时间进入了一个短时的异常压力状态。

这种状态可能来自：

- 真实信息到达
- 市场群体反应
- 大户集中交易
- 流动性撤出
- 潜在对抗性 / 操纵性行为

因此，这个系统更适合作为一个：

> **异常筛查与诊断工具**

而不是一个直接判定恶意行为的最终取证系统。

---

## 9. 为什么这种方法合理

本项目的方法对于当前数据和目标是合理的，原因如下：

### 1）适配现有数据
我们当前拥有的是 trade 数据和部分 snapshot / timeseries 数据，没有可靠人工标签，因此适合做无监督 / 经验型异常检测。

### 2）能够适应不同市场
每个市场都是相对其自身近期历史进行评分，而不是用同一个绝对阈值强行比较。

### 3）可解释性强
每个事件都可以从 activity、liquidity、price 三个角度解释。

### 4）以事件为中心
我们不是只抓孤立点，而是能得到有开始和结束时间的事件区间。

### 5）具有扩展性
后续可以继续加入：
- 更多特征
- 不同打分方式
- 新闻 / 外部标签验证
- 更复杂的异常检测方法

---

## 10. 当前范围与局限性

### 当前范围
本版本重点关注：

- YES-side market
- bucket-based empirical anomaly detection
- event-level summarization
- snapshot-based enrichment
- interpretable driver attribution

### 局限性
- 不能直接证明恶意操纵意图
- 依赖 snapshot 覆盖质量
- 当前未结合外部新闻标签做 ground-truth 对照
- 当前是经验型检测框架，不是未来价格预测模型

---

## 11. 一句话总结

本项目构建了一个可解释的经验型异常检测管线，通过融合交易活跃度、流动性恶化和短时价格偏移三个维度，来识别并解释 Polymarket 市场中的**市场压力异常事件（market stress events）**。

---

## 12. 代码结构说明（Repository Structure）

下面按照当前项目的主要代码组织方式，说明每个模块和脚本的作用，方便组员快速理解整个 pipeline 的实现逻辑。

### 12.1 整体结构概览

```text
src/
├── config.py
├── run_activity_pipeline.py
├── run_activity_pipeline_batch.py
│
├── preprocessing/
│   ├── aggregate_trades.py
│   └── aggregate_timeseries.py
│
├── features/
│   └── feature_fusion.py
│
├── detectors/
│   └── composite_anomaly.py
│
└── postprocessing/
    ├── summarize_events.py
    └── enrich_events.py
```
### 12.2 顶层脚本说明

### `src/config.py`

这个文件用于集中管理项目中的主要参数配置，例如：

- bucket 大小（如 60 秒）
- rolling window 长度
- anomaly quantile 阈值
- score method（如 additive / pca）
- 其他全局超参数

#### 作用
它的意义是把“参数”和“逻辑”分开。  
这样当我们需要调整检测窗口、阈值或评分方式时，不需要到处修改代码，只需要在配置文件中统一修改即可。

---

### `src/run_activity_pipeline.py`

这是**单市场运行脚本**。

#### 作用
它负责对**一个指定市场文件**完整执行整条 stress detection pipeline，包括：

1. 读取 trade 数据
2. 读取 timeseries / snapshot 数据
3. 做时间桶聚合
4. 做特征融合
5. 计算 bucket-level stress score
6. 标记 stress anomaly
7. 合并为 stress events
8. 用 snapshot 信息 enrich event
9. 输出单市场结果文件

#### 适合什么时候用
- 调试某一个市场
- 查看某个市场的详细结果
- 做 case study
- 检查某个异常事件是否合理

#### 输出内容
通常会输出该市场对应的：

- `bucket_features_*.csv`
- `bucket_scores_*.csv`
- `stress_events_enriched_*.csv`

---

### `src/run_activity_pipeline_batch.py`

这是**批处理运行脚本**。

#### 作用
它会对多个市场批量执行完整 pipeline，并最终输出：

- 每个市场的 summary
- 所有市场的合并 event 表

#### 它主要负责
1. 扫描 trades/ 和 timeseries/ 中可匹配的 YES-side 文件
2. 逐个市场调用单市场逻辑
3. 保存每个市场的中间输出和事件输出
4. 汇总为 batch-level summary
5. 生成 all-events 总表

#### 适合什么时候用
- 做整体实验
- 跨市场比较
- 找 top stress events
- 给报告或展示提供整体结果

#### 输出内容
通常会输出：

- `market_stress_summary_additive.csv`
- `all_stress_events_additive.csv`

---

### 12.3 预处理模块（Preprocessing）

### `src/preprocessing/aggregate_trades.py`

这个文件负责对原始逐笔 trade 数据做预处理与时间桶聚合。

#### 主要工作
- 读取原始 trade csv
- 解析时间戳
- 按 bucket（如 60 秒）聚合
- 计算基础交易特征，例如：
  - `trade_count`
  - `amount_sum`
  - `avg_trade_size`

#### 输出
返回一个 trade bucket dataframe，每一行表示一个时间桶的交易统计结果。

#### 作用总结
它把“原始逐笔交易”变成“可用于检测的短时交易特征序列”。

---

### `src/preprocessing/aggregate_timeseries.py`

这个文件负责对原始 timeseries / snapshot 数据做预处理和时间桶聚合。

#### 主要工作
- 读取 snapshot / timeseries csv
- 解析时间戳
- 对齐到 bucket
- 提取或聚合市场状态特征，例如：
  - `midpoint`
  - `spread`
  - `total_depth`
  - `depth_imbalance`

#### 输出
返回一个 snapshot bucket dataframe，每一行表示一个时间桶内的盘口状态特征。

#### 作用总结
它把“离散的市场状态快照”变成“与 trade 特征可对齐的时间桶级特征”。

---

### 12.4 特征融合模块（Features）

### `src/features/feature_fusion.py`

这个文件负责将 trade bucket 特征和 snapshot bucket 特征融合起来。

#### 主要工作
- 按 bucket 合并 trade dataframe 和 snapshot dataframe
- 处理缺失值
- 生成进一步的融合特征，例如：
  - `midpoint_return`
  - `abs_midpoint_return`
  - 其他辅助列

#### 为什么要单独做这个模块
因为 trade 数据和 snapshot 数据本来来自不同来源、不同节奏，需要统一到同一个 bucket 粒度上，才能进行联合打分。

#### 输出
返回融合后的 bucket-level dataframe，它是后续检测模块的输入。

---

### 12.5 异常检测模块（Detectors）

### `src/detectors/composite_anomaly.py`

这个文件是**异常检测核心模块**。

#### 它负责什么
对融合后的 bucket-level dataframe 计算：

- 各种 rolling z-score
- activity / liquidity / price 三个维度的异常强度
- 最终的 `stress_score`
- 异常标记 `is_stress_anomaly`

#### 它通常包含的逻辑
- rolling mean / std 或其它局部基线方法
- 对以下特征做异常标准化：
  - `trade_count`
  - `amount_sum`
  - `avg_trade_size`
  - `spread`
  - `depth_drop`
  - `abs_midpoint_return`
  - `abs_depth_imbalance`
- 组合得到：
  - `activity_component`
  - `liquidity_component`
  - `price_component`
  - `stress_score`

#### 输出
返回带有 anomaly score 和 flag 的 bucket-level dataframe。

#### 作用总结
它是整个项目最核心的“异常评分器”。

---

### 12.6 后处理模块（Postprocessing）

### `src/postprocessing/summarize_events.py`

这个文件负责把异常 bucket 合并成事件，并生成 event-level summary。

#### 主要工作
- 根据 `is_stress_anomaly` 或指定 flag，筛选异常 bucket
- 将连续异常 bucket 合并成同一个 event
- 计算 event-level 指标，例如：
  - `start_datetime`
  - `end_datetime`
  - `duration_minutes`
  - `peak_stress_score`
  - `total_amount`

#### 为什么这个模块重要
因为真实市场异常通常不是一个孤立点，而是一个持续短时间的过程。  
这个模块把点异常提升成可解释的“事件”。

---

### `src/postprocessing/enrich_events.py`

这个文件负责使用 snapshot 信息对已检测到的 event 进行补充分析。

#### 主要工作
对每个 event 对应的时间窗口，计算：

- `max_abs_midpoint_return`
- `max_spread`
- `min_total_depth`
- `max_abs_depth_imbalance`
- `snapshot_covered`
- `num_snapshot_buckets`

同时也可能会做：
- activity / liquidity / price component 的 event-level 归因
- dominant driver 标签生成

#### 作用总结
它让我们不仅知道“有异常事件”，还知道“这个事件期间盘口发生了什么”和“这个事件主要由什么驱动”。

---

### 12.7 一个市场从头到尾的数据流

下面用最简化的方式说明单个市场是如何流过整个 pipeline 的：

#### 输入
- 一个 market 的 trade csv
- 一个 market 的 timeseries csv

#### 流程
1. `aggregate_trades.py`
   - 把逐笔 trade 聚合成 trade buckets

2. `aggregate_timeseries.py`
   - 把 snapshot / timeseries 聚合成 snapshot buckets

3. `feature_fusion.py`
   - 合并 trade bucket 和 snapshot bucket
   - 构造 unified bucket-level features

4. `composite_anomaly.py`
   - 计算各种 z-score
   - 计算 stress score
   - 标记异常 bucket

5. `summarize_events.py`
   - 合并连续异常 bucket 为 stress event

6. `enrich_events.py`
   - 用 snapshot 信息补充解释 event
   - 输出 event-level enriched table

#### 最终输出
- bucket 特征表
- bucket score 表
- stress event 表

---

### 12.8 Batch 模式下的额外输出

当使用 `run_activity_pipeline_batch.py` 时，会在单市场输出之外进一步产生：

#### `market_stress_summary_*.csv`
每个市场一行，用于比较不同市场的：
- bucket 数量
- stress anomaly 数量
- stress event 数量
- snapshot coverage
- 最大事件强度
- 最大事件金额

#### `all_stress_events_*.csv`
把所有市场的 stress event 合并成一个总表，用于：
- 找出跨市场 top events
- 做最终案例展示
- 进行横向比较分析

---

### 12.9 如何理解这些模块之间的关系

从实现逻辑上说：

- `preprocessing/` 负责把原始数据整理干净
- `features/` 负责把不同来源的特征对齐和融合
- `detectors/` 负责算分和判定异常
- `postprocessing/` 负责把异常点提升成事件，并补充解释
- `run_*.py` 脚本负责把所有模块串起来，真正执行实验

也就是说：

> 模块负责“做具体功能”，  
> 顶层脚本负责“把整条流程跑起来”。

---

### 12.10 给组员的最简理解方式

如果只想最快理解整个仓库，可以这样记：

- **aggregate_trades.py**：把逐笔交易变成时间桶特征
- **aggregate_timeseries.py**：把 snapshot 变成时间桶特征
- **feature_fusion.py**：把两类特征合并
- **composite_anomaly.py**：计算 stress score 和异常标记
- **summarize_events.py**：把异常 bucket 合并成事件
- **enrich_events.py**：给事件补充盘口解释和归因
- **run_activity_pipeline.py**：跑单个市场
- **run_activity_pipeline_batch.py**：批量跑多个市场
- **config.py**：统一管理参数

---

## 13. 如何运行项目（How to Run）

下面给出最常用的运行方式，方便组员快速复现实验。

### 13.1 环境准备

建议使用 Python 3.10+，并在虚拟环境中安装依赖。

示例：

```bash
python -m venv .venv