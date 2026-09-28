def get_auth_token(client, username="testdemo", password="TestDemo123!"):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]

def test_attendance_checkin_idempotency(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. First check-in of the day
    res1 = client.post("/api/attendance/check-in", headers=headers)
    assert res1.status_code == 200
    assert res1.json()["xp_reward"] == 50

    # 2. Second check-in on the same day -> idempotent (0 XP reward)
    res2 = client.post("/api/attendance/check-in", headers=headers)
    assert res2.status_code == 200
    assert res2.json()["xp_reward"] == 0
    assert "already checked in" in res2.json()["message"]
