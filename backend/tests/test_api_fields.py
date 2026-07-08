def _register_and_login(client):
    client.post("/auth/register", json={"email": "farmer@example.com", "password": "secretpass123"})
    resp = client.post("/auth/login", data={"username": "farmer@example.com", "password": "secretpass123"})
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    resp = client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    assert resp.status_code == 201
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "password123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_rejects_wrong_password(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    resp = client.post("/auth/login", data={"username": "a@b.com", "password": "wrong"})
    assert resp.status_code == 401


def test_field_crud_requires_auth(client):
    resp = client.get("/fields")
    assert resp.status_code == 401


def test_create_and_list_field(client):
    headers = _register_and_login(client)
    resp = client.post(
        "/fields",
        headers=headers,
        json={
            "name": "North Plot",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "soil_type": "loam",
            "area_hectares": 2.5,
            "irrigation_method": "drip",
        },
    )
    assert resp.status_code == 201
    field_id = resp.json()["id"]

    resp = client.get("/fields", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["id"] == field_id


def test_create_field_rejects_invalid_soil_type(client):
    headers = _register_and_login(client)
    resp = client.post(
        "/fields",
        headers=headers,
        json={
            "name": "Bad Plot",
            "latitude": 28.6,
            "longitude": 77.2,
            "soil_type": "moon_dust",
            "area_hectares": 1.0,
        },
    )
    assert resp.status_code == 400


def test_fields_are_isolated_per_user(client):
    headers_a = _register_and_login(client)
    client.post(
        "/fields",
        headers=headers_a,
        json={"name": "A's Field", "latitude": 1, "longitude": 1, "soil_type": "clay", "area_hectares": 1},
    )

    client.post("/auth/register", json={"email": "b@example.com", "password": "password123"})
    login_b = client.post("/auth/login", data={"username": "b@example.com", "password": "password123"})
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    resp = client.get("/fields", headers=headers_b)
    assert resp.status_code == 200
    assert resp.json() == []


def test_list_crops_seeded(client):
    headers = _register_and_login(client)
    resp = client.get("/crops", headers=headers)
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert len(names) >= 8
    assert "Maize (grain)" in names


def test_recommendation_requires_active_crop(client):
    headers = _register_and_login(client)
    resp = client.post(
        "/fields",
        headers=headers,
        json={"name": "No Crop Field", "latitude": 28.6, "longitude": 77.2, "soil_type": "loam", "area_hectares": 1},
    )
    field_id = resp.json()["id"]
    resp = client.get(f"/fields/{field_id}/recommendation", headers=headers)
    assert resp.status_code == 400
