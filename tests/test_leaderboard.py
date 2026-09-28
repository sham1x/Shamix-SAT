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

def test_leaderboard_you_suffix_only_on_caller(client):
    # Register second user
    client.post("/api/auth/register", json={
        "username": "user2",
        "email": "user2@shamixprep.sat",
        "password": "Password123!",
        "display_name": "Second Student"
    })
    
    # Login as testdemo
    token1 = get_auth_token(client, username="testdemo", password="TestDemo123!")
    resp1 = client.get("/api/leaderboard?period=all_time", headers={"Authorization": f"Bearer {token1}"})
    data1 = resp1.json()

    demo_row_for_demo = next(s for s in data1["standings"] if s["isUser"])
    user2_row_for_demo = next(s for s in data1["standings"] if not s["isUser"])

    assert demo_row_for_demo["name"] == "Test Demo User (You)"
    assert user2_row_for_demo["name"] == "Second Student"

    # Login as user2
    token2 = get_auth_token(client, username="user2", password="Password123!")
    resp2 = client.get("/api/leaderboard?period=all_time", headers={"Authorization": f"Bearer {token2}"})
    data2 = resp2.json()

    demo_row_for_user2 = next(s for s in data2["standings"] if not s["isUser"])
    user2_row_for_user2 = next(s for s in data2["standings"] if s["isUser"])

    assert demo_row_for_user2["name"] == "Test Demo User"
    assert user2_row_for_user2["name"] == "Second Student (You)"
