# Topic Queue

The daily search must follow the active topic and active subtopic in:

`00_registry/search_state.md`

Do not search all topics at once.

## Main topic order

{{#each TOPICS}}
{{@index_1}}. {{this.display_name}}
{{/each}}

## Auto-rotation rule

Automatically switch to the next topic if either condition is met:

1. The current topic has {{ROTATION_DOWNLOAD_THRESHOLD}} downloaded papers.
2. The current topic has fewer than {{ROTATION_LOW_YIELD_THRESHOLD}} high-quality new candidates for {{ROTATION_LOW_YIELD_RUNS}} consecutive daily runs.

## Same-day fallback rule

The daily target is up to {{DAILY_PAPER_COUNT}} papers.

First search the active topic.

If the active topic produces fewer than {{DAILY_PAPER_COUNT}} good candidates:

1. Do not add weak papers just to fill the quota.
2. Try the next subtopic within the same main topic.
3. If still fewer than 3 good candidates, search the next main topic as fallback.
4. Clearly mark fallback-topic papers in the daily email.

Example:

- Papers 1-3: {{TOPICS.[0].display_name}}
- Papers 4-5: {{TOPICS.[1].display_name}} fallback

## Manual override

If the user manually changes `active_topic` or `active_subtopic` in `00_registry/search_state.md`, follow the user-defined value.

Do not override it unless rotation conditions are met again.

## Subtopic order per topic

{{#each TOPICS}}
### {{this.display_name}}

{{#each this.subtopics}}
{{@index_1}}. {{this}}
{{/each}}

{{/each}}

## Output

Every daily run should return up to {{DAILY_PAPER_COUNT}} papers.

Quality is more important than quantity.

If fewer than {{DAILY_PAPER_COUNT}} good papers are found, report fewer papers and explain why.

After each daily run, update:

- candidate_sent_count
- consecutive_low_yield_runs

After each successful download, update:

- downloaded_count
