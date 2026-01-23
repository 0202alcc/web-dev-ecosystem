import pytest

from app.services.auth_service import AuthService


class TestAuthService:
    """Tests for AuthService."""

    def test_generate_user_jwt_with_email(self):
        """Test JWT generation with email only."""
        token = AuthService.generate_user_jwt(user_email="test@example.com")

        assert token is not None
        assert isinstance(token, str)

    def test_generate_user_jwt_with_external_id(self):
        """Test JWT generation with external ID only."""
        token = AuthService.generate_user_jwt(user_external_id="usr_test123")

        assert token is not None
        assert isinstance(token, str)

    def test_generate_user_jwt_with_both(self):
        """Test JWT generation with both email and external ID."""
        token = AuthService.generate_user_jwt(
            user_email="test@example.com", user_external_id="usr_test123"
        )

        assert token is not None
        assert isinstance(token, str)

    def test_generate_user_jwt_without_params_raises_error(self):
        """Test JWT generation without parameters raises ValueError."""
        with pytest.raises(
            ValueError, match="Either user_email or user_external_id must be provided"
        ):
            AuthService.generate_user_jwt()

    def test_generate_bot_jwt(self):
        """Test bot JWT generation."""
        token = AuthService.generate_bot_jwt(bot_id="bot_001")

        assert token is not None
        assert isinstance(token, str)
