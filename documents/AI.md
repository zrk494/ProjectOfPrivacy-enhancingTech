# AI-Driven SDD Development Standard Operating Procedure (SOP)

This document defines the AI collaboration standards for this project. We will adopt the **SDD (Specification-Driven Development)** model, combined with an external file memory system and specific Agent skill libraries, to completely eliminate "hallucinations, goal drift, and infinite loops" in AI programming.

## 1. Toolchain and Architecture Selection (Toolchain)

Our AI collaboration stack consists of the following tools:

- **Main Brain Engine: OpenCode + DeepSeek API**
  - **Positioning**: Responsible for high-intelligence architecture deduction, requirement brainstorming, task breakdown, and root cause analysis of complex bugs.
  - **Advantages**: DeepSeek API's powerful logical capabilities combined with OpenCode's native Skill system.
- **Execution Engine: TRAE (SOLO Mode)**
  - **Positioning**: Responsible for step-by-step execution of `task_plan.md`, automated file modifications, terminal command execution, and code building.
  - **Advantages**: Strong fully automatic context execution and workspace operation capabilities.

***

## 2. Core System Mechanisms (Core Mechanisms)

### 2.1 External Memory System (Planning-with-files)

To prevent AI context overload and forgetting, we strictly prohibit lengthy discussions in the dialog box. All states must be persisted as the following three "living documents":

1. `findings.md` (Knowledge Base): Stores brainstorming conclusions, research results, API structures (such as `anomaly_interface_spec.md`). **(Strict Rule: Must be persisted after 2 consecutive queries)**
2. `task_plan.md` (Register): Only stores Todo Checkboxes `-[ ]` for the current phase. Tasks must be small and verifiable.
3. `progress.md` (Error Notebook): Stores test failure logs, error messages, and repair attempts.

### 2.2 Agent Skills Matrix

AI must call appropriate skills based on the scenario, strictly prohibiting "programming by feeling":

- **Superpowers Core Skills**: `brainstorming` (divergent requirements), `writing-plans` (task breakdown), `systematic-debugging` (standardized troubleshooting).
- **Anti-Loop Skill**: `pua` (<https://github.com/tanweai/pua>) When AI falls into an ineffective cycle of "sorry I'm wrong, I'll fix it immediately", use this skill to force AI to stop writing code and conduct deep reflection.

***

## 3. Standard Development Flow (The SDD Workflow)

The development of each new feature must strictly follow the following 5 phases:

### Phase One: Requirement Clarification and Exploration (Brainstorming)

- **Tools Used**: OpenCode + DeepSeek
- **Operation Method**:

  Enter in OpenCode: `"Use superpowers/brainstorming skill to help me plan the development of [new feature name]."`
- **Execution Discipline**:
  - Must establish Goals and Non-Goals.
  - Technical decisions and data interfaces discussed must be mandatorily written into `findings.md` by AI.

### Phase Two: Contract Signing (Writing Specification)

- **Tools Used**: OpenCode + DeepSeek
- **Operation Method**:

  After brainstorming, ask AI to summarize and output `spec.md`.
- **Execution Discipline**:
  - `spec.md` should not exceed one page.
  - Must include Acceptance Criteria, which must be testable assertions (Given/When/Then format).

### Phase Three: Task Breakdown (Task Planning)

- **Tools Used**: OpenCode + DeepSeek
- **Operation Method**:

  Enter: `"Use superpowers/writing-plans skill, read spec.md and findings.md, and generate a list of 10-30 extremely granular tasks in task_plan.md."`
- **Execution Discipline**:
  - Each task must be an atomic code commit.
  - Task descriptions must include verification methods (such as "run pytest test_api.py").

### Phase Four: Autonomous Execution (Autonomous Execution)

- **Tools Used**: TRAE (SOLO Mode)
- **Operation Method**:

  Start SOLO mode in TRAE and issue the启动指令:
  > "Please read the next uncompleted task in `task_plan.md`. Strictly refer to the design specifications in `findings.md`. Execute the task, run the tests, record the execution results in `progress.md`, and finally check the task off in `task_plan.md`."
- **Execution Discipline**:
  - Follow TDD principles: write tests first, verify failure, then write implementation, verify success.

### Phase Five: Exception Breaking (Troubleshooting & Anti-Loop)

During SOLO execution, if AI encounters an error and fails to fix it after 2-3 consecutive attempts (starts guessing, reverts to original error code, apologizes repeatedly):

- **Tools Used**: Either OpenCode or TRAE
- **Operation Method**:

  Immediately stop AI execution and call the `pua` skill:
  > "Load and execute pua skill. Carefully read the failed attempts recorded in `progress.md`. Stop apologizing and stop generating any code! Use first principles to analyze why previous attempts failed, provide 3 root cause hypotheses, and do not touch code until you can prove your hypotheses."
- **Execution Discipline**:
  - The purpose of the `pua` skill is to break the large model's inherent tendency to "flatter and rush to provide answers".
  - Force AI to enter the role of a "cold auditor", locate the problem, then update `task_plan.md` for precise fixes.

***

## 4. Phase Transition and Memory Pruning

To ensure that OpenCode (DeepSeek) and TRAE do not become less intelligent in long-term projects, regular memory pruning must be performed:

1. **Single Subtask Completion**: Clear chat window context and restart the conversation relying only on `*.md` files on disk.
2. **Major Milestone Completion (Epic Done)**:
   - Transfer solidified architectural knowledge from `findings.md` to formal project documentation (such as `architecture.md`).
   - Move `task_plan.md` and `progress.md` to `docs/archive/` for archiving and backup.
   - Create new, blank three files to prepare for the next SDD cycle.
