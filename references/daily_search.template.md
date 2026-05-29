# Daily Literature Search Task

Goal: search for {{DAILY_PAPER_COUNT}} relevant papers in {{RESEARCH_DOMAIN}} and email the user a detailed daily summary.

## Search scope

Search papers related to:

{{#each SEARCH_KEYWORDS}}
- {{this}}
{{/each}}

## Daily target

Find {{DAILY_PAPER_COUNT}} papers per day from a candidate pool of ~15 papers.

Prioritize:

1. Papers from Tier S journals and high-impact-factor venues.
2. Papers from Tier A journals.
3. High-citation papers (classic/landmark works preferred over newer but low-impact ones).
4. Recent arXiv papers within the last 2 years if highly relevant and well-cited.
5. Papers close to the user's interests:
{{#each USER_INTERESTS}}
   - {{this}}
{{/each}}

**Default filtering strategy** (tell the user during setup): papers from higher-tier journals and with higher impact factors are prioritized. Freshness alone is not enough — a new preprint without citations from an unknown venue should not displace a highly-cited Nature/NeurIPS paper from 2-3 years ago.

## Required metadata

For each paper, verify:

- title
- authors
- year
- venue or arXiv status
- DOI or arXiv URL if available
- abstract
- PDF URL if available
- target folder

## Summary requirements

For each paper, write a detailed Chinese summary containing:

1. Problem background
2. What problem the paper tries to solve
3. Main method
4. Main result
5. Why it may be useful to the user
6. Suggested folder

## Output files

Create a daily markdown report:

`08_daily_reports/{{PROJECT_TAG}}_daily_summary_YYYY-MM-DD.md`

If possible, also render it to:

`08_daily_reports/{{PROJECT_TAG}}_daily_summary_YYYY-MM-DD.pdf`

Update:

- `00_registry/reviewed_candidates.md`
- target folder `README.md`

## Email

Send the user an email with the daily summary.

The email must include numbered candidate IDs:

- {{PROJECT_TAG}}-YYYYMMDD-01
- {{PROJECT_TAG}}-YYYYMMDD-02
- ...

Tell the user they can reply with the IDs or numbers to request deep reading.

Example:

"回复 `1,3,5` 或 `{{PROJECT_TAG}}-YYYYMMDD-01 {{PROJECT_TAG}}-YYYYMMDD-03`，我会下载 PDF 并发送精读报告。"
