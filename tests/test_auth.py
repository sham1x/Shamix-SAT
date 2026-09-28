def test_register_and_login_flow(client):
    # 1. Register new user
    reg_resp = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@shamixprep.sat",
        "password": "Password123!",
        "display_name": "New User"
    })
    assert reg_resp.status_code == 201
    reg_data = reg_resp.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == "newuser"

    # 2. Login with registered user
    login_resp = client.post("/api/auth/login", json={
        "username": "newuser",
        "password": "Password123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]

    # 3. Test /api/auth/me with valid token
    me_resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_resp.status_code == 200
    assert me_resp.json()["username"] == "newuser"

def test_register_short_password(client):
    resp = client.post("/api/auth/register", json={
        "username": "shortpwuser",
        "email": "shortpw@shamixprep.sat",
        "password": "pass" # < 8 chars
    })
    assert resp.status_code == 422 or resp.status_code == 400

def test_register_password_complexity_rules(client):
    # 1. Reject missing uppercase first letter
    resp1 = client.post("/api/auth/register", json={
        "username": "user1", "email": "user1@shamixprep.sat", "password": "password123!"
    })
    assert resp1.status_code in [400, 422]

    # 2. Reject missing digit/number
    resp2 = client.post("/api/auth/register", json={
        "username": "user2", "email": "user2@shamixprep.sat", "password": "Password!"
    })
    assert resp2.status_code in [400, 422]

    # 3. Reject missing special character/symbol
    resp3 = client.post("/api/auth/register", json={
        "username": "user3", "email": "user3@shamixprep.sat", "password": "Password123"
    })
    assert resp3.status_code in [400, 422]

def test_login_wrong_password(client):
    resp = client.post("/api/auth/login", json={
        "username": "testdemo",
        "password": "WrongPassword123!"
    })
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid username or password"

def test_protected_endpoint_without_token(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Not authenticated"

def test_rate_limiting_returns_429(client):
    # Make 20 login attempts
    for i in range(20):
        client.post("/api/auth/login", json={"username": f"rluser_{i}", "password": "WrongPassword123!"})
    
    # 21st attempt must be blocked with HTTP 429
    resp = client.post("/api/auth/login", json={"username": "rluser_21", "password": "WrongPassword123!"})
    assert resp.status_code == 429
    assert "Too many attempts" in resp.json()["detail"]
