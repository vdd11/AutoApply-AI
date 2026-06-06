from autoapply_ai.job_sources import clean_html, is_reasonably_relevant
from autoapply_ai.models import Job


def test_clean_html_removes_tags():
    assert clean_html('<p>Hello&nbsp;<b>World</b></p>') == 'Hello World'


def test_relevant_data_job_passes_strict_filter():
    job = Job('1','Junior Data Analyst','Acme','Remote','Test','https://example.com','Python SQL dashboards analytics')
    assert is_reasonably_relevant(job, strict=True)


def test_sales_job_blocked():
    job = Job('2','Sales Account Executive','Acme','Remote','Test','https://example.com','analytics platform customer outreach')
    assert not is_reasonably_relevant(job, strict=True)
