import os
from flask import Flask
from supabase import create_client, Client
from supabase.client import ClientOptions
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app():
    """
    Flask application factory.
    Creates and configures the Flask app with Supabase integration.
    """
    app = Flask(__name__)

    # Flask configuration
    app.secret_key = os.environ.get("SECRET_KEY", "dev-key")

    # Supabase client initialization with custom options
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError(
            "Missing Supabase credentials. "
            "Please set SUPABASE_URL and SUPABASE_KEY in .env file"
        )

    supabase: Client = create_client(
        url,
        key,
        options=ClientOptions(
            postgrest_client_timeout=10,  # Timeout for API calls
            storage_client_timeout=10,    # Timeout for storage operations
            schema="public",              # Database schema
        )
    )

    # Attach Supabase client to app for route access
    app.supabase = supabase

    # Register blueprints
    # Note: These will be imported after app creation to avoid circular imports
    from app.routes import auth, dashboard, data, profile

    app.register_blueprint(auth.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(profile.bp)

    # Future: Add validation for user_configs JSON on edit
    # - Ensure 'headers' list is not empty
    # - Validate eviction method is one of allowed values
    # - Validate limit is positive integer

    return app
