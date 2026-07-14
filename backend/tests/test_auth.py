def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "full_name": "Test Student",
        "email": "student1@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "academic_level": "Undergraduate",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "student1@example.com"
    assert "access_token" in data


def test_register_duplicate_email_fails(client):
    payload = {
        "full_name": "Test Student Two",
        "email": "student2@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "academic_level": "Undergraduate",
    }
    first = client.post("/api/auth/register", json=payload)
    assert first.status_code == 201

    second = client.post("/api/auth/register", json=payload)
    assert second.status_code == 409


def test_register_password_mismatch_fails(client):
    response = client.post("/api/auth/register", json={
        "full_name": "Test Student Three",
        "email": "student3@example.com",
        "password": "Password123",
        "confirm_password": "Different123",
        "academic_level": "Undergraduate",
    })
    assert response.status_code == 422


def test_register_weak_password_fails(client):
    response = client.post("/api/auth/register", json={
        "full_name": "Test Student Four",
        "email": "student4@example.com",
        "password": "weak",
        "confirm_password": "weak",
        "academic_level": "Undergraduate",
    })
    assert response.status_code == 422


def test_login_success_and_failure(client):
    client.post("/api/auth/register", json={
        "full_name": "Login User",
        "email": "loginuser@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "academic_level": "Self Learner",
    })

    good = client.post("/api/auth/login", json={"email": "loginuser@example.com", "password": "Password123"})
    assert good.status_code == 200
    assert "access_token" in good.json()

    bad = client.post("/api/auth/login", json={"email": "loginuser@example.com", "password": "WrongPassword"})
    assert bad.status_code == 401


def test_protected_route_requires_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_protected_route_with_token(client):
    register = client.post("/api/auth/register", json={
        "full_name": "Protected User",
        "email": "protected@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
        "academic_level": "Educator",
    })
    token = register.json()["access_token"]
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "protected@example.com"
