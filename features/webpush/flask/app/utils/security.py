import logging
from datetime import UTC, datetime, timedelta

from flask import Request

logger = logging.getLogger(__name__)


def validate_ip_prefix(ip: str, allowed_prefix: str) -> bool:
    """Validate that IP address matches allowed prefix.

    Args:
        ip: IP address to validate
        allowed_prefix: Allowed IP prefix (e.g., "192.168.12.")

    Returns:
        True if IP matches prefix, False otherwise
    """
    if not ip:
        return False

    if not allowed_prefix:
        return False

    return ip.startswith(allowed_prefix)


def validate_timestamp(timestamp_ms: int, max_age_minutes: int = 5) -> bool:
    """Validate that timestamp is within acceptable time window.

    Args:
        timestamp_ms: Timestamp in milliseconds
        max_age_minutes: Maximum age in minutes (default 5)

    Returns:
        True if timestamp is valid, False otherwise
    """
    try:
        timestamp = datetime.fromtimestamp(timestamp_ms / 1000, tz=UTC)
        now = datetime.now(UTC)
        max_age = timedelta(minutes=max_age_minutes)

        age = abs(now - timestamp)
        return age <= max_age
    except (ValueError, OSError):
        logger.error(f"Invalid timestamp: {timestamp_ms}")
        return False


def get_client_ip(request: Request) -> str | None:
    """Get client IP address from request.

    Args:
        request: Flask request object

    Returns:
        Client IP address or None if not found
    """
    if request.headers.getlist("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    return request.remote_addr
