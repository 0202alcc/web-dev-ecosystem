#!/usr/bin/env uv run python
import os
import secrets


def generate_env_file():
    env_file = "features/webpush/flask/.env"
    if os.path.exists(env_file):
        print(".env already exists, skipping generation.")
        return True

    env_content = ""

    # VAPID keys (generate if not provided)
    vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", secrets.token_hex(32))
    vapid_private_key = os.getenv("VAPID_PRIVATE_KEY", secrets.token_urlsafe(32))

    env_content += f"VAPID_PUBLIC_KEY={vapid_public_key}\n"
    env_content += f"VAPID_PRIVATE_KEY={vapid_private_key}\n"

    # Flask secret
    flask_secret = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
    env_content += f"FLASK_SECRET_KEY={flask_secret}\n"

    # Bot JWT secret
    bot_jwt_secret = os.getenv("BOT_JWT_SECRET", secrets.token_hex(32))
    env_content += f"BOT_JWT_SECRET={bot_jwt_secret}\n"
    # JWT secret for user JWT
    jwt_secret = os.getenv("JWT_SECRET", secrets.token_hex(32))
    env_content += f"JWT_SECRET={jwt_secret}\n"

    # Bot IPs allowed
    env_content += "ALLOWED_BOT_IPS=127.0.0.1\n"

    with open(env_file, "w") as f:
        f.write(env_content)

    print(".env file generated successfully.")
    return True


if __name__ == "__main__":
    generate_env_file()
