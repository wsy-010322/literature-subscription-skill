# Journal Filter

Only prioritize papers from the following venues, unless the paper is a recent arXiv preprint within the last 2 years and is highly relevant.

## Tier S

{{#each JOURNAL_TIER_S}}
- {{this}}
{{/each}}

## Tier A

{{#each JOURNAL_TIER_A}}
- {{this}}
{{/each}}

## arXiv rule

- If the paper appeared within the last 2 years, the arXiv version may be used for reading.
- If the paper is older than 2 years, only include it if it has been published in one of the whitelisted venues.
- For every paper, verify the venue using reliable metadata such as DOI, publisher page, Crossref, Semantic Scholar, OpenAlex, journal page, or arXiv journal-ref.
- Do not invent venue information.
- If the venue is uncertain, mark it as `venue_uncertain` and lower priority.
