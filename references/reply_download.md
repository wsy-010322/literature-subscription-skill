# Email Reply Download Task

Goal: when the user replies to a daily literature email with paper numbers or candidate IDs, download the selected papers and generate deep read reports.

## Input

The user may reply with:

- `1`
- `1,3,5`
- `{{PROJECT_TAG}}-YYYYMMDD-01`
- `download 1 2`
- Chinese text containing numbers, such as `下载第1和第3篇`

## Steps

1. Parse selected candidate IDs.
2. Find the corresponding entries in `00_registry/reviewed_candidates.md`.
3. Check `00_registry/downloaded_papers.md`.
4. If already downloaded, do not download again. Use the existing PDF.
5. If not downloaded, download the PDF from the verified source.
6. Save the PDF into the routed folder.
7. Extract full text into `10_extracted_text/`.
8. Generate a detailed markdown deep read report using `00_prompts/deep_read_report.md`.
9. Render the markdown report into PDF.
10. Email the PDF report to the user as an attachment.
11. Update:
    - `00_registry/reviewed_candidates.md`
    - `00_registry/downloaded_papers.md`
    - target folder `README.md`

## Important

Do not create a new folder unless the user has approved it.

If a selected paper has `pending_folder_approval` status, email the user for folder approval first.
