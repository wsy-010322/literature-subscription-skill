# Daily Literature Search Skill Template

This is the template for the Hermes skill that will be registered in Phase 3.
Replace {{PLACEHOLDERS}} with actual values from user_config.json.

---

name: daily-literature-search-{{PROJECT_TAG_LOWER}}
description: '{{RESEARCH_DOMAIN}} 每日文献查询：搜索、去重、筛选、报告、邮件。'
version: 1.0.0
category: research
---

# {{PROJECT_NAME}} Daily Literature Search

## Trigger

用户说"文献查询执行"时，立即执行此 skill。

## Base Path

```
{{PROJECT_ROOT}}
```

以下路径均相对于此 base path。

## Required Files (按顺序加载)

1. `00_registry/search_state.md`
2. `00_prompts/daily_search.md`
3. `00_prompts/topic_queue.md`
4. `00_prompts/journal_filter.md`
5. `00_prompts/folder_routing.md`
6. `00_prompts/email_templates.md`
7. `00_prompts/file_and_registry_rules.md`

## Workflow

### Step 1: 读 search_state.md

从 `search_state.md` 获取 `active_topic` 和 `active_subtopic`。

### Step 2: 读所有 required prompt 文件

按顺序读完所有 prompt 文件。

### Step 3: 搜索论文

**排序优先级**（不可被忽略或压低）：

1. **期刊等级**（Tier S > Tier A > 其他顶刊）
2. **引用量**（高引用经典论文优先于新论文）
3. **相关性**（与 active_subtopic 匹配）

**绝对禁止**：仅用 `sortBy=submittedDate` 搜索。这会系统性地遗漏高引用的经典论文。

**搜索分层**：

第一轮（必须执行，不可压缩）：**顶刊 + 高引用搜索**
- 用 Tier S 期刊名称 + 关键词 query，`sortBy=relevance`，不加日期限制。
- 不加过多 AND 过滤，确保捕获综述和里程碑论文。
- 取 ~10 篇。

第二轮：**active_subtopic 定向搜索**
- 用当前 subtopic 对应的关键词 query，`sortBy=relevance`。
- 如当前 subtopic 产出不足，fallback 到相邻 subtopic。
- 取 ~8 篇。

第三轮：**最新补充**（可选，前面两轮不足 15 篇时才用）
- `sortBy=submittedDate`，仅覆盖最近 1-2 个月。
- 取 ~5 篇。

总候选目标 15-20 篇，合并去重。

**原则**：筛选时先看期刊等级和引用量，再看是否与 active_subtopic 相关。
新但不好的论文不选；好但旧的论文优先选。

### Step 4: 保存原始候选

保存到 `00_registry/tmp/raw_candidates_YYYY-MM-DD.json`。

### Step 5: 去重过滤

```bash
cd "{{PROJECT_ROOT}}" && python3 scripts/filter_fresh_candidates.py --input "00_registry/tmp/raw_candidates_YYYY-MM-DD.json" --output "00_registry/tmp/fresh_candidates_YYYY-MM-DD.json"
```

### Step 5b: 富化候选（期刊/影响因子/引用量查询）

去重后，对每篇 fresh candidate 查询以下数据：

1. **arXiv API** — 获取 `journal_ref` 和 `DOI`（如果有）
2. **OpenAlex API** — 按 DOI 或标题查询：
   - `cited_by_count`（引用量）
   - `primary_location.source.display_name`（发表的期刊/会议名）
   - `primary_location.source.issn_l`（期刊 ISSN）
   - 期刊级指标：`h_index`、`2yr_mean_citedness`（近似影响因子）

```bash
cd "{{PROJECT_ROOT}}" && python3 scripts/enrich_candidates.py --input "00_registry/tmp/fresh_candidates_YYYY-MM-DD.json" --output "00_registry/tmp/enriched_candidates_YYYY-MM-DD.json"
```

输出 JSON 新增字段：
- `enriched_journal`: 验证后的期刊名
- `enriched_venue_issn`: ISSN-L
- `enriched_cited_by_count`: 引用量（-1 表示未查到）
- `enriched_h_index`: 期刊 h-index（-1 表示未查到）
- `enriched_2yr_mean_citedness`: 期刊 2 年平均被引（-1 表示未查到）
- `enriched_source`: `openalex` / `arxiv_only` / `none`

### Step 6: 读取 enriched 候选，按期刊/影响因子/引用量筛选

### Step 7: 选出最多 {{DAILY_PAPER_COUNT}} 篇高质量论文

- **第一优先**：顶刊/顶会（Tier S > Tier A）
- **第二优先**：高影响因子和高引用量
- 与 active_subtopic 高度相关
- 不凑数
- 如低产出，更新 search_state.md 计数器

**筛选机制**（用户配置时告知）：期刊好、影响因子高的论文优先入选。同一话题下，优先推荐发表在 Tier S 期刊或高引用的经典论文，而非仅看新鲜度。

### Step 8: 保存并加入索引

保存到 `00_registry/tmp/selected_candidates_YYYY-MM-DD.json`，然后：

```bash
cd "{{PROJECT_ROOT}}" && python3 scripts/add_to_paper_index.py --input "00_registry/tmp/selected_candidates_YYYY-MM-DD.json"
```

### Step 9: 更新 registry

更新：
- `00_registry/reviewed_candidates.md`
- 目标主题文件夹 `README.md`
- `00_registry/search_state.md`（计数器）

### Step 10: 生成每日报告

生成 `08_daily_reports/{{PROJECT_TAG}}_daily_summary_YYYY-MM-DD.md`。

### Step 11: 渲染并发送邮件

- 优先 pandoc + xelatex 渲染 PDF
- SMTP 信息从 `00_registry/user_config.json` email 字段获取
- 附件只附 PDF，不附 Markdown

### Step 12: 回复轮询

发完邮件后，创建一次性 cron job 来轮询 INBOX。

## 规则

- 不下载 PDF（被 cron job 调用时）
- 不生精读报告（被 cron job 调用时）
- 不读完整 paper_index.jsonl
- 不凑数
- **期刊等级和引用量是第一筛选标准，不是新鲜度**

## 模型

默认 DeepSeek。
