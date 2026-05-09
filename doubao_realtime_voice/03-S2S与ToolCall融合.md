# 03 S2S × ToolCall 融合：多意图车控场景

**场景**：用户说 `帮我打开空调并且调节座椅靠背`

## 一、核心机制：统一 Token 空间

S2S 模型不是"音频进 → 音频出"的黑盒，现代端到端语音大模型（豆包实时语音、GPT-4o Realtime 同类）输出的是 **混合 token 流**：

```
模型输出序列 = [speech_token | text_token | tool_call_token] 交错
```

解码器按 token 类型**实时分流**：

- `speech_token` → TTS 声码器 → 扬声器（流式播放）
- `tool_call_token` → Tool Executor → 车机总线/API
- `text_token` → 字幕通道

这样就**在同一次推理里**既能说话又能调工具，而不是"先 ASR 再 LLM 再 TTS"的三段式。

---

## 二、场景完整时序

### 时序图

```
时间线 ──────────────────────────────────────────────────►

用户语音: ━━━━━━━━━━"帮我打开空调并且调节座椅靠背"━━━┓
                                                      ┃ VAD 结束
                                                      ▼
S2S模型输入:       [历史ctx] + [audio_tokens_of_query]
                                                      │
                   模型流式解码，边推边出 ↓
                                                      │
输出token流(时间顺序):
  ├─ [speech]"好的"  ────────────────────────► 立即播放
  ├─ [speech]"，马上为您"                     ► 继续播放
  │
  ├─ [tool_call] {
  │     id: "t1",
  │     name: "hvac.turn_on",
  │     args: {}
  │   } ───────────────────────────────► 派发至车控总线(并行)
  │
  ├─ [tool_call] {
  │     id: "t2",  
  │     name: "seat.adjust_backrest",
  │     args: {angle: <MISSING>}         ← 槽位缺失
  │   } ───────────────────────────────► 不派发，触发反问
  │
  ├─ [speech]"打开空调"
  ├─ [speech]"，座椅靠背您想调到"
  └─ [speech]"多少度？"  ──────────────► 播放完毕，进入LISTENING
                                                      │
                                                      ▼
并行工具执行通道:
  t1: hvac.turn_on()  ──► CAN总线 ──► 200ms返回 success
                                        │
                                        ▼
                              结果注入下一轮上下文(静默)
```

### 输出的实际 token 流（示意）

```
<|speech_start|>好的，马上为您<|speech_end|>
<|tool_call_start|>
{"id":"t1","name":"hvac.turn_on","args":{}}
<|tool_call_end|>
<|tool_call_start|>
{"id":"t2","name":"seat.adjust_backrest","args":{},"missing":["angle"]}
<|tool_call_end|>
<|speech_start|>打开空调，座椅靠背您想调到多少度？<|speech_end|>
```

---

## 三、关键设计点

### 1. 多意图在模型内部先拆解

模型直接在一次生成中**发出两个 tool_call**，不需要外层再跑一个"意图拆解器"。这是 LLM 比传统 NLU pipeline 强的地方。

### 2. 槽位缺失的三种策略

| 策略 | 说明 | 适用场景 |
|---|---|---|
| **反问补槽** | 如上，angle 缺失 → 语音反问 | 安全相关 / 无默认值 |
| **默认值填充** | `angle = user_preference.default_backrest` 或记忆中的常用值 | 用户历史偏好明确 |
| **乐观执行+可撤销** | 先调到中位，播报"已调到舒适位置，需要调整请告诉我" | 体验优先场景 |

豆包车机场景大概率是 **用户记忆 + 默认值** 优先，反问兜底。

### 3. 边说边执行（流式并行）

```
话术播放时间:  |好的，马上为您|打开空调|，座椅靠背...|
工具派发时间:      ↑派发t1  ↑派发t2
工具返回时间:                    ↑t1 success
```

**工具调用不阻塞话术**，用户听到话的同时空调已经在开了。这是车机场景用户感知"快"的关键。

### 4. 工具结果回流

```
t1 返回 success → 作为 system message 注入下一轮：
  {"tool_result": {"id":"t1","status":"ok","data":{"temp":24}}}

如果用户继续说"那就28度吧"：
  模型看到：[上一轮t1已成功] + [本轮:28度] 
  → 只发 t2 的 tool_call，并说"好的，已调整"
```

### 5. 失败处理与话术改写

```
假设 t1 返回 failure（空调故障）：
  模型要能"改口" —— 但已经说出的"马上为您打开空调"收不回

工程解法：
  ├─ 方案A: 话术延后 —— 关键确认话术放在 tool_call 之后再说
  │         "好的" → [tool_call] → 等结果 → "空调已打开/打开失败"
  ├─ 方案B: 补偿话术 —— 继续说"不过空调好像有点问题，我再试试"
  └─ 方案C: 二次 turn —— 工具失败作为新事件，模型发起新轮次通知
```

实际产品通常是 **A+B 混合**：先说模糊话术("好的，稍等")，结果出来再说确定话术。

---

## 四、训练层面的配合

S2S 模型要能正确输出 tool_call，训练数据里必须有：

```
多模态对话样本：
  user_audio: "帮我打开空调并且调节座椅靠背"
  assistant_output:
    <speech>好的，马上为您</speech>
    <tool_call>hvac.turn_on()</tool_call>
    <tool_call>seat.adjust_backrest(angle=?)</tool_call>
    <speech>打开空调，座椅靠背调到多少度？</speech>
```

也就是在 SFT 阶段，把 **语音 token + 工具调用 token** 在同一序列里混合训练，让模型学会什么时候说、什么时候调。

---

## 五、完整链路总结

```
"帮我打开空调并且调节座椅靠背"
        │
        ▼ (50ms)
    音频编码 → audio tokens
        │
        ▼ (300ms 首token)
    S2S模型流式解码
    ├─► speech: "好的，马上为您"  ─────► TTS播放 (~500ms用户听到)
    ├─► tool: hvac.turn_on         ─────► 车控并行执行
    ├─► tool: seat.adjust (缺槽)   ─────► 挂起，触发反问
    └─► speech: "打开空调，座椅靠背调到多少度？"
        │
        ▼
    用户回答"120度" → 新一轮 → 补槽 → seat.adjust(angle=120) → "已调整"
```

---

## 一句话总结

S2S 和 ToolCall 的结合点是 **"同一个模型、同一次推理、一条混合 token 流"**，由解码器实时分流到语音通道和工具通道；多意图在模型内部天然拆解为多个并行 tool_call，缺槽位触发反问，失败靠补偿话术兜底。
