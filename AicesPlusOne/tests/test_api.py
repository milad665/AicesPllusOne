import pytest
from fastapi.testclient import TestClient
from aices_plus_one.api import app


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Git Repository Manager"
    assert "endpoints" in data


def test_get_repositories_empty(client):
    """Test getting repositories when none are configured"""
    response = client.get("/repositories")
    assert response.status_code == 200
    assert response.json() == []


def test_get_projects_empty(client):
    """Test getting projects when none are available"""
    response = client.get("/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_add_repository_invalid_data(client):
    """Test adding a repository with invalid data"""
    invalid_repo = {
        "name": "",  # Empty name should be invalid
        "url": "not-a-valid-url",
        "ssh_private_key": "fake-key",
        "ssh_public_key": "fake-key",
        "default_branch": "main"
    }
    
    response = client.post("/repositories", json=invalid_repo)
    # Should fail with validation error
    assert response.status_code == 422


def test_sync_repositories(client):
    """Test triggering repository synchronization"""
    response = client.post("/repositories/sync")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
