# Loop Engineering: Designing Systems That Prompt AI Agents

> 原文链接：<https://lushbinary.com/blog/loop-engineering-ai-coding-agents-guide/?utm_source=chatgpt.com>
>
> 作者：Lushbinary Team
> 发布日期：2026-06-09
> 阅读时长：16 min read
> 提取时间：2026-06-16

---

## 摘要

Loop engineering is the shift from prompting AI agents by hand to designing the systems that prompt them. This guide covers what the term means, the five building blocks (plus memory) of an agent loop, how Claude Code and OpenAI Codex implement each piece, a realistic end-to-end loop, and the risks that get sharper as the loop improves.

---

## 目录

1. What Loop Engineering Actually Means
2. From Prompt Engineering to Loop Engineering
3. The Ralph Technique: Where the Loop Started
4. The Five Building Blocks (Plus Memory)
5. Automations: The Heartbeat of a Loop
6. Worktrees: Parallel Agents Without Collisions
7. Skills & Memory: Stop Re-Explaining Your Project
8. Sub-Agents: Separate the Maker From the Checker
9. What One Loop Looks Like, End to End
10. The Risks Loop Engineering Does Not Solve
11. Why Lushbinary for Agentic Engineering
12. FAQ

---

## 1. What Loop Engineering Actually Means

Loop engineering is **replacing yourself as the person who prompts the agent, and designing the system that does it instead**. A loop here is a recursive goal: you define a purpose once, and the agent iterates until the work is actually complete.

Instead of you typing the next instruction after every response, a small system:
- finds the work
- hands it out
- checks the result
- writes down what is done
- decides the next thing to do

You let that system **poke the agent instead of poking it yourself**.

### 关键心智模型

A coding agent already runs an **inner loop** on every turn:

> **reason → take action → observe → loop back**

That perceive/reason/act/observe cycle is the **agentic loop**. Loop engineering sits one floor above it: you build an **outer loop** that runs on a schedule, spawns helpers, feeds itself work, and keeps going across many of those inner cycles without you in the seat for each one.

### 一句话定义

> **Loop engineering is building a system that prompts your agent on a schedule and against a goal, instead of typing each prompt yourself.** The leverage moves from the quality of a single prompt to the design of the system that generates and verifies prompts.

### 产品化拐点

What surprised early adopters is that **this is no longer a build-it-yourself effort**. A year ago, a loop meant a pile of bash scripts you maintained forever. As of mid 2026, the pieces ship inside the products. Peter Steinberger's checklist of what a loop needs maps almost exactly onto the OpenAI Codex app, and nearly the same list onto Anthropic's Claude Code.

---

## 2. From Prompt Engineering to Loop Engineering

| Layer | What you optimize | Unit of work |
| :-- | :-- | :-- |
| Prompt engineering | How you phrase a single instruction | One turn you type by hand |
| Context engineering | What else goes in the window: docs, history, tool definitions | The conditions around one answer |
| Loop engineering | The system that decides what to prompt and when, and whether the result is acceptable | A self-running cycle across many turns |

> ⚠️ The leverage moved, the work did not get easier.
> Boris Cherny's point is not that coding got easier. It is that the **highest-value thing you can do shifted from writing prompts to designing loops**. A well-designed loop multiplies a good engineer. A badly designed loop multiplies a bad decision just as fast, with less of you watching.

Prompt engineering never goes away. Context engineering does not go away either. **Loop engineering adds the autonomous control structure around all of that.**

---

## 3. The Ralph Technique: Where the Loop Started

Before anyone called it loop engineering, there was **Ralph**. In early 2026 Geoffrey Huntley described running a coding agent inside a plain `while` loop:

- feed the agent the same prompt against a written spec
- let it pick one task and implement it
- start a fresh instance and feed the identical prompt again
- repeat until the work is done

He named it after Ralph Wiggum (the Simpsons character) because the technique is, in his words, **"deterministically simple in an unpredictable world"**.

### 非显而易见的洞见：上下文重置

A long agent session degrades as the window fills with old reasoning, dead ends, and stale file contents. Ralph sidesteps that entirely:

> Every iteration is a new agent with a clean context that reads the current state of the repo and the task list from disk, does exactly one unit of work, commits it, and exits.

The intelligence does not live in a heroic single run. **It lives in clear, granular specifications and verifiable outcomes, applied over and over against an external memory the model cannot pollute.**

### The Ralph Loop: One Task Per Fresh Context

```
while ! done:
    run agent:
        Read spec + state
        Do one task
        Test & commit
    Reset context
```

The task list on disk is the only memory that survives a reset.

### 原始 Ralph 实现

```bash
# The original Ralph loop: same prompt, fresh context, until done
while ! grep -q "ALL TASKS DONE" STATUS.md; do
  # each pass is a brand-new agent with an empty context window
  claude -p "Read PLAN.md and STATUS.md. Pick the next unchecked
task, implement it, run the tests, commit on success,
and update STATUS.md. Then stop." \
  --dangerously-skip-permissions
done

# PLAN.md and STATUS.md are the durable memory. The agent forgets
# everything between passes; the files remember what is done.
```

> 💡 Loop engineering is Ralph, productized.
> Ralph is the proof of concept that you do not need a clever harness, just persistence, an external state file, and verifiable stopping criteria. Loop engineering is what happens when those exact ideas move inside the tools.

---

## 4. The Five Building Blocks (Plus Memory)

A working loop needs **five things**, and then one place to remember state:

1. **Automations** — fire on a schedule and do discovery and triage by themselves.
2. **Worktrees** — so two agents working in parallel do not step on each other's files.
3. **Skills** — write down the project knowledge the agent would otherwise guess at every session.
4. **Plugins and connectors** — plug the agent into the tools you already use.
5. **Sub-agents** — one of them has the idea and a different one checks it.

The sixth piece is **memory**: a markdown file, a Linear or GitHub board, anything that lives outside a single conversation and holds what is done and what is next.

> The model forgets everything between runs, so the state has to live on disk, not in the context window. **The agent forgets. The repo does not.**

### The Anatomy of One Agent Loop

```
Automation fires on schedule
        ↓
Discover & triage work
        ↓
Sub-agent drafts the change
        ↓
Verifier sub-agent checks it
        ↓
Connectors open PR & ticket
        ↓
next cycle
(Memory on disk persists state)
```

---

## 5. Automations: The Heartbeat of a Loop

Automations are what make a loop an actual loop and not just one run you did once. **They are the heartbeat**: a recurring trigger that surfaces work without you asking.

### In OpenAI Codex
- **Automations tab**: pick project, prompt, cadence, local checkout vs background worktree
- Runs that find something land in a **Triage inbox**; runs that find nothing archive themselves
- An automation can **call a skill**, so the recurring instruction stays maintainable

### In Claude Code
- `/loop` schedules a recurring prompt on an interval (turns your cadence into a cron job)
- **hooks** fire shell commands at points in the agent lifecycle
- Push the whole thing to **GitHub Actions** to keep running after you close the laptop
- `/goal` keeps working across turns until a condition you wrote is verifiably true — after every turn, a separate, smaller model checks whether you are done (the agent that wrote the code is **not** the one grading it)

```bash
# Claude Code: run a recurring triage prompt every weekday at 9am
/loop "Read yesterday's CI failures and open issues, write findings
 to TODO.md, and draft fixes for anything labeled quick-win"
 --schedule "0 9 * * 1-5"

# Claude Code: run until a verifiable stopping condition holds
/goal "All tests in test/auth pass and lint is clean"

# OpenAI Codex: persisted long-running objective (CLI 0.128.0+)
codex /goal "Migrate the billing module to the new pricing API,
 keep all existing tests green"
```

> ⚠️ Watch the token bill.
> A scheduled loop with a verifier model running after every turn can burn tokens fast. Start with a slow cadence and a tight goal condition, watch the cost for a few days, and scale up only once the loop is producing work you actually merge.

### Write the stop condition like a contract, not a wish

A goal is only as good as the evidence that proves it.

| Contract field | Weak version | Verifiable version |
| :-- | :-- | :-- |
| End state | "Improve test coverage" | "Coverage for `src/billing` is at or above 90%" |
| Evidence | "It looks done" | "`npm test` exits 0 and the coverage report confirms the number" |
| Constraints | (unstated) | "Do not touch public APIs or delete existing tests" |
| Budget | (unbounded) | "Stop after 25 turns or $5, whichever comes first" |

> 💡 Three changes that make a loop trustworthy.
> The Claude Code team frames a reliable loop around three habits: **preserve mistakes** so the loop can learn from them instead of repeating them, **build verification into the loop** rather than bolting it on after, and **treat the failing test or red CI as the signal** that keeps the agent honest.

---

## 6. Worktrees: Parallel Agents Without Collisions

The moment you run more than one agent, files start colliding. A **git worktree** fixes it — a separate working directory on its own branch sharing the same repo history.

（原文此处被截断，下面是基于已抓取内容的整理）

> 本节为 lushbinary 指南原文中被截断的部分，工程实践要点可参考其他三篇已抓取的 Loop Engineering 文档。

---

## 7. Skills & Memory: Stop Re-Explaining Your Project

- **Skills** are project knowledge written down so the agent does not re-derive intent from zero every cycle.
- 形式：通常为 `SKILL.md`，包含 instructions 与 metadata，Claude Code 与 Codex 都使用此模式。
- **Memory** lives outside the conversation — markdown files, Linear boards, GitHub Issues。

> The model forgets between runs, the repo doesn't.

---

## 8. Sub-Agents: Separate the Maker From the Checker

The most useful structural thing: **split the one who writes from the one who checks**. The model that wrote the code is too nice grading its own homework.

---

## 9. What One Loop Looks Like, End to End

（原文此节描述了一个完整的 loop 端到端示例，常见结构为：）

1. 自动化每天早晨运行 triage skill，发现 CI 失败与开放 issue
2. 每个发现创建一个 worktree，派遣 sub-agent 起草修复
3. 第二个 sub-agent 按项目 skills 和现有测试审阅草稿
4. 连接器打开 PR，更新 ticket
5. 状态文件记录已尝试、通过、仍开放的内容

> You did not prompt any of those steps. That is Steinberger's whole point made real.

---

## 10. The Risks Loop Engineering Does Not Solve

- **Verification is still on you** — a loop running unattended is a loop making mistakes unattended.
- **Your understanding still rots** — the faster the loop ships code you did not write, the bigger the gap between what exists and what you actually understand.
- **Cognitive surrender is real** — designing the loop is the cure when you do it with judgment, and the accelerant when you do it to avoid thinking.

---

## 12. FAQ

### What is loop engineering?
The practice of designing systems that prompt coding agents automatically instead of prompting them by hand. You build a loop that discovers work, dispatches it to agents, verifies the output, and tracks what's done — all while you are not watching.

### What are the five building blocks of a loop?
Automations, worktrees, skills, plugins and connectors, and sub-agents. Plus a sixth element: **state or memory** that lives outside the conversation.

### How is this different from prompt engineering?
Prompt engineering is about writing a good prompt. Loop engineering is about designing a system where you don't need to write individual prompts anymore.

### Which tools support loop engineering?
Both OpenAI Codex and Claude Code ship all five primitives. The names differ slightly but the capability is the same.

### Do I still need to review the code?
Yes. Verification is the most important human role in the loop.

---

## 相关引用

- [vibe coding guide (Lushbinary)](https://lushbinary.com/blog/vibe-coding-developer-guide-ai-first-development/)
- [Claude Code agent teams (Lushbinary)](https://lushbinary.com/blog/claude-code-agent-teams-multi-agent-development-guide/)
- [AI coding agents comparison 2026 (Lushbinary)](https://lushbinary.com/blog/ai-coding-agents-comparison-cursor-windsurf-claude-copilot-kiro-2026/)
- [OpenAI Codex sub-agents guide (Lushbinary)](https://lushbinary.com/blog/openai-codex-subagents-autonomous-coding-teams-guide/)
