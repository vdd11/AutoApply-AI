# v9 Upgrade Summary

## Product Upgrades

- Added session-safe user identity layer.
- Added profile-first workflow for public deployments.
- Added stricter user filters for remote, US-friendly, employment type, salary, blocked companies, and whitelisted companies.
- Added saved alerts table for future scheduled notifications.
- Added apply-click tracking and status management.
- Added job quality score and quality flags.

## Matching Upgrades

- Added semantic matching wrapper that uses SentenceTransformers when installed.
- Added TF-IDF fallback for lightweight deployment.
- Added job-quality component to ranking.
- Added better missing-skill analysis and market skill coverage.
- Added resume section extraction for better future tailoring.

## Deployment Upgrades

- Dark-mode Streamlit app.
- Streamlit Cloud-ready structure.
- SQLite default persistence.
- Docker support.
- GitHub Actions tests.
- 17 passing tests.

## Recommended Future Production Extension

For a true SaaS deployment, migrate SQLite to PostgreSQL, connect alert rows to a scheduler, and add email delivery through a provider such as SendGrid or Resend.
