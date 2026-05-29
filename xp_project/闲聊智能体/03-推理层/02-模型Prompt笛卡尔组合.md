### 2.5 模型 × Prompt 笛卡尔组合

**能力定位**：通过构建「模型池 × Prompt 池」的组合矩阵，实现多实验并行、灵活调度，避免单一配置的局限性。

**组合矩阵示例**：

```
模型池                    Prompt 池
────────────              ──────────────────
M1: GPT-4o          ×    P1: 温柔姐姐人设
M2: 文心一言 4.5    ×    P2: 活泼朋友人设
M3: 端侧小模型      ×    P3: 专业助理人设
                          P4: 幽默段子手人设

笛卡尔积 → 12 个候选配置（M×P combinations）
```

**路由调度策略**：

```
请求进入推理层
    ↓
读取 AB 实验分桶 → 确定当前用户命中哪个实验组
    ↓
实验组配置 = {model_id: "M1", prompt_id: "P2"}
    ↓
按 sub_intent 做 Prompt 精调：
    - 情感类  → Prompt 加入"共情引导"片段
    - 幽默类  → Prompt 加入"段子能力"片段
    - 问候类  → Prompt 精简，减少 token 消耗
    ↓
拼装最终 Prompt = Base 人设 + 场景片段 + 多轮上下文 + 当前 Query
```

**组合配置管理**：

```yaml
# 配置中心，支持热更新
combinations:
  - id: "combo_001"
    model: "gpt-4o"
    prompt_template: "persona_warm_sister"
    ab_group: "exp_A"
    weight: 0.3         # 流量占比

  - id: "combo_002"
    model: "ernie-4.5"
    prompt_template: "persona_funny_friend"
    ab_group: "exp_B"
    weight: 0.3

  - id: "combo_base"
    model: "ernie-4.5"
    prompt_template: "persona_default"
    ab_group: "control"
    weight: 0.4
```

**关键决策**：
- Prompt 采用**模板分段设计**（Base + 场景片段），避免全量 Prompt 膨胀，片段可独立迭代
- 新 combo 上线时先走**灰度流量（1%→5%→20%）**，指标达标后再放量，防止劣化配置大面积影响用户
- 模型间的**价格/质量/延迟三角**纳入路由权重，低峰期可多用大模型；高峰期自动切到小模型降本

**答辩问答预设**：
> Q：笛卡尔组合数量爆炸怎么办，不可能把所有组合都跑一遍 AB？
> A：对，实际上我们采用**分阶段淘汰**策略：先用小流量快速过滤明显差的组合（统计显著需要 N 次请求），再把胜出的 top-K 进入下一轮精细对比。本质上是个多臂赌博机（MAB）问题，用 UCB 或 Thompson Sampling 做流量分配，收敛速度比纯 AB 快 3~5 倍。

---

