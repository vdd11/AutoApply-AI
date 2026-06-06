from .config import OUTPUT_DIR
from .database import connect, init_db
PACKET_DIR=OUTPUT_DIR/"prep_packets"
def make_prep_packet(job: dict, profile) -> str:
    missing=job.get('missing_skills','') or 'None obvious from the posting.'
    return f"""# Apply Prep Packet: {job.get('title')} at {job.get('company')}

## Match Summary
Match Score: {job.get('match_score')}%\nPriority: {job.get('priority')}\nClassification: {job.get('classification')}

## Why this role matches
{job.get('why_match')}

## Skills to emphasize
{profile.skills}

## Missing or weaker skills
{missing}

## Tailored resume bullet ideas
- Applied Python, statistics, and data visualization to analyze quantitative datasets and communicate actionable insights.
- Built data-focused projects using Pandas, NumPy, machine learning, and dashboard tools to solve real-world analytics problems.
- Translated technical findings into clear recommendations for non-technical stakeholders through teaching, research, and analytics experience.

## Cover letter draft
Dear Hiring Manager,

I am excited to apply for the {job.get('title')} position at {job.get('company')}. My background in Python-based analysis, statistics, research, and data-focused project work aligns strongly with this role.

Sincerely,\n{profile.name}

## Interview prep questions
1. Tell me about a project where you analyzed messy data.
2. How would you explain a technical result to a non-technical stakeholder?
3. What SQL/Python techniques would you use to validate a dataset?
4. How would you measure whether your analysis created impact?

## Apply link
{job.get('url')}
"""
def save_prep_packet(job: dict, profile):
    PACKET_DIR.mkdir(parents=True,exist_ok=True); content=make_prep_packet(job,profile); path=PACKET_DIR/f"prep_packet_{job.get('id')}_{str(job.get('company','company')).replace(' ','_')}.md"; path.write_text(content,encoding='utf-8')
    init_db(); conn=connect(); conn.execute("""INSERT INTO prep_packets(job_id,session_id,content) VALUES(?,?,?) ON CONFLICT(job_id,session_id) DO UPDATE SET content=excluded.content, created_at=CURRENT_TIMESTAMP""",(int(job.get('id')),profile.session_id,content)); conn.commit(); conn.close(); return path
