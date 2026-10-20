from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_rejects_nonpositive_amount():
    response = client.post("/transactions", json={
        "title": "Lunch", "amount": 0, "category": "Food",
        "kind": "expense", "transaction_date": "2026-01-01"
    })
    assert response.status_code == 422
