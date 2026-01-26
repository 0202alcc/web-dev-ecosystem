from flask import Flask
from pathlib import Path


def create_app() -> Flask:
    """Application factory pattern for Flask app."""
    static_folder = Path(__file__).parent.parent / "static"
    app = Flask(__name__, static_folder=str(static_folder), static_url_path="/static")

    app.config.from_object("app.config.Config")

    # ---------- ENV sanity check ----------
    allowed_envs = {"production", "development", "testing"}
    if app.config.get("ENV") not in allowed_envs:
        raise RuntimeError(
            f"Invalid ENV value '{app.config.get('ENV')}'! Must be one of {allowed_envs}"
        )

    if app.config.get("ENV") != "production":
        print(
            f"⚠️  WARNING: App running in {app.config.get('ENV').upper()} mode! "
            "Make sure this is intentional."
        )

    # -------------------- continue normal init --------------------

    from app.routes import api
    app.register_blueprint(api.bp)

    @app.route("/")
    def index():
        """Serve the main PWA page."""
        return app.send_static_file("index.html")

    @app.route("/sw.js")
    def service_worker():
        """Serve service worker from root to allow scope of /."""
        response = app.send_static_file("sw.js")
        response.headers["Content-Type"] = "application/javascript"
        response.headers["Service-Worker-Allowed"] = "/"
        return response

    @app.route("/favicon.ico")
    def favicon():
        """Serve favicon to prevent 404 errors."""
        return app.send_static_file("favicon.ico", mimetype="image/x-icon")

    return app
