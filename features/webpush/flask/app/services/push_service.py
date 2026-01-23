"""Direct web push notification service (bypasses MagicBell)."""

import json
import logging
from pathlib import Path
from typing import Any

from pywebpush import webpush

from app.config import Config

logger = logging.getLogger(__name__)

# Simple file-based storage for subscriptions
SUBSCRIPTIONS_FILE = Path(__file__).parent.parent.parent / "subscriptions.json"


class PushService:
    """Service for managing push subscriptions and sending notifications."""

    @staticmethod
    def load_subscriptions() -> dict[str, dict[str, Any]]:
        """Load subscriptions from file."""
        if not SUBSCRIPTIONS_FILE.exists():
            return {}

        try:
            with open(SUBSCRIPTIONS_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load subscriptions: {e}")
            return {}

    @staticmethod
    def save_subscriptions(subscriptions: dict[str, dict[str, Any]]) -> None:
        """Save subscriptions to file."""
        try:
            with open(SUBSCRIPTIONS_FILE, "w") as f:
                json.dump(subscriptions, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save subscriptions: {e}")

    @staticmethod
    def register_subscription(
        user_external_id: str, subscription: dict[str, Any]
    ) -> None:
        """Register a push subscription for a user.

        Args:
            user_external_id: User's external ID
            subscription: Push subscription object
        """
        subscriptions = PushService.load_subscriptions()
        subscriptions[user_external_id] = subscription
        PushService.save_subscriptions(subscriptions)
        logger.info(f"Registered push subscription for user: {user_external_id}")

    @staticmethod
    def get_subscription(user_external_id: str) -> dict[str, Any] | None:
        """Get a user's push subscription.

        Args:
            user_external_id: User's external ID

        Returns:
            Push subscription object or None if not found
        """
        subscriptions = PushService.load_subscriptions()
        return subscriptions.get(user_external_id)

    @staticmethod
    def send_notification(
        user_external_id: str, title: str, content: str
    ) -> bool:
        """Send a push notification to a user.

        Args:
            user_external_id: User's external ID
            title: Notification title
            content: Notification content

        Returns:
            True if successful, False otherwise
        """
        subscription = PushService.get_subscription(user_external_id)
        if not subscription:
            logger.warning(f"No subscription found for user: {user_external_id}")
            return False

        try:
            notification_data = json.dumps({"title": title, "content": content})

            webpush(
                subscription_info=subscription,
                data=notification_data,
                vapid_private_key=Config.VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:admin@example.com",  # Required by VAPID spec
                },
            )

            logger.info(
                f"Push notification sent to {user_external_id}: {title}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
            return False

    @staticmethod
    def broadcast_notification(title: str, content: str) -> int:
        """Send a push notification to all subscribed users.

        Args:
            title: Notification title
            content: Notification content

        Returns:
            Number of successful sends
        """
        subscriptions = PushService.load_subscriptions()
        success_count = 0

        for user_id in subscriptions:
            if PushService.send_notification(user_id, title, content):
                success_count += 1

        logger.info(
            f"Broadcast notification sent to {success_count}/{len(subscriptions)} users"
        )
        return success_count
