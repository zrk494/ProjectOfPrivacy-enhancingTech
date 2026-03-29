# &#x20;AI 驱动的 SDD 开发标准操作程序 (SOP)

本文档定义了本项目的 AI 协作标准。我们将采用 **SDD (Specification-Driven Development，规范驱动开发)** 模式，结合外部文件记忆系统和特定的 Agent 技能库，以彻底消除 AI 编程中的“幻觉、目标漂移和死循环”。

## 1. 工具链与架构选型 (Toolchain)

我们的 AI 协作栈由以下工具组成：

- **主脑引擎：OpenCode + DeepSeek API**
  - **定位**：负责高智商的架构推演、需求头脑风暴、任务拆解以及复杂 Bug 的根因分析。
  - **优势**：DeepSeek API 的强大逻辑能力配合 OpenCode 的原生 Skill 系统。
- **执行引擎：TRAE (SOLO 模式)**
  - **定位**：负责按部就班地执行 `task_plan.md`，进行自动化的文件修改、终端命令运行和代码构建。
  - **优势**：极强的全自动上下文执行和工作区操作能力。

***

## 2. 核心系统机制 (Core Mechanisms)

### 2.1 外部记忆系统 (Planning-with-files)

为了防止 AI 的上下文超载和遗忘，我们严禁在对话框中长篇大论。所有状态必须落盘为以下三个“活文档”：

1. `findings.md`（知识库）：存放头脑风暴结论、调研结果、API 结构（如 `anomaly_interface_spec.md`）。**（严格遵守：连续 2 次查询后必须落盘）**
2. `task_plan.md`（寄存器）：只存放当前阶段的 Todo Checkbox `-[ ]`。任务必须微小且可验证。
3. `progress.md`（错题本）：存放测试失败日志、报错信息和修复尝试。

### 2.2 Agent Skills 矩阵

AI 必须根据场景调用合适的技能（Skill），严禁“凭感觉编程”：

- **Superpowers 核心技能**：`brainstorming` (发散需求), `writing-plans` (拆解任务), `systematic-debugging` (规范化排错)。
- **防死循环技能**：`pua` (<https://github.com/tanweai/pua>)  当 AI 陷入“抱歉我错了马上改”的无效循环时，使用此技能强制 AI 停止写代码并进行深度反思。

***

## 3. 标准开发流 (The SDD Workflow)

每一个新功能（Feature）的开发，都必须严格遵守以下 5 个阶段：

### 阶段一：需求澄清与探索 (Brainstorming)

- **使用工具**：OpenCode + DeepSeek
- **操作方法**：

  在 OpenCode 中输入：`"使用 superpowers/brainstorming 技能，帮我规划 [新功能名称] 的开发。"`
- **执行纪律**：
  - 必须确立 Goal（目标）和 Non-Goals（非目标）。
  - 讨论得出的技术决策和数据接口，必须强制要求 AI 写入 `findings.md` 中。

### 阶段二：签订契约 (Writing Specification)

- **使用工具**：OpenCode + DeepSeek
- **操作方法**：

  头脑风暴结束后，让 AI 总结并输出 `spec.md`。
- **执行纪律**：
  - `spec.md` 不超过一页。
  - 必须包含验收标准（Acceptance Criteria），且必须是可测试的断言（Given/When/Then 格式）。

### 阶段三：任务拆解 (Task Planning)

- **使用工具**：OpenCode + DeepSeek
- **操作方法**：

  输入：`"使用 superpowers/writing-plans 技能，读取 spec.md 和 findings.md，在 task_plan.md 中生成 10-30 个粒度极小的任务清单。"`
- **执行纪律**：
  - 每个任务必须是一个原子的代码提交。
  - 任务说明中必须包含验证方法（如“运行 pytest test\_api.py”）。

### 阶段四：自治执行 (Autonomous Execution)

- **使用工具**：TRAE (SOLO 模式)
- **操作方法**：

  在 TRAE 中开启 SOLO 模式，抛出启动指令：
  > "请读取 `task_plan.md` 中下一个未完成的任务。严格参考 `findings.md` 中的设计规范。执行任务，跑通测试后，在 `progress.md` 中记录执行结果，最后在 `task_plan.md` 中打勾。"
- **执行纪律**：
  - 遵循 TDD 原则：先写测试，验证失败，再写实现，验证通过。

### 阶段五：异常破局 (Troubleshooting & Anti-Loop)

在 SOLO 执行过程中，如果 AI 遇到报错，并且连续 2-3 次尝试修复依然失败（开始瞎猜、改回原本的错误代码、疯狂道歉）：

- **使用工具**：OpenCode / TRAE 均可
- **操作方法**：

  立刻中止 AI 的执行，调用 `pua` 技能：
  > "加载并执行 pua skill。仔细阅读 `progress.md` 中记录的这几次失败尝试。收起你的道歉，停止生成任何代码！使用第一性原理分析为什么之前的尝试都失败了，给出 3 个根本原因推测，并在证明你的推测前不准动代码。"
- **执行纪律**：
  - `pua` 技能的作用是打破大模型固有的“谄媚和急于给出答案”的倾向。
  - 强迫 AI 进入“冷酷的审计员”角色，定位问题后再更新 `task_plan.md` 进行精准修复。

***

## 4. 阶段转换与记忆清理 (Memory Pruning)

为了保证 OpenCode (DeepSeek) 和 TRAE 在长期项目中不变笨，必须执行定期的记忆清理：

1. **单个子任务完成**：清空聊天窗口上下文，只依赖硬盘上的 `*.md` 文件重新开启对话。
2. **大型里程碑完成（Epic Done）**：
   - 将 `findings.md` 中固化的架构知识转移到正式项目文档（如 `architecture.md`）。
   - 将 `task_plan.md` 和 `progress.md` 移动到 `docs/archive/` 进行归档备份。
   - 创建全新的、空白的三文件，迎接下一轮 SDD 循环。

