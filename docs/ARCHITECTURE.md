# Architecture

```text
Resume Upload
    ↓
Resume Parser + Section Extractor
    ↓
Profile Store
    ↓
Job Sources / Careers Crawler
    ↓
Relevance Filter
    ↓
Semantic + Keyword + Quality Scoring
    ↓
Ranked Job Matches
    ↓
Dashboard Cards / Apply Links / Prep Packets
    ↓
Application Tracker + Alerts
```

## Database Tables

- `users`
- `resumes`
- `jobs`
- `job_scores`
- `applications`
- `prep_packets`
- `saved_searches`
- `job_events`
- `alerts`

## Matching Formula

The score combines:

- title match
- semantic similarity
- keyword overlap
- classification strength
- remote/location signal
- risk penalty
- job quality score

The system intentionally hides unrelated or high-risk results by default.
