from fastapi.testclient import TestClient

from stripe2qbo.api.app import app

client = TestClient(app)


def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_user_id():
    response = client.get("/userId")
    assert response.status_code == 401
    assert response.text is not None

def test_logout():
    response = client.post("/logout")
    assert response.status_code == 200

def test_get_settings():
    response = client.get("/settings")
    assert response.status_code == 401

def test_save_settings():
    response = client.post("/settings")
    assert response.status_code == 401

def test_sync_single_transaction():
    response = client.post("/sync")
    assert response.status_code == 401

