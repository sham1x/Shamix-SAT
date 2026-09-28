def get_auth_token(client, username="testdemo", password="TestDemo123!"):
    resp = client.post("/api/auth/login", json={"username": username, "password": password})
    return resp.json()["access_token"]

def test_homework_question_privacy(client):
    token = get_auth_token(client)
    resp = client.get("/api/homework/testhw-1", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    hw_data = resp.json()
    assert len(hw_data["questions"]) > 0
    q = hw_data["questions"][0]
    
    # CRITICAL: Verify correct_index and explanation are NOT returned in GET!
    assert "correct_index" not in q
    assert "explanation" not in q

def test_homework_start_answer_submit_flow(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Start attempt
    start_resp = client.post("/api/homework/testhw-1/start", headers=headers)
    assert start_resp.status_code == 200
    assert start_resp.json()["status"] == "in_progress"

    # 2. Answer question (q_id=1, selected_index=1)
    ans_resp = client.post("/api/homework/testhw-1/answer?question_id=1", json={"selected_index": 1}, headers=headers)
    assert ans_resp.status_code == 200

    # 3. Submit attempt
    submit_resp = client.post("/api/homework/testhw-1/submit", headers=headers)
    assert submit_resp.status_code == 200
    sub_data = submit_resp.json()
    assert sub_data["status"] == "completed"
    assert sub_data["score"] == "100%"
    assert sub_data["xp_rewarded"] == 150
    assert len(sub_data["results"]) == 1
    assert sub_data["results"][0]["is_correct"] == True
    assert "explanation" in sub_data["results"][0]

def test_no_double_xp_on_repeated_homework_submit(client):
    token = get_auth_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    client.post("/api/homework/testhw-1/start", headers=headers)
    client.post("/api/homework/testhw-1/answer?question_id=1", json={"selected_index": 1}, headers=headers)

    # First submit -> awards XP
    resp1 = client.post("/api/homework/testhw-1/submit", headers=headers)
    assert resp1.status_code == 200

    # Repeated submit -> 0 XP rewarded (idempotent)
    resp2 = client.post("/api/homework/testhw-1/submit", headers=headers)
    assert resp2.status_code == 200
    assert resp2.json()["xp_rewarded"] == 0
