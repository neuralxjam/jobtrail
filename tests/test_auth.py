def test_login_page_loads(anon_client):
    r = anon_client.get("/login")
    assert r.status_code == 200
    assert "magic link" in r.text.lower()


def test_unauthenticated_root_redirects(anon_client):
    r = anon_client.get("/")
    assert r.status_code in (302, 307)
    assert "/login" in r.headers["location"]


def test_unauthenticated_dashboard_redirects(anon_client):
    r = anon_client.get("/dashboard")
    assert r.status_code in (302, 307)
    assert "/login" in r.headers["location"]
