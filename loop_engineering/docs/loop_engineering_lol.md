---
tags: [loop-engineering, AI编码, 资料]
status: 📦
updated: 2026-06-23
---

# Loop Engineering

> 原文链接：<https://loopengineering.lol/?utm_source=chatgpt.com>
>
> 站点：loopengineering.lol
> 提取时间：2026-06-16

---

## 核心命题

> You don't really need to be good at prompting anymore. The thing to get good at is the loop that does the prompting for you. It's five building blocks plus state that make up a loop: **automations, worktrees, skills, plugins, and sub-agents**.

**Core loop**: Automate → Isolate → Skill → Connect → Verify

---

## What Makes Loop Engineering Different

Loop engineering is **replacing yourself as the person who prompts the agent**. You design the system that does it instead.

> "You shouldn't be prompting coding agents anymore. You should be designing loops that prompt your agents."
> — **Peter Steinberger**

> "I don't prompt Claude anymore. I have loops running that prompt Claude and figuring out what to do. My job is to write loops."
> — **Boris Cherny**, head of Claude Code at Anthropic

> For like two years the way you got something out of a coding agent was you wrote a good prompt and shared enough context. You type a thing, you read what came back, you type the next thing. The agent is a tool and you are holding it the entire time, one turn after the other. That part is kind of over, or at least some think it's going to be.
>
> Now you build a small system that finds the work, hands it out, checks it, writes down what is done and then decides the next thing, and you let that system poke the agents instead of you. **Loop engineering sits one floor above the harness.** The harness that runs on a timer, it spawns little helpers, and it feeds itself.

---

## 四大特征

### 01 — A Real Feedback Loop
The agent proposes a change, runs the experiment, reads the result, and keeps only the ideas that improve the outcome.

### 02 — Not Just Automation
Automations handle discovery and triage on a schedule. **They are the heartbeat** that makes a loop an actual loop and not just one run.

### 03 — Skills Codify Knowledge
A skill is project knowledge written down in a `SKILL.md` so the agent doesn't re-derive intent from zero every cycle.

### 04 — Sub-Agents Verify
The most useful structural thing: **split the one who writes from the one who checks**. The model that wrote the code is too nice grading its own homework.

---

## The Five Pieces (Plus State)

A loop needs **five things** and then **one place to remember stuff**. Here is the shape that works in Codex, Claude Code, and every tool that follows.

| # | Primitive | Job in the Loop |
| :--: | :-- | :-- |
| 1 | **Automations** | Discovery + triage on a schedule |
| 2 | **Worktrees** | Isolate parallel features |
| 3 | **Skills** | Codify project knowledge |
| 4 | **Plugins / Connectors** | Connect your tools |
| 5 | **Sub-Agents** | Ideate and verify |
| 6 | **State** | Track what's done |

### 1. Automations
Automations are what make a loop an actual loop and not just one run you did once. Define an autonomous task, give it a cadence, and let the findings come to you.

### 2. Worktrees
The second you run more than one agent the files start colliding. A git worktree fixes it — a separate working directory on its own branch sharing the same repo history.

### 3. Skills
A skill is how you stop re-explaining the same project context every session. Both tools use a folder with a `SKILL.md` holding instructions and metadata.

### 4. Plugins & Connectors
A loop that can only see the filesystem is a tiny loop. Connectors built on MCP let the agent read your issue tracker, query a database, or drop a message in Slack.

### 5. Sub-Agents
A second agent with different instructions and sometimes a different model catches the stuff the first one talked itself into. **The maker and checker, split.**

### 6. State (Memory)
A markdown file or a Linear board — anything that lives outside the single conversation and holds what's done and what is next. **The model forgets between runs, the repo doesn't.**

---

## How One Loop Works

Stick it together and a single thread turns into a little control panel.

### 01 — An automation runs every morning
Its prompt calls a **triage skill** that reads yesterday's CI failures, the open issues, the recent commits, and writes the findings into a markdown file or a Linear board.

### 02 — Isolated worktrees for each fix
For each finding worth doing, the thread opens an isolated worktree and sends a sub-agent to draft the fix, and a second sub-agent reviews that draft against the project skills and existing tests.

### 03 — Connectors close the loop
Connectors let the loop open the PR and update the ticket. Anything the loop can not handle lands in the triage inbox. The state file remembers what got tried, what passed, what is still open.

### 04 — You designed it one time
You did not prompt any of those steps. That is Steinberger's whole point made real, and it's the same loop in Codex or in Claude Code because the pieces are the same pieces.

---

## What the Loop Still Does Not Do for You

The loop changes the work. **It does not delete you from it.** Three problems actually get sharper as the loop gets better.

### Verification Is Still on You
A loop running unattended is also a loop making mistakes unattended. **Your job is to ship code you confirmed works.**

### Your Understanding Still Rots
The faster the loop ships code you did not write, the bigger the gap between what exists and what you actually understand. **Read what the loop made.**

### Cognitive Surrender Is Real
When the loop runs itself it's tempting to stop having an opinion. **Designing the loop is the cure when you do it with judgment and the accelerant when you do it to avoid thinking.**

> **Build the loop. But build it like someone who intends to stay the engineer, not just the person who presses go.**

---

## FAQ

### What is loop engineering?
The practice of designing systems that prompt coding agents automatically instead of prompting them by hand. You build a loop that discovers work, dispatches it to agents, verifies the output, and tracks what's done — all while you are not watching.

### What are the five building blocks of a loop?
Automations, worktrees, skills, plugins and connectors, and sub-agents. Plus a sixth element: **state or memory** that lives outside the conversation.

### How is this different from prompt engineering?
Prompt engineering is about writing a good prompt. Loop engineering is about designing a system where you don't need to write individual prompts anymore — the loop does it for you.

### Which tools support loop engineering?
Both OpenAI Codex and Claude Code ship all five primitives. The names differ slightly but the capability is the same. A loop designed for one works in the other with minimal adjustment.

### Do I still need to review the code?
Yes. **Verification is the most important human role in the loop.** A loop running unattended is also a loop making mistakes unattended.

---

*Loop Engineering — Design systems that prompt agents, not yourself.*

*Views and opinions expressed on this site are for informational purposes only.*
