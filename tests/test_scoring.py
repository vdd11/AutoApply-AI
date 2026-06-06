from autoapply_ai.scoring import score_job
from autoapply_ai.profile_store import DEFAULT_PROFILE

def test_score_good_job():
    job={'title':'Junior Data Analyst','description':'Python SQL pandas dashboard statistics','location':'Remote'}
    result=score_job(job, DEFAULT_PROFILE)
    assert result['match_score'] >= 60
    assert result['classification'] == 'Data/Analytics'

def test_score_bad_job():
    job={'title':'Sales Account Executive','description':'cold calling quota CRM','location':'Remote'}
    result=score_job(job, DEFAULT_PROFILE)
    assert result['priority'] == 'Reject'
