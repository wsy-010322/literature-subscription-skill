---
name: literature-subscription-skill
description: '通用化学术文献订阅与数字库建立。用户说出研究领域，自动创建文件夹结构，实现每日文献搜索、筛选、精读报告、邮件推送。'
version: 1.0.0
category: research
---

# Literature Subscription

## 触发

用户说"帮我搭建文献订阅"、"建立论文订阅系统"、"设置每日论文推送"时加载。

## 导航

本 skill 分 3 个阶段，严格按顺序执行。每个阶段只加载对应的 prompt 文件。

| 阶段 | 任务 | 加载 |
|---|---|---|
| Phase 1 | 引导对话，收集研究信息 | `00_prompts/phase1_onboarding.md` |
| Phase 2 | 创建文件夹结构 | `00_prompts/phase2_folder_setup.md` |
| Phase 3 | 注册为 Hermes skill + cron job | `00_prompts/phase3_register_and_cron.md` |

## 资源

- `references/` — 模板文件。Phase 2 时填充 `{{PLACEHOLDER}}` 后写入用户项目目录。
- `references/AGENTS.md.template` — 用户项目运行时的规则文件，Phase 2 结束时拷贝到用户项目根。
- `references/scripts/` — Python 去重/索引脚本，Phase 2 时拷贝到用户项目的 `scripts/`。

## 原则

- **用户确认驱动**：每个阶段结束时等待用户确认
- **模板化**：搜索词、话题、期刊、邮箱都是变量，填入 `user_config.json` 后才渲染为最终文件
- **不要一次性加载所有 prompt**：每个阶段只读对应的文件
