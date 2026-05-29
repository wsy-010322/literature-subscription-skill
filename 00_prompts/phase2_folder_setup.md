# Phase 2: Folder Structure Setup

根据 user_config.json 中的 topics，生成文件夹结构。

## Step 1: 读取配置

读取 `00_registry/user_config.json`。

## Step 2: 生成文件夹结构提案

基于 topics 列表，生成以下目录结构提案：

```
{PROJECT_ROOT}/
├── AGENTS.md                    # 文献管理 agent 规则
├── 00_registry/
│   ├── user_config.json         # 项目配置
│   ├── search_state.md          # 搜索状态机
│   ├── reviewed_candidates.md   # 已审核论文记录
│   ├── downloaded_papers.md     # 已下载论文记录
│   ├── pending_folder_approvals.md
│   ├── paper_index.jsonl        # 论文索引
│   ├── README.md
│   └── tmp/                     # 临时文件
├── 00_prompts/
│   ├── daily_search.md          # 每日搜索任务
│   ├── journal_filter.md        # 期刊过滤规则
│   ├── folder_routing.md        # 文件夹路由规则
│   ├── email_templates.md       # 邮件模板
│   ├── file_and_registry_rules.md
│   ├── reply_download.md        # 回复下载任务
│   ├── deep_read_report.md      # 精读报告模板
│   └── topic_queue.md           # 话题队列
├── 01_{topic1}/
│   └── README.md
├── 02_{topic2}/
│   └── README.md
├── ...（根据 topics 数量生成）
├── 08_daily_reports/
├── 09_weekly_reports/
├── 10_extracted_text/
│   └── README.md
├── 11_deep_read_reports/
│   └── README.md
├── scripts/\n│   ├── filter_fresh_candidates.py  # 去重脚本\n│   ├── enrich_candidates.py        # 期刊/影响因子/引用量查询\n│   ├── add_to_paper_index.py       # 索引入库脚本\n│   ├── check_duplicate.py          # 查重工具\n│   └── paper_key_utils.py          # 论文标识工具
└── 99_archive/
```

## Step 3: 展示并等待确认

将提案展示给用户：

> 这是根据你的话题生成的文件夹结构：
>
> [展示目录树]
>
> 每个话题会分配一个编号前缀的文件夹。论文 PDF 会归档到对应话题文件夹，每日报告放在 `08_daily_reports/`，精读报告放在 `11_deep_read_reports/`。
>
> 确认后我将创建这个文件夹结构。你也可以要求调整文件夹命名或增减话题。

## Step 4: 创建文件夹

用户确认后：

1. 创建所有文件夹和子文件夹
2. 从 skill 的 `references/AGENTS.md.template` 拷贝到项目根 `AGENTS.md`，替换 `{{PLACEHOLDER}}`
3. 从 skill 的 `references/scripts/` 复制 Python 脚本到项目 `scripts/`
4. 从 skill 的 `references/` 中读取各个 `.template.md`，替换 `{{PLACEHOLDER}}` 后写入 `00_prompts/`
5. 将 `user_config.json` 写入 `00_registry/`
6. 将 `search_state.md`（初始化状态）写入 `00_registry/`

## 文件夹编号规则

- 话题文件夹：`01_xxx`, `02_xxx`, `03_xxx`... 按用户列出的话题顺序编号
- registry 文件夹：`00_registry`
- prompt 文件夹：`00_prompts`
- 报告文件夹从 `08` 开始预留空间

## 需要填充用户自定义内容的文件

以下 prompt 文件需要根据 user_config.json 的实际内容替换占位符：

### daily_search.md
- 搜索关键词替换为 `user_config.search_keywords`
- 用户兴趣偏向替换为 topics
- 每日论文数量可配置

### journal_filter.md
- Tier S/Tier A 期刊列表替换为 `user_config.journal_tiers`

### folder_routing.md
- 路由表根据 `user_config.topics` 生成

### email_templates.md
- 发件人/收件人邮箱
- 项目标签（如 QEC 改为用户设置的项目缩写）

### topic_queue.md
- 话题队列根据 `user_config.topics` 生成
- 每个 topic 的 subtopics 根据配置生成
