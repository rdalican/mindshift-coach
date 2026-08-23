import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_stripe_checkout_endpoint():
    payload = {
        "sync_key": "MIND-STRIPE-001",
        "email": "user@example.com"
    }
    response = client.post("/api/payments/checkout", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "checkout_url" in data
    assert "session_id" in data

def test_stripe_plan_status_endpoint():
    response = client.get("/api/payments/status/MIND-STRIPE-001")
    assert response.status_code == 200
    data = response.json()
    assert "plan_status" in data
    assert data["sync_key"] == "MIND-STRIPE-001"
