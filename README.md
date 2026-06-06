# AutoApply AI Pro — Resume-to-Job Matching Platform

A deployable Streamlit application that lets a user create a profile, upload a resume, fetch live job postings, rank the postings against the user's skills, and apply on the original job website.

This is intentionally **review-first**. It does not mass-submit applications or fill forms without user approval. The app helps a candidate find stronger-fit roles faster and prepare better application materials.

## Core Workflow

1. Create or load a candidate profile
2. Upload a PDF/TXT resume
3. Extract skills and resume sections
4. Fetch jobs from public sources and optional careers pages
5. Filter out unrelated roles
6. Score and rank jobs by match strength
7. Review job cards, risks, missing skills, and ATS coverage
8. Click **Apply on Website** to open the original posting
9. Track Viewed, Applied, Interview, Rejected, and follow-up status
10. Download a job-specific prep packet

## Quick Start

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

CLI demo:

```bash
python main.py quickstart
python main.py top --limit 10
```

## Deploy on Streamlit Cloud

1. Push this repo to GitHub.
2. Go to Streamlit Cloud.
3. Choose the repo.
4. Set app file to `app.py`.
5. Deploy.

The app uses SQLite by default for local/demo deployment. For production multi-user deployment, connect the storage layer to PostgreSQL using the schema in `autoapply_ai/database.py`.

## Portfolio Positioning

**AutoApply AI Pro** is an end-to-end AI/data product demonstrating:

- Python software engineering
- Data ingestion from APIs and web pages
- Resume parsing and NLP-style feature extraction
- Recommendation/ranking systems
- Data cleaning and normalization
- Streamlit dashboard development
- SQLite database design
- Application analytics
- Testing, Docker, CI/CD, and deployment readiness

## Ethical Design

This project does not auto-submit applications. It sends users to the official job posting so they can review and apply manually.
"# AutoApply-AI" 
