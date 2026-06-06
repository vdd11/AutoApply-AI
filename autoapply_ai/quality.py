from __future__ import annotations

def job_quality_score(job: dict) -> dict:
    text=f"{job.get('title','')} {job.get('company','')} {job.get('description','')} {job.get('salary','')}".lower()
    score=70; flags=[]
    if len(job.get('description','')) < 250: score-=15; flags.append('Very short job description')
    if not job.get('url'): score-=30; flags.append('Missing apply URL')
    if any(x in text for x in ['unpaid','volunteer','commission only']): score-=40; flags.append('Weak compensation signal')
    if any(x in text for x in ['senior','principal','staff','director','10+ years','8+ years']): score-=20; flags.append('Likely too senior')
    if any(x in text for x in ['visa sponsorship not available','must relocate']): score-=10; flags.append('Constraint warning')
    if any(x in text for x in ['sql','python','analytics','data','dashboard','statistics']): score+=10
    return {'job_quality_score': max(0,min(100,score)), 'quality_flags': ', '.join(flags)}
