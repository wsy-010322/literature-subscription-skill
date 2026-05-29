# Search State

## Active topic

active_topic: {{ACTIVE_TOPIC}}

## Active subtopic

active_subtopic: {{ACTIVE_SUBTOPIC}}

## Auto rotation

auto_rotation: true

## Rotation rule

Switch to the next main topic if either condition is met:

1. The current topic has {{ROTATION_DOWNLOAD_THRESHOLD}} downloaded papers.
2. The current topic has fewer than {{ROTATION_LOW_YIELD_THRESHOLD}} high-quality new candidates for {{ROTATION_LOW_YIELD_RUNS}} consecutive daily runs.

## Topic priority queue

{{#each TOPICS}}
{{@index_1}}. {{this.folder_name}}
{{/each}}

## Topic counters

{{#each TOPICS}}
### {{this.folder_name}}

downloaded_count: 0
consecutive_low_yield_runs: 0
candidate_sent_count: 0

{{/each}}

## Subtopic queues

{{#each TOPICS}}
### {{this.folder_name}} subtopic queue

{{#each this.subtopics}}
{{@index_1}}. {{this.folder_name}}_{{this}}
{{/each}}

{{/each}}
