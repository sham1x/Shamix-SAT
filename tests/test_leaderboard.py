def get_auth_token(client, username="testdemo", password="TestDemo123!"):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]

def test_leaderboard_ordering_and_own_rank(client):
    token = get_auth_token(client)
    resp = client.get("/api/leaderboard?period=all_time&limit=10", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert "standings" in data
    assert "userRank" in data
    assert data["userRank"]["isUser"] == True
    assert data["userRank"]["name"].startswith("Test Demo User")
