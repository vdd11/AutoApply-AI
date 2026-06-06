# Interview Talk Track

I built AutoApply AI Pro as a job intelligence platform rather than an auto-application bot. The app follows a review-first workflow: a user creates a profile, uploads a resume, fetches public job postings, and receives ranked job recommendations with reasons, missing skills, risk flags, and external apply links.

Technical highlights:

- Streamlit frontend with dark-mode UX
- SQLite normalized storage layer
- Resume parsing for PDF/TXT files
- Public API ingestion from Remotive, Arbeitnow, and RemoteOK
- Job normalization and deduplication
- Relevance filtering to remove unrelated roles
- Resume-job scoring with TF-IDF similarity, keyword matching, title relevance, and risk penalties
- Application status tracking
- Market skill analytics and learning roadmap
- Tests, Docker, and GitHub Actions

I designed the project to demonstrate data science, NLP-style text matching, product thinking, dashboarding, and software engineering practices.
