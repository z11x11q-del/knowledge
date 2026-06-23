#!/usr/bin/env python3
"""
Batch-add YAML frontmatter to all markdown files in the vault.

Rules:
- Skip files that already have frontmatter (start with --- on line 1).
- Determine tags + status by directory.
- updated: 2026-06-23 (today's date per task context).
- Preserve original content; insert frontmatter at the top.
"""

import os
import sys
from pathlib import Path

VAULT_ROOT = Path(r"D:\code\own-github\knowledge")
TODAY = "2026-06-23"

# (tags, status) by directory prefix
# Order matters: more specific prefixes first.
DIR_RULES = [
    # loop_engineering docs - 资料摘录
    ("loop_engineering/docs/", (["loop-engineering", "AI编码", "资料"], "📦")),
    ("loop_engineering/", (["loop-engineering", "AI编码", "索引"], "✅")),
    # xp_project sub-projects
    ("xp_project/闲聊智能体/07-ADR/", (["小鹏项目", "闲聊智能体", "ADR"], "✅")),
    ("xp_project/闲聊智能体/08-记忆架构/", (["小鹏项目", "闲聊智能体", "记忆架构"], "✅")),
    ("xp_project/闲聊智能体/06-基础能力/", (["小鹏项目", "闲聊智能体", "基础能力"], "✅")),
    ("xp_project/闲聊智能体/05-闭环层/", (["小鹏项目", "闲聊智能体", "闭环层"], "✅")),
    ("xp_project/闲聊智能体/04-后处理层/", (["小鹏项目", "闲聊智能体", "后处理层"], "✅")),
    ("xp_project/闲聊智能体/03-推理层/", (["小鹏项目", "闲聊智能体", "推理层"], "✅")),
    ("xp_project/闲聊智能体/02-预处理层/", (["小鹏项目", "闲聊智能体", "预处理层"], "✅")),
    ("xp_project/闲聊智能体/", (["小鹏项目", "闲聊智能体"], "✅")),
    ("xp_project/", (["小鹏项目", "项目经验"], "✅")),
    # car_voice_wiki
    ("car_voice_wiki/03-语音能力/", (["车机语音", "wiki", "语音能力"], "🚧")),
    ("car_voice_wiki/", (["车机语音", "wiki"], "🚧")),
    # doubao
    ("doubao_realtime_voice/", (["豆包", "多模态", "实时语音"], "🚧")),
    # lbs
    ("lbs/", (["lbs", "八股", "求职"], "✅")),
    # expression
    ("expression/", (["话术", "面试", "表达"], "✅")),
    # life_work
    ("life_work/", (["个人发展", "规划"], "✅")),
    # renamed directories
    ("文心Web/", (["文心一言", "项目", "归档"], "📦")),
    ("待发展能力/", (["能力", "待办"], "🚧")),
    ("随手记/", (["随手记", "临时"], "📦")),
]

ROOT_README_TAGS = (["导航", "vault"], "✅")


def classify(rel_path: str):
    """Return (tags, status) for a given relative path."""
    if rel_path == "README.md":
        return ROOT_README_TAGS
    for prefix, rule in DIR_RULES:
        if rel_path.startswith(prefix):
            return rule
    # Fallback
    return (["未分类"], "🚧")


def file_already_has_frontmatter(path: Path) -> bool:
    """Check whether the file already begins with a '---' line."""
    try:
        with path.open("r", encoding="utf-8") as f:
            first = f.readline()
            return first.strip() == "---"
    except Exception:
        return False


def build_frontmatter(tags, status) -> str:
    """Build a YAML frontmatter block."""
    tags_yaml = "[" + ", ".join(tags) + "]"
    return (
        "---\n"
        f"tags: {tags_yaml}\n"
        f"status: {status}\n"
        f"updated: {TODAY}\n"
        "---\n\n"
    )


def process_file(path: Path) -> bool:
    rel = path.relative_to(VAULT_ROOT).as_posix()
    if file_already_has_frontmatter(path):
        print(f"SKIP (has frontmatter): {rel}")
        return False
    tags, status = classify(rel)
    frontmatter = build_frontmatter(tags, status)
    with path.open("r", encoding="utf-8") as f:
        original = f.read()
    # Avoid double-prepending an existing blank line
    payload = frontmatter + original.lstrip("\n")
    with path.open("w", encoding="utf-8") as f:
        f.write(payload)
    # Use safe ASCII output for Windows console
    status_label = {"✅": "DONE", "🚧": "WIP", "📦": "ARCHIVE"}.get(status, status)
    print(f"OK: {rel}  tags={tags}  status={status_label}")
    return True


def main():
    count_total = 0
    count_processed = 0
    for dirpath, dirnames, filenames in os.walk(VAULT_ROOT):
        # Skip hidden / config dirs
        parts = Path(dirpath).parts
        if any(p.startswith(".") for p in parts[len(VAULT_ROOT.parts):]):
            continue
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            full = Path(dirpath) / fn
            count_total += 1
            if process_file(full):
                count_processed += 1
    print(f"\nTotal .md files scanned: {count_total}")
    print(f"Processed (frontmatter added): {count_processed}")


if __name__ == "__main__":
    main()
