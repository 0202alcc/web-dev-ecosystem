import time

import pytest
import time

from app import create_app


@pytest.fixture
def app():
    """Create and configure a test app."""
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


class TestAPIEndpoints:
    """Tests for API endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/api/health")
        assert response.status_code == 200

        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "flask-webpush"

    def test_generate_jwt_with_email(self, client):
        """Test JWT generation with email."""
        response = client.get("/api/jwt?user_email=test@example.com")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "token" in data

    def test_generate_jwt_with_external_id(self, client):
        """Test JWT generation with external ID."""
        response = client.get("/api/jwt?user_external_id=usr_test123")
        assert response.status_code == 200

        data = response.get_json()
        assert data["success"] is True
        assert "token" in data

    def test_generate_jwt_without_params(self, client):
        """Test JWT generation without parameters."""
        response = client.get("/api/jwt")
        assert response.status_code == 400

        data = response.get_json()
        assert data["success"] is False

    def test_send_notification_unauthorized_ip(self, client):
        """Test sending notification with unauthorized IP returns 403."""
        data = {
            "bot_id": "bot_001",
            "title": "Test Notification",
            "content": "Test message",
            "timestamp": int(time.time() * 1000),
        }

        # Set invalid IP in test client
        client.environ_base = {"REMOTE_ADDR": "192.168.1.1"}

        response = client.post("/api/send-notification", json=data)

        assert response.status_code == 403

        data = response.get_json()
        assert data["success"] is False
        assert "error" in data
