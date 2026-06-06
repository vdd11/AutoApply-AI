from autoapply_ai.tailoring import ats_keyword_coverage, tailored_resume_bullets, interview_questions
from autoapply_ai.models import ResumeProfile


def test_ats_keyword_coverage_detects_present_and_missing_terms():
    result = ats_keyword_coverage("Python SQL Tableau statistics", "Python and SQL", "Python, SQL")
    assert result["coverage"] > 0
    assert "Python" in result["present"]
    assert any(x.lower() == "tableau" for x in result["missing"])


def test_tailored_resume_bullets_returns_copy_ready_items():
    profile = ResumeProfile(session_id="u", skills="Python, SQL", raw_text="Python SQL analytics")
    job = {"title":"Data Analyst", "company":"Acme", "description":"Python SQL dashboards"}
    bullets = tailored_resume_bullets(job, profile)
    assert len(bullets) >= 3
    assert all(isinstance(b, str) and len(b) > 20 for b in bullets)


def test_interview_questions_are_role_specific():
    qs = interview_questions({"title":"Data Analyst", "company":"Acme"})
    assert any("Data Analyst" in q for q in qs)
