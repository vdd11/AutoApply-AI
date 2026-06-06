from autoapply_ai.filters import passes_user_filters, parse_salary_floor
from autoapply_ai.resume_sections import extract_sections
from autoapply_ai.quality import job_quality_score
from autoapply_ai.embeddings import semantic_similarity


def test_salary_floor_parser():
    assert parse_salary_floor('$70,000 - $95,000') == 70000


def test_filters_block_unwanted_company():
    ok, reasons = passes_user_filters({'company':'BadCo','title':'Data Analyst','location':'Remote','description':'Python SQL'}, blocked_companies=['BadCo'])
    assert not ok
    assert 'Blocked company' in reasons


def test_resume_sections_extracts_skills():
    sections = extract_sections('Summary\nAnalyst\nSkills\nPython SQL\nExperience\nResearch')
    assert 'skills' in sections and 'Python' in sections['skills']


def test_job_quality_penalizes_missing_url():
    out = job_quality_score({'title':'Data Analyst','company':'X','description':'short','url':''})
    assert out['job_quality_score'] < 70


def test_semantic_similarity_fallback_returns_float():
    score, method = semantic_similarity('python sql data analyst', 'data analyst using python and sql')
    assert 0 <= score <= 1
    assert method
