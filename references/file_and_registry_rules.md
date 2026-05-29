# File and Registry Rules

## Registry files

Use these files as persistent memory.

### reviewed_candidates.md

Record every searched and selected candidate paper here, even if not downloaded.

Required columns:

| Date | Candidate ID | Title | Authors | Venue | Year | Folder | Status | Source URL | Notes |

Status options:

- candidate_sent
- skipped_duplicate
- rejected_low_relevance
- venue_uncertain
- pending_folder_approval
- selected_for_download
- downloaded
- deep_read_sent

### downloaded_papers.md

Record every downloaded PDF here.

Required columns:

| Date | Candidate ID | Title | Folder | PDF Path | Text Path | Deep Report Path | Source URL |

### pending_folder_approvals.md

Record papers that need a new folder.

Required columns:

| Date | Candidate ID | Title | Suggested Folder | Reason | Source URL | Status |

## Duplicate prevention

Before adding a candidate:

1. Normalize title by lowercasing and removing punctuation.
2. Check `reviewed_candidates.md`.
3. Check `downloaded_papers.md`.
4. If the title or DOI already exists, skip it unless there is a clear reason to update metadata.

## File naming

Use this filename pattern:

`YYYY-MM-DD - Short Sanitized Title.pdf`

For extracted text:

`10_extracted_text/YYYY-MM-DD - Short Sanitized Title.txt`

For deep read markdown:

`11_deep_read_reports/YYYY-MM-DD - Short Sanitized Title - deep_read.md`

For deep read PDF:

`11_deep_read_reports/YYYY-MM-DD - Short Sanitized Title - deep_read.pdf`

## Folder README update

When a paper is accepted as a candidate, update the target folder `README.md` with a short entry.

Each entry should include:

- title
- authors
- venue
- year
- local PDF link if downloaded, otherwise source URL
- **brief content summary** (2-3 sentences in Chinese: what problem the paper solves, main method, key result)
- **user notes** (a placeholder `<!-- user_notes: -->` field where the user can later add their own remarks)

Example format:

```markdown
### 2026-05-29

1. **LLM-20260529-01** — Paper Title
   - Authors et al. (2026) — Venue
   - 本文研究了 XXX 问题，提出了 YYY 方法，实现了 ZZZ 结果。
   - [arXiv](https://arxiv.org/abs/xxxx.xxxxx)
   - 本地PDF：`YYYY-MM-DD - Short Title.pdf`
   - <!-- user_notes:  -->
```

The content summary should be written in Chinese and kept concise (2-3 sentences). It should help the user quickly recall what each paper is about without re-reading the abstract. The `<!-- user_notes: -->` HTML comment is invisible when rendered but editable by the user to add personal remarks.

Do not make very long summaries in folder README files.
Detailed summaries belong in daily reports or deep read reports.
