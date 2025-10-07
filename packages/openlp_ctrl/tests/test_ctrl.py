"""
Test for openlp_ctrl
"""

from fastapi.testclient import TestClient
from openlp_ctrl.server import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "connected_clients" in data


def test_status_endpoint():
    """Test the status endpoint"""
    response = client.get("/status")
    assert response.status_code == 200
    data = response.json()
    assert "connected_clients" in data
    assert "total_connections" in data


def test_set_slide_endpoint():
    """Test the set-slide endpoint"""
    response = client.post("/set-slide", json={"id": "slide-123"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "slide_id" in data
    assert data["slide_id"] == "slide-123"
