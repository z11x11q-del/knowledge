---
tags: [loop-engineering, AI编码, 索引]
status: ✅
updated: 2026-06-23
---

# Links

> 本文件用于记录 `loop_engineering` 目录下需要关注的链接。
> 每条链接包含：**名称**、**实际地址**、**本地提取状态**。

| 序号 | 名称 | 实际地址 | 本地文档 | 已提取 | 翻译 | 提取时间 |
| :--: | :-- | :-- | :-- | :--: | :--: | :-- |
| 1 | Loop Engineering：从微反馈回路到自进化循环 | <https://mp.weixin.qq.com/s/OebIEJmc6Ls2IS_TO2XXMA> | [loop_engineering.md](./docs/loop_engineering.md) | ✅ | —（中文原文） | 2026-06-16 |
| 2 | Prompt 该退环境了，未来属于 Loop Engineering（Khazix @ X） | <https://x.com/Khazix0918/status/2066394718519656909> | [x_khazix0918_prompt_should_retire.md](./docs/x_khazix0918_prompt_should_retire.md) | ✅ | —（中文原文） | 2026-06-16 |
| 3 | Loop engineering for AI coding agents（Kyenai Guide） | <https://www.kyenai.com/guides/loop-engineering-ai-coding-agents?utm_source=chatgpt.com> | [kyenai_loop_engineering_guide.md](./docs/kyenai_loop_engineering_guide.md) | ✅ | [中文](./docs/kyenai_loop_engineering_guide_cn.md) | 2026-06-16 |
| 4 | Loop Engineering: Designing Systems That Prompt AI Agents（Lushbinary） | <https://lushbinary.com/blog/loop-engineering-ai-coding-agents-guide/?utm_source=chatgpt.com> | [lushbinary_loop_engineering_guide.md](./docs/lushbinary_loop_engineering_guide.md) | ✅ | [中文](./docs/lushbinary_loop_engineering_guide_cn.md) | 2026-06-16 |
| 5 | Loop Engineering（loopengineering.lol 站点） | <https://loopengineering.lol/?utm_source=chatgpt.com> | [loop_engineering_lol.md](./docs/loop_engineering_lol.md) | ✅ | [中文](./docs/loop_engineering_lol_cn.md) | 2026-06-16 |

---

## 字段说明

- **名称**：链接对应的文章 / 资源标题。
- **实际地址**：原始 URL（点击可访问）。
- **本地文档**：提取后保存到本地的 Markdown 文件相对路径（位于 `./docs/`）；若未提取则为 `-`。
- **已提取**：✅ 表示全文已保存到本地；❌ 表示仅记录链接，正文未提取。
- **翻译**：英文原文附中文翻译时，给出 `_cn.md` 的相对路径；中文原文则填 `—（中文原文）`。
- **提取时间**：将正文保存到本地的日期（`YYYY-MM-DD`）。

## 目录结构

```
loop_engineering/
├── link.md            # 本文件：链接索引
└── docs/              # 所有下载 / 翻译的文档
    ├── loop_engineering.md                  # 微信原文（中文）
    ├── x_khazix0918_prompt_should_retire.md # X 文章原文（中文）
    ├── kyenai_loop_engineering_guide.md     # 英文原文
    ├── kyenai_loop_engineering_guide_cn.md  # 中文翻译
    ├── lushbinary_loop_engineering_guide.md # 英文原文
    ├── lushbinary_loop_engineering_guide_cn.md # 中文翻译
    ├── loop_engineering_lol.md               # 英文原文
    └── loop_engineering_lol_cn.md            # 中文翻译
```

## 使用约定

1. 新增链接时，按表格顺序追加一行。
2. 提取正文后：
   - 在「本地文档」列填写 `./docs/<文件名>.md` 相对路径
   - 将「已提取」改为 ✅
   - 填写「提取时间」
3. 命名规范：本地文件名建议与「名称」对应，使用下划线连接，例如 `loop_engineering.md`。
4. 翻译规则：英文原文追加 `<原文件名>_cn.md` 中文翻译，并在「翻译」列填写相对路径；中文原文填 `—（中文原文）`。
