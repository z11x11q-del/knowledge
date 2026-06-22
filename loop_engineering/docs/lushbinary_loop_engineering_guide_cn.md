# 循环工程：设计提示 AI Agent 的系统

> 原文链接：<https://lushbinary.com/blog/loop-engineering-ai-coding-agents-guide/?utm_source=chatgpt.com>
> 中文翻译：基于 2026-06-16 抓取的英文版本
> 英文原文档：[lushbinary_loop_engineering_guide.md](./lushbinary_loop_engineering_guide.md)
> 注意：英文原文在抓取时部分章节被截断，中文版对应处保留要点摘要。

---

## 摘要

循环工程是 **不再亲手给 AI Agent 发提示词，转而设计替你发提示词的系统**。本文将介绍这个术语的含义、Agent 循环的五大构件（外加记忆）、Claude Code 与 OpenAI Codex 在每个构件上的实现方式、一个真实可运行的端到端循环，以及循环越完善反而越尖锐的风险。

---

## 目录

1. 循环工程的真正含义
2. 从提示词工程到循环工程
3. Ralph 技巧：循环的起点
4. 五大构件（外加记忆）
5. Automations：循环的心跳
6. Worktrees：并行 Agent 不撞车
7. 技能与记忆：不再每次重述项目
8. 子 Agent：把作者与审阅者分开
9. 一个端到端循环长什么样
10. 循环工程没能消除的风险
11. 为什么选 Lushbinary 做 Agent 工程
12. FAQ

---

## 1. 循环工程的真正含义

循环工程是 **取代你自己作为提示 Agent 的人的角色，转而设计替你做这件事的系统**。这里的循环是一个递归的目标：你定义一次意图，Agent 就会不断迭代直到工作真正完成。

不再是"你每轮回复后再敲下下一条指令"，而是一个小系统：

- 发现工作
- 分派任务
- 检查结果
- 记下完成项
- 决定下一步做什么

你让这个系统 **去戳 Agent**，而不是你自己去戳它。

### 关键心智模型

编码 Agent 在每一轮内部已经在跑一个 **内循环**：

> **推理 → 行动 → 观察 → 再回到推理**

这条"感知-推理-行动-观察"链条就是 **Agentic Loop**。循环工程位于其上层：你构建一个 **外循环**，按计划运行、派生子任务、自喂任务，在许多内循环之间持续运转，而你不必每一轮都坐在椅子上。

### 一句话定义

> **循环工程就是按计划、围绕目标构建一个替你给 Agent 发提示词的系统，而不是自己敲下每条提示词。** 杠杆点从单条提示词的质量，迁移到了生成并校验提示词的系统的设计质量。

### 产品化拐点

让早期采用者惊讶的是，**这不再是一项需要自研的工作**。一年前，"循环"意味着你要维护一堆只有自己看得懂的 bash 脚本。到了 2026 年中，这些构件直接内置在你正在使用的产品里。Peter Steinberger 列出的循环必备清单几乎与 OpenAI Codex App 完全对应，又与 Anthropic Claude Code 几乎对应。

---

## 2. 从提示词工程到循环工程

| 层级 | 优化的对象 | 工作单元 |
| :-- | :-- | :-- |
| 提示词工程 | 你如何表述一条指令 | 你亲手敲下的一轮 |
| 上下文工程 | 窗口里还要塞进什么：文档、历史、工具定义 | 一次回答的外部条件 |
| 循环工程 | 决定何时提示、提示什么、结果是否可接受的系统 | 跨多轮的自运行周期 |

> ⚠️ **杠杆点迁移了，但工作并没有变简单。**
> Boris Cherny 想表达的不是"写代码变简单了"，而是 **最高价值的事情从写提示词迁移到了设计循环**。设计良好的循环能放大一名优秀工程师；设计糟糕的循环会以同样快的速度放大糟糕的决策，并且你盯得还更少。

提示词工程不会消失——循环本身就由提示词组成；上下文工程也不会消失——循环依然需要把合适的文件、历史和工具定义塞到每一轮的窗口里。**循环工程所做的，是在这一切之外再加上自主控制结构。**

---

## 3. Ralph 技巧：循环的起点

在"循环工程"这个词被提出之前，已经有了 **Ralph**。2026 年初，Geoffrey Huntley 描述了一种用朴素的 `while` 循环驱动编码 Agent 的方法：

- 把同一条提示词配着书面 spec 喂给 Agent
- 让它挑一个任务并实现
- 起一个新的实例，再次喂入完全相同的提示词
- 重复直到工作完成

他用《辛普森一家》里的 Ralph Wiggum 来命名这项技巧，因为用他自己的话说，它在不可预测的世界里 **"决定性地简单"**。

### 非显而易见的洞见：上下文重置

长会话的 Agent 会随着窗口被旧推理、死胡同、陈旧文件内容填满而退化。Ralph 完全绕开了这一点：

> 每次迭代都是一个全新的 Agent，拥有干净的上下文，从磁盘上读取仓库当前状态与任务列表，做正好一个单位的任务，提交，然后退出。

智能并不存在于某次英雄式运行里。**它存在于清晰、细粒度的规约与可验证的结果中，反复地、以模型无法污染的外部记忆为参照地施加。**

### Ralph 循环：一次任务，一份全新上下文

```
while ! done:
    run agent:
        读取 spec + 状态
        做一个任务
        测试并提交
    重置上下文
```

任务列表存在磁盘上，是唯一能在重置中幸存的记忆。

### 原始 Ralph 实现

```bash
# 原始 Ralph 循环：同一条提示词、全新上下文，直到完成
while ! grep -q "ALL TASKS DONE" STATUS.md; do
  # 每一次都是上下文窗口为空的全新 Agent
  claude -p "Read PLAN.md and STATUS.md. Pick the next unchecked
task, implement it, run the tests, commit on success,
and update STATUS.md. Then stop." \
  --dangerously-skip-permissions
done

# PLAN.md 与 STATUS.md 是持久化记忆。Agent 在每轮之间忘记一切，
# 文件却记得哪些已经完成。
```

> 💡 **循环工程就是产品化的 Ralph。**
> Ralph 证明了你不需要聪明的 harness，只需要持久性、外部状态文件与可验证的停止条件。循环工程就是这些思想被搬进工具之后的样子：`while` 变成定时自动化，上下文重置变成 worktree + 子 Agent，`"ALL TASKS DONE"` 的判断变成由独立模型打分的 `/goal` 条件。同样的形状，只是少了几个扎手的角。

---

## 4. 五大构件（外加记忆）

一个能跑起来的循环需要 **五样东西**，再加一个地方来记住状态：

1. **Automations** —— 按计划触发，自主完成发现与分诊。
2. **Worktrees** —— 并行 Agent 互不踩对方的文件。
3. **Skills** —— 把 Agent 每轮都要现想一遍的项目知识写下来。
4. **插件与连接器** —— 把 Agent 接到你已有的工具上。
5. **子 Agent** —— 一个负责提出想法，另一个负责检查。

第六个要素是 **记忆**：一个 Markdown 文件、一个 Linear 或 GitHub 看板，任何处在单次会话之外、记录着"已完成"和"接下来"的东西。

> 模型在每次运行之间都会遗忘，所以状态必须存在于磁盘，而不是上下文窗口。**Agent 会遗忘。仓库不会。**

### 一个 Agent 循环的解剖图

```
按计划触发的 Automation
        ↓
发现并分诊工作
        ↓
子 Agent 起草改动
        ↓
校验子 Agent 检查结果
        ↓
连接器开 PR 与工单
        ↓
进入下一轮
（磁盘上的记忆持久化状态）
```

---

## 5. Automations：循环的心跳

Automations 才是让循环真正成为"循环"而不是"只跑过一次的运行"的原因。**它们是心跳**：一个不需要你开口就能浮现工作的循环触发器。循环中的其它一切都在响应 Automation 的发现。

### OpenAI Codex 中的实现
- **Automations 标签页**：选择项目、提示词、节奏、跑在本地 checkout 还是后台 worktree。
- 有发现的运行进入 **Triage 收件箱**；没发现的运行自我归档。
- Automation 可以 **调用 skill**，让循环指令可维护：你触发的是一个命名 skill，而不是往一份永远没人更新的调度里塞一大段说明。

### Claude Code 中的实现
- `/loop` 按节奏调度一条循环提示词（会把节奏转成 cron 任务）。
- **Hooks** 在 Agent 生命周期的特定节点执行 shell 命令。
- 把整个东西推到 **GitHub Actions**，让你关上笔记本后它仍然运行。
- `/goal` 会跨多轮工作，直到你写的条件可验证地为真——每轮之后由一个独立的、较小的模型判断是否完成（**写代码的不是打分的那个**）。

```bash
# Claude Code：每个工作日早上 9 点跑一次分诊提示词
/loop "Read yesterday's CI failures and open issues, write findings
 to TODO.md, and draft fixes for anything labeled quick-win"
 --schedule "0 9 * * 1-5"

# Claude Code：跑，直到一个可验证的停止条件成立
/goal "All tests in test/auth pass and lint is clean"

# OpenAI Codex：持续运行的长时目标（CLI 0.128.0+）
codex /goal "Migrate the billing module to the new pricing API,
 keep all existing tests green"
```

> ⚠️ **盯紧 token 账单。**
> 一个每轮都让校验模型跑一遍的定时循环，token 消耗非常快。开局用慢节奏、紧的目标条件，花几天观察成本，等循环确实在产出你愿意合并的工作之后，再加大力度。

### 把停止条件写成契约，而不是愿望

一个目标的好坏，完全取决于证明它的证据。

| 契约字段 | 弱版本 | 可验证版本 |
| :-- | :-- | :-- |
| 终态 | "提升测试覆盖率" | "`src/billing` 覆盖率 ≥ 90%" |
| 证据 | "看起来做完了" | "`npm test` 退出码为 0，覆盖率报告印证数字" |
| 约束 | （未声明） | "不动公开 API，不删既有测试" |
| 预算 | （无界） | "超过 25 轮或 $5 即停止，取先到者" |

> 💡 **让循环值得信赖的三件事。**
> Claude Code 团队把可靠的循环归结为三条习惯：**保留错误**，让循环能从中学习而不是重蹈覆辙；**把验证内嵌到循环里**，而不是事后打补丁；**把失败的测试或红色的 CI 当作信号**，让 Agent 保持诚实。

---

## 6. Worktrees：并行 Agent 不撞车

一旦运行不止一个 Agent，文件就会开始打架。**Git worktree** 就是修这个问题的——一个独立的 working directory、独占分支，却共享同一份仓库历史。

> 原文此节在抓取时被截断。其它相关说明可参考本文档与本目录下其他 Loop Engineering 文档。

---

## 7. 技能与记忆：不再每次重述项目

- **Skills** 是把项目知识写下来，让 Agent 不用每轮都从零推导意图。
- 形式：通常为 `SKILL.md`，包含指令与元数据，Claude Code 与 Codex 都采用此结构。
- **记忆** 存在于会话之外——Markdown 文件、Linear 看板、GitHub Issues 等。

> 模型在每次运行之间遗忘；仓库不会。

---

## 8. 子 Agent：把作者与审阅者分开

最有用的结构性做法：**写的人与查的人分开**。写出代码的模型在批改自己的作业时手太软。

---

## 9. 一个端到端循环长什么样

英文原文此节描述了一个完整的循环，常见结构为：

1. 每天早上由 Automation 运行分诊 skill，读取昨日 CI 失败、开放 issue、最近提交，把发现写到 Markdown 文件或 Linear 看板。
2. 针对每个值得处理的发现，线程在隔离的 worktree 里派出一个子 Agent 起草修复方案，再派第二个子 Agent 按项目 skills 与既有测试审阅草稿。
3. 连接器负责开 PR、更新工单。循环处理不了的落到分诊收件箱。状态文件记录哪些试过、哪些通过、哪些还开着。
4. 你只是预先设计了一次。

> 你没有亲手为这些步骤写过任何一条提示词。这正是 Steinberger 那句话的真实落地。

---

## 10. 循环工程没能消除的风险

- **验证仍然落在你头上** —— 一个无人值守的循环就是一个无人值守地制造错误的循环。
- **你的理解仍然在腐烂** —— 循环越快地产出你没写过的代码，存在与理解之间的鸿沟就越大。**读一读循环写出的东西。**
- **认知投降是真实的** —— 当循环自己跑起来，停止持有观点很容易。**带着判断力设计循环是解药，逃避思考地设计循环是催化剂。**

---

## 12. FAQ

### 什么是循环工程？
设计自动提示编程 Agent 的系统来代替手动提示词。循环负责发现工作、分派任务、校验输出、追踪完成项——整个过程不需要你盯着。

### 循环的五大构件是什么？
Automations、Worktrees、Skills、Plugins/Connectors、Sub-Agents，外加第六项：**状态/记忆**，存放在会话之外。

### 它与提示词工程的区别？
提示词工程关心如何写好一条提示词；循环工程关心如何设计一个你根本不再写单条提示词的、由系统代劳的循环。

### 哪些工具支持循环工程？
OpenAI Codex 与 Claude Code 都内置了五大构件。命令名略有差异，但能力对等。在一方设计的循环，能在另一方几乎无缝地跑起来。

### 我还需要 review 代码吗？
需要。**验证是循环中最重要的人类角色**。

---

## 相关链接

- [Vibe Coding 开发指南（Lushbinary）](https://lushbinary.com/blog/vibe-coding-developer-guide-ai-first-development/)
- [Claude Code Agent 团队多 Agent 开发指南（Lushbinary）](https://lushbinary.com/blog/claude-code-agent-teams-multi-agent-development-guide/)
- [2026 AI 编程 Agent 对比（Lushbinary）](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- [OpenAI Codex 子 Agent 自治团队指南（Lushbinary）](https://lushbinary.com/blog/openai-codex-subagents-autonomous-coding-teams-guide/)
