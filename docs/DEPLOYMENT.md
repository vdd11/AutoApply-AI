# Deployment Guide

## Local

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

## Streamlit Community Cloud

1. Push this repository to GitHub.
2. Open Streamlit Community Cloud.
3. Create a new app from the GitHub repo.
4. Set the app file to `app.py`.
5. Deploy.

The app includes `.streamlit/config.toml` with a dark theme.

## Docker

```bash
docker build -t autoapply-ai-pro .
docker run -p 8501:8501 autoapply-ai-pro
```

Then open `http://localhost:8501`.

## Notes

- The app uses SQLite by default for simplicity.
- Public job APIs can occasionally time out or return noisy results. The app handles failures gracefully and includes demo data for interviews.
- The apply button uses `st.link_button`, which opens the real external URL when the job posting includes a valid HTTP/HTTPS link.
