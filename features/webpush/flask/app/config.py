import os
from dotenv import load_dotenv


def load_env() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


load_env()


class Config:
    """Configuration class for Flask application."""

    SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-secret-key")
    VAPID_PUBLIC_KEY: str = os.getenv("VAPID_PUBLIC_KEY", "")
    VAPID_PRIVATE_KEY: str = os.getenv("VAPID_PRIVATE_KEY", "")
    BOT_JWT_SECRET: str = os.getenv("BOT_JWT_SECRET", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dummy-secret")
    ALLOWED_BOT_IPS: str = os.getenv("ALLOWED_BOT_IPS", "")
