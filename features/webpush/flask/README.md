# Flask WebPush Implementation
A Flask-based implementation of web push notifications using pywebpush.
## Features
- Direct Web Push API integration (no external services)
- IP whitelist + timestamp validation security
- PWA support with service worker
- Comprehensive test suite
## Quick Start
```bash
cd features/webpush/flask
uv venv
uv pip install -e ".[dev]"
uv run main.py
```
## API Endpoints
- `GET /api/health` - Health check
- `GET /api/jwt` - Generate user JWT
- `POST /api/send-notification` - Send push notifications
- `POST /api/register-push-subscription` - Register subscriptions
## Security
- IP whitelist validation
- Timestamp validation (5-minute window)
- Optional JWT authentication
## Testing
```bash
uv run pytest tests/
```
For more details, see the main monorepo documentation.
