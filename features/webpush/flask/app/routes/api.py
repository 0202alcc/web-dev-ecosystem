import logging

from flask import Blueprint, jsonify, request

from app.config import Config
from app.models.bot_request import BotNotificationRequest
from app.services.auth_service import AuthService
from app.services.push_service import PushService
from app.utils.security import get_client_ip, validate_ip_prefix, validate_timestamp

logger = logging.getLogger(__name__)

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.route("/config", methods=["GET"])
def get_config():
    """Get client configuration.

    Returns:
        JSON response with VAPID public key
    """
    return jsonify(
        {
            "success": True,
            "vapid_public_key": Config.VAPID_PUBLIC_KEY,
        }
    )


@bp.route("/send-notification", methods=["POST"])
def send_bot_notification():
    """Endpoint for bots to send push notifications.

    This endpoint validates:
    1. IP address matches allowed prefix
    2. Timestamp is within 5-minute window
    3. JWT authentication (OPTIONAL - see comments below)

    NOTE: JWT authentication is available but NOT currently activated.
    To enable JWT validation for enhanced security:
    1. Set BOT_JWT_SECRET in .env
    2. Add JWT validation call after timestamp validation
    3. Update bot client to include JWT in request headers
    See docs/documentation.md section "Security Configuration" for implementation details.

    Request Body (JSON):
        {
            "bot_id": "bot_identifier",
            "title": "Notification title",
            "content": "Notification content",
            "timestamp": 1737302400000
        }

    Returns:
        JSON response with notification status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(
                {
                    "success": False,
                    "error": "No JSON data provided",
                }
            ), 400

        # Extract recipient_external_id before validation (not part of BotNotificationRequest model)
        recipient_external_id = data.get("recipient_external_id")

        # Create request object (excludes recipient_external_id)
        bot_req = BotNotificationRequest(**data)

        client_ip = get_client_ip(request) or ""

        if not validate_ip_prefix(client_ip, Config.ALLOWED_BOT_IPS):
            logger.warning(f"Unauthorized IP attempt: {client_ip}")
            return jsonify(
                {
                    "success": False,
                    "error": "Unauthorized IP address",
                }
            ), 403

        if not validate_timestamp(bot_req.timestamp_ms):
            logger.warning(f"Invalid timestamp: {bot_req.timestamp_ms}")
            return jsonify(
                {
                    "success": False,
                    "error": "Invalid or expired timestamp",
                }
            ), 403

        try:
            # Send push notification directly
            if recipient_external_id:
                success = PushService.send_notification(
                    user_external_id=recipient_external_id,
                    title=bot_req.title,
                    content=bot_req.content,
                )
                if not success:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"No subscription found for user: {recipient_external_id}",
                        }
                    ), 404

                logger.info(
                    f"Notification sent from bot {bot_req.bot_id} to {recipient_external_id}: {bot_req.title}"
                )
            else:
                # Broadcast to all subscribed users
                count = PushService.broadcast_notification(
                    title=bot_req.title,
                    content=bot_req.content,
                )
                logger.info(
                    f"Notification broadcast from bot {bot_req.bot_id} to {count} users: {bot_req.title}"
                )

            return jsonify(
                {
                    "success": True,
                    "message": "Notification sent successfully",
                }
            )

        except Exception as e:
            logger.error(f"Push notification error: {e}")
            return jsonify(
                {
                    "success": False,
                    "error": "Failed to send notification",
                }
            ), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify(
            {
                "success": False,
                "error": "Internal server error",
            }
        ), 500


@bp.route("/register-push-subscription", methods=["POST"])
def register_push_subscription():
    """Register a push subscription (stored locally).

    Request Body (JSON):
        {
            "subscription": {
                "endpoint": "https://...",
                "keys": {
                    "p256dh": "...",
                    "auth": "..."
                }
            },
            "user_external_id": "device-uuid-here"
        }

    Returns:
        JSON response with registration status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(
                {
                    "success": False,
                    "error": "No JSON data provided",
                }
            ), 400

        subscription = data.get("subscription")
        user_external_id = data.get("user_external_id")

        if not subscription or not user_external_id:
            return jsonify(
                {
                    "success": False,
                    "error": "Missing subscription or user_external_id",
                }
            ), 400

        # Store subscription locally
        PushService.register_subscription(user_external_id, subscription)

        logger.info(f"Push subscription registered for {user_external_id}")
        return jsonify(
            {
                "success": True,
                "message": "Subscription registered successfully",
            }
        )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify(
            {
                "success": False,
                "error": "Internal server error",
            }
        ), 500


@bp.route("/test-notification", methods=["POST"])
def send_test_notification():
    """Test endpoint to send a notification (bypasses bot security for testing).

    Request Body (JSON):
        {
            "title": "Notification title",
            "content": "Notification content",
            "user_external_id": "device-uuid" (optional, broadcasts if not provided)
        }

    Returns:
        JSON response with notification status
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify(
                {
                    "success": False,
                    "error": "No JSON data provided",
                }
            ), 400

        title = data.get("title", "Test Notification")
        content = data.get("content", "This is a test notification")
        user_external_id = data.get("user_external_id")

        try:
            # Send push notification directly
            if user_external_id:
                success = PushService.send_notification(
                    user_external_id=user_external_id,
                    title=title,
                    content=content,
                )
                if not success:
                    return jsonify(
                        {
                            "success": False,
                            "error": f"No subscription found for user: {user_external_id}",
                        }
                    ), 404

                logger.info(f"Test notification sent to {user_external_id}: {title}")
            else:
                count = PushService.broadcast_notification(
                    title=title,
                    content=content,
                )
                logger.info(f"Test notification broadcast to {count} users: {title}")

            return jsonify(
                {
                    "success": True,
                    "message": "Notification sent successfully",
                }
            )

        except Exception as e:
            logger.error(f"Push notification error: {e}")
            return jsonify(
                {
                    "success": False,
                    "error": f"Failed to send notification: {str(e)}",
                }
            ), 500

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify(
            {
                "success": False,
                "error": "Internal server error",
            }
        ), 500


@bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint.

    Returns:
        JSON response with health status
    """
    return jsonify(
        {
            "status": "healthy",
            "service": "flask-webpush",
        }
    )


@bp.route("/jwt", methods=["GET"])
def generate_user_jwt():
    """Generate User JWT for MagicBell authentication.

    Query Parameters:
        user_email: User's email address (optional)
        user_external_id: User's external ID (optional)

    Returns:
        JSON response with JWT token
    """
    user_email = request.args.get("user_email")
    user_external_id = request.args.get("user_external_id")

    try:
        token = AuthService.generate_user_jwt(user_email, user_external_id)
        return jsonify(
            {
                "success": True,
                "token": token,
                "api_key": Config.MAGICBELL_API_KEY,
                "vapid_public_key": Config.VAPID_PUBLIC_KEY,
            }
        )
    except ValueError as e:
        logger.error(f"JWT generation error: {e}")
        return jsonify(
            {
                "success": False,
                "error": str(e),
            }
        ), 400
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify(
            {
                "success": False,
                "error": "Internal server error",
            }
        ), 500
