# Email Templates

## Daily summary email

Subject:

`每日{{PROJECT_TAG}}文献摘要 - YYYY-MM-DD`

Body structure:


今天筛选了 {{DAILY_PAPER_COUNT}} 篇{{RESEARCH_DOMAIN}}相关文献，已避免与历史记录重复。

你可以直接回复编号，例如：
1,3
或者：
{{PROJECT_TAG}}-YYYYMMDD-01 {{PROJECT_TAG}}-YYYYMMDD-03

我会下载对应 PDF，提取正文，并生成精读报告 PDF 附件。

[1] Title
Authors:
Venue:
Folder:
Source:
Summary:

Problem background:
Method:
Result:
Why relevant:

[2] ...


## Folder approval email

Subject:

`需要确认是否新建文献文件夹 - YYYY-MM-DD`

Body structure:


我发现以下文献不适合放入现有一级目录。

候选文献：

Title:
Authors:
Venue:
Reason:

建议新建文件夹：
XX_folder_name

请回复：
同意新建：yes folder_name
不同意：no，并指定应放入哪个现有文件夹


## Deep read email

Subject:

`文献精读报告 - Candidate ID - Short Title`

Body:


已完成以下文献的精读报告：

Title:
Authors:
Venue:
Folder:

附件中包含：

Markdown 渲染后的 PDF 精读报告

本地已更新：

downloaded_papers.md
reviewed_candidates.md
target folder README.md
extracted text folder
