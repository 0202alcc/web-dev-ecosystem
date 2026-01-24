# Flask WebPush Implementation
A Flask-based implementation of web push notifications using pywebpush.
## Features
- Direct Web Push API integration (no external services)
- IP whitelist + timestamp validation security
- PWA support with service worker
- Comprehensive test suite
## Quick Start
```bash
# Create new project
mkdir PROJECT-NAME-HERE
cd PROJECT-NAME-HERE

# Init git and add remote
git init
git remote add origin https://github.com/0202alcc/web-dev-ecosystem.git

# Enable sparse checkout
git config core.sparseCheckout true

# Configure sparse checkout to only include Flask webpush
echo "features/webpush/flask/*" >> .git/info/sparse-checkout

# Pull only the Flask webpush directory
git pull origin main

# Move files to project root (optional)
mv features/webpush/flask/* .
rm -rf features/
```

How to run the project
```bash
cd features/webpush/flask # If files are not in root then cd to flask project
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
