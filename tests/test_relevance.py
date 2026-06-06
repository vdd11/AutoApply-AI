from autoapply_ai.relevance import classify_job

def test_data_role_allowed():
    c, _ = classify_job('Junior Data Analyst', 'Python SQL dashboards')
    assert c == 'Data/Analytics'

def test_sales_rejected():
    c, _ = classify_job('Sales Account Executive', 'CRM pipeline')
    assert c == 'Unrelated'
