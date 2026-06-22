# AI 编程 Agent 的循环工程（Loop Engineering）

> 原文链接：<https://www.kyenai.com/guides/loop-engineering-ai-coding-agents?utm_source=chatgpt.com>
> 中文翻译：基于 2026-06-16 抓取的英文版本
> 英文原文档：[kyenai_loop_engineering_guide.md](./kyenai_loop_engineering_guide.md)

---

## 摘要

**循环工程（Loop Engineering）** 是为 AI 编程系统设计 **执行（act）→ 观察（observe）→ 推理（reason）** 循环的实践，使其在目标达成或停止规则触发前不断重复。不同于单次提示词或固定的 cron 脚本，循环内的 Agent 会根据测试输出、日志、diff 或工具结果自主决定下一步。

你的工作重心从 **为每条提示词费心**，转向 **定义目标、验证命令、迭代上限、升级路径与成本边界**。

---

## 一、循环工程模式矩阵

> 数据来源：截至 2026-06-15 的从业者与厂商实践整理。

| 模式 | 适用场景 | 停止条件 | 工具示例 | 需控制的风险 |
| :-- | :-- | :-- | :-- | :-- |
| **计划 → 执行 → 验证** | 边界清晰的仓库任务，配有明确成功命令（测试、类型检查、构建） | 验证通过或达到迭代上限 | Claude Code agent 会话、Cursor Agent 模式、Codex + AGENTS.md 验证规则 | 无限重试导致文件被反复搅动、却未读取失败输出 |
| **带上限的重试** | 易抖动的命令、迁移步骤或初始化任务（多试一次常常成功） | 每个任务硬性尝试上限，超限升级到人工 | Claude Code `/loop` 定时、Cursor Automations + 明确 max-run 注释 | 在同一错误假设上反复烧 token，却不切换策略 |
| **评估器 → 优化器** | 质量标准清晰的工作：评审、文档、测试计划、重构方案 | 评估器通过或改进停滞 | Claude Code 子 Agent（作者 + 检查者）、Codex `.codex/agents/` 中的子 Agent | 两个 Agent 达成"漂亮但错误"的共识，缺少真实校验 |
| **探索 → 收敛 → 实现** | 不熟悉的代码库、事故排查或首文件猜测常错的场景 | 目标文件和改动范围确定后，切入受限编辑 | 只读子 Agent、Ask 模式、Scoped 分支上的 Agent 模式 | 探索无限延长、不切换到有边界的实现循环 |
| **定时唤醒循环** | 周期性巡检：依赖预警、夜间测试分诊、变更日志扫描、待办清理 | 每次运行以摘要、工单或空操作结束；定时本身不等于循环内无限重试 | Claude Code `/loop` 与 cron、Cursor Automations、GitHub Actions agent 任务 | 把 cron 任务当成循环，缺少循环内观察与停止规则 |
| **人机协同检查点** | 生产变更、权限扩张、Schema 迁移或破坏性操作 | 暂停直到指定人员批准、拒绝或收窄范围 | 部署前 Hook、MCP 审批门、云端 Agent 强制走 PR | 因循环"差一点完成"而跳过检查点 |

---

## 二、循环的五大构件

每一个可持续运行的编程 Agent 循环，在扩展并行度或定时之前都需要这些控制。

### 1. 清晰的目标与完成信号
明确"完成"的含义：命令通过、PR 已合并、工单已建、报告已交付。

### 2. 可观察的工具
把测试、Linter、日志、diff 或 MCP 访问给到 Agent，使每个周期都能产出证据。

### 3. 上下文预算
按需加载仓库说明、技能与限定范围内的文件，迭代间及时裁剪。

### 4. 终止与升级
限制迭代次数、明确升级路径，并在同一错误反复出现时立即停止。

### 5. 成本与并发上限
为 token、并行 Agent 与运行时设置预算，防止循环在夜间无限运行。

---

## 三、循环工程不是提示词工程的放大版

提示词工程优化的是 **单次交互**；循环工程则是把单次交互转成 **更大系统中的一个组件**——该系统具备记忆、工具与终止逻辑。

cron 任务只是按计划运行同一脚本；**循环则让一个 Agent 检查当前状态、选择下一步、观察结果，并自行决定继续、重试、回滚还是停止**。

> 2026 年中的从业者一语中的：别再亲自盯 Agent 发提示词了，转而设计能给 Agent 发提示词的系统。这并没有消除工程判断——它把判断转移到了循环设计：什么算成功、什么算有效证据、何时需要人工介入。

---

## 四、循环在当下工具中的落点

- **Claude Code**：通过 `/loop` 定时、生命周期 Hook、按"探索-实现-验证"拆分的子 Agent，以及在关闭笔记本后仍能持续运行的无头/CI 模式来支撑循环。
- **Cursor**：支持长生命周期的云端 Agent、隔离分支上的并行 Agent，以及由 GitHub、Slack、Linear 或定时触发的 Automations。
- **Codex** 与类似 Agent：通过工具调用、子 Agent 与声明验证命令的仓库说明实现循环。

不同厂商的界面各异，但架构骨架重复出现：**目标、上下文、工具、观察、调整、终止**。

---

## 五、Prompt vs Loop 决策表

借助此表判断任务到底该用一次性会话还是持续运行的循环。

| 维度 | 适合单次 Prompt | 适合设计循环 | 需要补充的停止规则 |
| :-- | :-- | :-- | :-- |
| **任务形态** | 步骤可预测，能在一次专注会话中完成 | Agent 必须读错误、改动并重新验证 | 给出验证命令与最大迭代次数 |
| **时长** | 你能整段时间守在键盘前 | 任务需要在你处理其他事项或关闭笔记本时继续 | 设置定时或队列，每次运行产出摘要工件 |
| **风险** | 改动可逆且局限于本地分支 | 循环会触及共享文件、CI、生产配置或权限 | 在合并或部署前要求人工检查点 |
| **成本** | 单次会话内 token 用量小且可见 | 重试、并行 Agent 或长时域可能让成本指数增长 | 设置每次/每天预算并自动停止 |
| **团队协作** | 单一工程师需要快速答复或小补丁 | 团队希望跨仓库执行可重复的分诊、评审或巡检 | 在不含敏感信息的运行日志上指派循环漂移的负责人 |

---

## 六、执行步骤

1. **命名目标与完成信号** —— 用可观察的术语描述"完成"：命令输出、PR 状态、工单链接或报告段落。避免"做得更好一点"这种模糊目标。

2. **选择第一个模式** —— 代码变更默认 **计划-执行-验证**。仅在评审标准明确时引入评估器-优化器。单一任务循环稳定后再使用定时唤醒循环做周期性分诊。

3. **先接通观察再追求速度** —— 给 Agent 配齐测试、Linter、构建命令、diff 审阅或返回真实世界结果的 MCP 工具。没有观察的循环只是昂贵的重复。

4. **设置终止与升级** —— 限制每个文件/任务的尝试次数；同一错误反复出现时立即停止；明确谁能批准生产或权限变更。文档化循环受阻时的应对策略。

5. **先试点、衡量再并行** —— 在一个仓库任务上运行循环，记录审阅时间、token 用量与实际发生的人工介入。只有在单线程循环可信之后，再加入并行 Agent 或云端接力。

---

## 七、常见陷阱

- **目标模糊且没有完成信号** —— 在首次无人值守运行前，把目标翻译为验证命令、必需工件或明确的人工验收步骤。
- **在同一错误上无限重试** —— 限制每个任务的迭代次数，并在反复失败后切换策略，而不是继续支付相同尝试。
- **没有 Agent 决策者的 cron** —— 确保每次运行都观察当前状态并选择下一步动作；定时器上跑固定脚本是 **调度**，不是循环工程。
- **并行 Agent 写同一批文件** —— 隔离分支或划分互不重叠的所有权；让 Agent 合并结果，而不是互相覆盖。

---

## 八、实施清单

- 用可观察的术语描述目标与完成信号。
- 把"计划-执行-验证"作为默认循环模式。
- 用测试、Linter 或构建作为循环观察的锚点。
- 限制迭代次数，明确重复失败的升级路径。
- 在生产或破坏性操作前加入人工检查点。
- 在无人值守运行前为 token 与并行 Agent 设置预算。
- 日志记录运行结果（去除敏感信息），并指定循环负责人。

---

## 九、FAQ

### 第一步该做什么？
从一个真实的仓库任务和一条"计划-执行-验证"循环开始，再考虑加入定时或并行 Agent。

### 这份指南面向谁？
正在 Cursor、Claude Code、Codex 或自研 CI Agent 中采用 Agentic 编码工作流的开发者、Staff 工程师与平台团队。

### 这份指南的证据基础？
基于 Addy Osmani、Anthropic、Kilo 的可引用来源。源链接与范围说明见原页面。

---

## 十、参考资料

- [Addy Osmani — Loop Engineering](https://addyosmani.com/blog/loop-engineering/)
- [Anthropic — Building effective AI agents](https://www.anthropic.com/research/building-effective-agents)
- [Kilo — What is loop engineering?](https://kilo.ai/articles/what-is-loop-engineering)
- [Anthropic — Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview)

---

## 十一、相关指南

- [Claude Code 子 Agent 工作流示例](https://www.kyenai.com/guides/claude-code-subagents-examples)
- [Claude Code Hooks 与 MCP 配置](https://www.kyenai.com/guides/claude-code-hooks-mcp-setup)
- [IDE 中 Agent 模式 vs Chat 模式](https://www.kyenai.com/guides/agent-mode-vs-chat-mode-in-ide)
- [本地 vs 云端 AI 编程 Agent](https://www.kyenai.com/guides/local-vs-cloud-ai-coding-agent)
- [Agent 治理检查清单](https://www.kyenai.com/guides/agent-governance-checklist-for-software-teams)
