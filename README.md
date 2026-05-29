# 📚 AI 文献订阅与数字图书馆

一个让 AI Agent 帮你自动管理学术文献的系统——每日搜索、智能筛选、邮件推送、一键精读，全部自动化。

用一个文件夹结构维护你的学术数字图书馆，浏览器直接查看，任何 Markdown 编辑器都能打开。支持 OpenClaw、Hermes Agent、Claude Code 等 AI Agent 一键安装。

---

## 快速开始

> 在 AI Agent（OpenClaw / Hermes / Claude Code）中说：

```
请从 GitHub 安装 literature-subscription-skill：
https://github.com/wsy-010322/literature-subscription-skill
```

然后对 AI 说：

```
帮我搭建文献订阅
```

AI 会引导你走完 3 步：收集研究方向 → 创建文件夹 → 注册定时任务。之后每天自动运行。

---

## 核心功能

| 功能 | 说明 |
|---|---|
| 📂 分类建立文献库，方便检索和存放 | 按研究方向自动创建文件夹结构，PDF 归类存放，README 里能看到每个文献的标题、作者、网站、大致内容总结，还有给你自己写备注的位置 |
| 📧 每天生成论文日报，包含泛读摘要 | 每天自动搜 arXiv，Python 去重，再查期刊和引用量，AI 精选 5 篇最值得读的发你邮箱。期刊好、影响因子高的优先抓取，不看是否最新 |
| 📖 回复 AI 精读，自动下载并生成精读报告 | 在邮件里回复 `1,3,5` 或 `下载第1篇`，AI 自动下载 PDF、提取全文、分块分析，出结构化中文精读报告发给你 |

---

## 项目优势

| 优势 | 说明 |
|---|---|
| 🐍 论文去重等操作用 Python 脚本实现，不消耗 token | 去重、索引管理、查期刊/引用量这些全是 Python 脚本跑的，AI 只做读摘要、判断质量、写报告这几件事 |
| 💰 不会一次性录入大量论文浪费 token | 每次搜索先存成 JSON，AI 按需逐篇读取，不是一口气喂进去几十篇摘要把上下文撑爆 |
| 📦 接入 DeepSeek，一次任务几毛钱 | 默认用 DeepSeek 模型，一次完整搜索+筛选+报告几毛钱。想用 GPT-4o 也支持 |
| 📂 纯文件夹，零绑定 | 整个文献库就是个文件夹——PDF、Markdown、JSON。哪天不想用 AI 了，照常打开看，换 ChatGPT 讨论也行 |
| 🔧 高度可定制 | 研究话题、期刊白名单、搜索频率、模型、邮箱全都可以自己改 |

---

## 工作流

```
arXiv 搜索 15 篇
      ↓
Python 去重 (filter_fresh_candidates.py)
      ↓
Python 富化 (enrich_candidates.py)  ← 查 OpenAlex，拿到引用量、期刊名、h-index、近似影响因子
      ↓
AI 按期刊优先级精选 5 篇
      ↓
生成日报 → 邮件推送
      ↓
用户回复编号 → AI 下载 PDF → 精读 → 报告邮件
```

---

## 生成的文献库长这样

```
LLM文献阅读_hermess/              ← 你的数字图书馆
├── 01_世界模型/                   ← PDF 按话题分类放
├── 02_注意力机制/
├── 03_因果律/
├── 08_daily_reports/             ← 每日推荐报告（通过邮箱发给你）
├── 10_extracted_text/            ← AI 从 PDF 提取的 txt，方便 AI 阅读
├── 11_deep_read_reports/         ← 精读报告
├── 00_registry/                  ← 索引、去重记录、搜索状态
└── scripts/                      ← Python 工具脚本
```

---

## 安装要求

- Python 3.10+
- 一个 AI Agent（Hermes Agent / OpenClaw / Claude Code）
- 邮箱账号（用于接收日报，支持 163/QQ/Gmail）

不需要 API Key（OpenAlex 免费开放，arXiv 也开放），不需要数据库，不需要 Docker。

---

## 目录结构

```
├── SKILL.md                     ← AI 读取的入口
├── README.md
├── 00_prompts/                  ← 向导脚本（引导用户配置）
│   ├── phase1_onboarding.md
│   ├── phase2_folder_setup.md
│   └── phase3_register_and_cron.md
└── references/                  ← 模板与脚本
    ├── daily_literature_skill_template.md
    ├── daily_search.template.md
    ├── deep_read_report.md
    ├── reply_download.md
    ├── file_and_registry_rules.md
    ├── journal_filter.template.md
    ├── folder_routing.template.md
    └── scripts/
        ├── enrich_candidates.py       ← 查期刊/引用量 (OpenAlex + arXiv API)
        ├── filter_fresh_candidates.py ← 去重
        ├── add_to_paper_index.py      ← 索引入库
        ├── check_duplicate.py         ← 查重
        └── paper_key_utils.py         ← 标识工具
```

---

## 常见问题

| 问题 | 回答 |
|---|---|
| 每天 5 篇会不会太少？ | 5 篇是精选过的最值得读的，读太多很累。非要每天看 20 篇也能调 |
| 支持哪些学科？ | 所有。arXiv 覆盖物理、CS、数学、生物等。期刊白名单自己定 |
| 费用多少？ | DeepSeek 一次任务约 ¥0.1-0.5。OpenAI GPT-4o 约 ¥1-3。OpenAlex 和 arXiv API 免费 |
| 能不能只搜索不下载？ | 默认就是不下载 PDF。只有你在邮件里回复要求精读时才下 |

---

## License

MIT
