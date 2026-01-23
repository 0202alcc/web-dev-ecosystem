import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from app.config import Config


class AuthService:
    """Service for JWT generation and validation."""

    @staticmethod
    def generate_user_jwt(
        user_email: Optional[str] = None, user_external_id: Optional[str] = None
    ) -> str:
        """Generate User JWT for MagicBell authentication.

        Args:
            user_email: User's email address
            user_external_id: User's external ID from your system

        Returns:
            JWT token string

        Raises:
            ValueError: If neither user_email nor user_external_id is provided
        """
        if not user_email and not user_external_id:
            raise ValueError("Either user_email or user_external_id must be provided")

        payload: Dict[str, Any] = {
            "api_key": Config.MAGICBELL_API_KEY,
        }

        if user_email:
            payload["user_email"] = user_email
        if user_external_id:
            payload["user_external_id"] = user_external_id

        return jwt.encode(
            payload,
            Config.MAGICBELL_API_SECRET,
            algorithm="HS256",
        )

    @staticmethod
    def generate_bot_jwt(bot_id: str) -> str:
        """Generate JWT for bot authentication.

        Args:
            bot_id: Bot identifier

        Returns:
            JWT token string
        """
        payload: Dict[str, Any] = {
            "bot_id": bot_id,
            "iat": datetime.now(timezone.utc),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        }

        return jwt.encode(
            payload,
            Config.BOT_JWT_SECRET,
            algorithm="HS256",
        )

    @staticmethod
    def validate_bot_jwt(token: str) -> Dict[str, Any]:
        """Validate bot JWT token.

        Args:
            token: JWT token string

        Returns:
            Decoded payload

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        return jwt.decode(  # type: ignore[no-any-return]
            token,
            Config.BOT_JWT_SECRET,
            algorithms=["HS256"],
        )
