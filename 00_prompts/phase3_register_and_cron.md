# Phase 3: Register Skill & Set Up Cron Job

将配置好的文献库接入 Hermes Agent 的日常运行流程。

## Step 1: 确认 Hermes Skill 注册

向用户确认：

> 文件夹结构和配置文件已经创建好了。接下来我需要把这个工作流注册为 Hermes Agent 的一个 skill，这样你随时可以说"文献查询执行"来触发每日搜索。
>
> 我也会帮你设置一个每天定时执行的 cron job。

## Step 2: 创建/更新 Hermes Skill

使用 Hermes 的 `skill_manage` 工具，将整个文献库注册为一个 skill。

Skill 名称建议：`daily-literature-search`（如果用户有多个文献库，可以用 `daily-literature-search-{project_tag}`）。

Skill 内容包含：
- 指向 `{PROJECT_ROOT}/AGENTS.md` 的引用
- 指向 `{PROJECT_ROOT}/00_registry/user_config.json` 的配置路径
- daily search 工作流的完整步骤（与现有 qec-daily-literature-search skill 结构类似，但参数化）

参见 `references/daily_literature_skill_template.md` 获取 skill 模板。

## Step 3: 设置 Cron Job

使用 Hermes 的 `cronjob` 工具创建定时任务：

```
- schedule: 用户指定（默认每天早上 9:00，"0 9 * * *"）
- prompt: "文献查询执行"
- skill: 上一步创建的 skill 名称
- 模型：默认 DeepSeek
- 不下载 PDF，不生精读报告（被 cron job 调用时）
```

向用户确认 cron 时间。

## Step 4: 告知用户使用方式

最终告知用户：

> 设置完成！以下是使用方式：
>
> 1. 对我说"文献查询执行"即可手动触发每日搜索
> 2. 每天 {时间} 自动执行一次搜索并发送邮件
> 3. 收到邮件后，回复论文编号（如 "1,3,5"）即可触发 PDF 下载和精读
> 4. 配置文件在 `{PROJECT_ROOT}/00_registry/user_config.json`，随时可以修改
>
> 需要修改任何配置或话题时，告诉我即可。
