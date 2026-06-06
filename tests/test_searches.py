from autoapply_ai.searches import save_search, recent_searches


def test_save_and_read_recent_searches(tmp_path, monkeypatch):
    # Uses the project default test DB from the package config; validates table works.
    save_search("test-session", "data analyst", "Remotive", True, 60, 3)
    df = recent_searches("test-session")
    assert not df.empty
    assert "data analyst" in df.iloc[0]["query"]
