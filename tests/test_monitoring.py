import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.monitoring import system_monitor

client = TestClient(app)

def test_health_diagnostics_endpoint():
    res = client.get("/health/diagnostics")
    assert res.status_code == 200
    data = res.json()
    assert "status" in data
    assert "uptime_seconds" in data
    assert "components" in data
    assert "database" in data["components"]
    assert "ai_engine" in data["components"]
    assert "monetization" in data["components"]
    assert data["components"]["database"]["status"] == "operational"

def test_system_monitor_unit():
    diag = system_monitor.run_full_diagnostics()
    assert diag["app_name"] == "MindShift Coach"
    assert diag["version"] == "0.4.0"
    assert diag["uptime_seconds"] >= 0
