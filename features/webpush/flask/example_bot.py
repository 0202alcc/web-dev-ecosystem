#!/usr/bin/env python3
"""
Example bot script to send notifications to the Flask WebPush server.

This script demonstrates how a bot/script on your network can trigger
push notifications that will be delivered to all subscribed devices.

Usage:
    python example_bot.py "Notification Title" "Notification content"

Or modify the FLASK_SERVER_URL and run directly.
"""

import sys
import time
import requests


# Configuration
FLASK_SERVER_URL = "http://192.168.12.118:3000"  # Change to your server's IP
RECIPIENT_EXTERNAL_ID = None  # Set to user's UUID to send to specific user, None to broadcast


def send_notification(title: str, content: str, recipient_external_id: str | None = None):
    """Send a notification via the Flask server.

    Args:
        title: Notification title
        content: Notification content
        recipient_external_id: Optional recipient external ID (if None, broadcasts to all)

    Returns:
        bool: True if successful, False otherwise
    """
    url = f"{FLASK_SERVER_URL}/api/send-notification"

    payload = {
        "bot_id": "example_bot",
        "title": title,
        "content": content,
        "timestamp": int(time.time() * 1000),  # Current timestamp in milliseconds
    }

    # Add recipient if specified
    if recipient_external_id:
        payload["recipient_external_id"] = recipient_external_id

    try:
        print(f"Sending notification to {url}...")
        print(f"Title: {title}")
        print(f"Content: {content}")
        if recipient_external_id:
            print(f"Recipient: {recipient_external_id}")
        else:
            print("Broadcasting to all users")

        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()

        data = response.json()
        if data.get("success"):
            print("✓ Notification sent successfully!")
            print(f"Notification ID: {data.get('notification_id')}")
            return True
        else:
            print(f"✗ Failed to send notification: {data.get('error')}")
            return False

    except requests.exceptions.ConnectionError:
        print(f"✗ Could not connect to {FLASK_SERVER_URL}")
        print("Make sure the Flask server is running and the URL is correct.")
        return False
    except requests.exceptions.Timeout:
        print("✗ Request timed out")
        return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Default test notification
        title = "Test Notification"
        content = "This is a test notification from the example bot!"
    elif len(sys.argv) == 2:
        title = sys.argv[1]
        content = "Notification from example bot"
    else:
        title = sys.argv[1]
        content = sys.argv[2]

    print("=" * 60)
    print("Flask WebPush Example Bot")
    print("=" * 60)

    success = send_notification(title, content, RECIPIENT_EXTERNAL_ID)

    print("=" * 60)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
