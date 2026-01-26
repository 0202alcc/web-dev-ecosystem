"""Integration tests for server startup and push notifications."""

import json
import tempfile
from unittest.mock import patch

import pytest
import requests
from flask import Flask

from app import create_app


@pytest.fixture(scope="session")
def test_app():
    """Create and configure a Flask app for testing."""
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def test_client(test_app: Flask):
    """A test client for the app."""
    return test_app.test_client()


@pytest.fixture(scope="session")
def mock_subscription_data():
    """Load mock subscription data."""
    with open("tests/fixtures/mock_subscription.json") as f:
        return json.load(f)


class TestServerStartup:
    """Test basic server startup."""

    def test_app_creation(self, test_app: Flask):
        """Test that the Flask app can be created without errors."""
        assert test_app is not None
        assert isinstance(test_app, Flask)

    def test_health_endpoint(self, test_client):
        """Test the health endpoint responds."""
        response = test_client.get("/api/health")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "status" in data
        assert data["status"] == "healthy"


class TestPushNotification:
    """Test mocked push notification flow."""

    def test_send_bot_notification_mock_success(
        self, test_client, mock_subscription_data
    ):
        """Test sending a bot notification with mocked external success."""
        # Mock the external webpush call
        with patch("app.services.push_service.PushService.broadcast_notification") as mock_broadcast:
            # Pretend one user was successfully notified
            mock_broadcast.return_value = 1

            # Create test payload
            payload = {
                "title": "Test Notification",
                "content": "Test body",
            }

            # Make request (skip auth details for MVP smoke test)
            response = test_client.post(
                "/api/test-notification",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            # Basic success check - expect 200 or auth-related success
            assert response.status_code in [
                200,
                201,
            ]  # Allow for auth variations in MVP
