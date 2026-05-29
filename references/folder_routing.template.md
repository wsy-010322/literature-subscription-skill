# Folder Routing Rules

## Global routing table

| Topic / paper type | Primary folder | Notes |
|---|---|---|
{{#each TOPICS}}
| {{this.display_name}} / {{this.keywords}} | `{{this.folder_name}}` | Default for {{this.display_name}}-related work |
{{/each}}
| Daily reports | `08_daily_reports` | Keep only active reports if used |
| Weekly reports | `09_weekly_reports` | Keep only active reports if used |
| Extracted text | `10_extracted_text` | Text only, no PDFs |
| Deep read reports | `11_deep_read_reports` | Markdown reports only |
| Old agent artifacts | `99_archive` | Archived prompts, registries, and old daily reports |

## Routing principles

1. Route each paper to exactly one primary folder.
2. Keep PDFs in place; do not move PDFs unless explicitly instructed.
3. Put extracted text in `10_extracted_text`.
4. Put deep-read reports in `11_deep_read_reports`.
5. If a paper does not fit cleanly, record it in `00_registry/pending_folder_approvals.md`.
