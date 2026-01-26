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

### Quick Test Run
```bash
cd features/webpush/flask # Navigate to the flask project
uv venv
uv pip install -e ".[dev]"
uv run pytest tests/ -v --tb=short
```

### Test Structure
- **Unit Tests** (`tests/unit/`): Core logic and services (18 existing tests)
- **Integration Tests** (`tests/integration/`): API endpoints and full flows (8 new tests)
- **Coverage**: ~60-70% on critical paths (server startup, API responses, basic push notifications)
- **CI Integration**: Tests run automatically via GitHub Actions: `.github/workflows/reusable-test-flask-webpush-framework.yml`

### Current Test Coverage Ensures
- ✅ Server starts without import errors or port conflicts
- ✅ Core API endpoints respond (health, config, JWT generation)
- ✅ Basic push notification flow works with mocked external calls
- ✅ Sparse checkout users get functional code without obvious breakage

### High Priority
- **Error Handling Tests**: Add comprehensive auth failure scenarios, malformed requests, expired tokens, and network error simulation
- **Full End-to-End Flow**: Implement complete notification lifecycle (subscription registration → push sending → client receipt)
- **API Documentation Tests**: Add tests to ensure API responses match documented schemas

### Medium Priority
- **Browser Integration Tests**: Service worker registration, push permission requests, and real browser notifications
- **Performance Benchmarks**: Load testing for multiple concurrent notifications
- **Configuration Testing**: Test different environment variable combinations and edge cases

### Low Priority
- **UI Integration**: Test the PWA frontend with real notifications
- **Cross-Browser Compatibility**: Test on Chrome, Firefox, Safari, and mobile browsers
- **Monitoring & Metrics**: Add tests for logging and error reporting functionality
- **Security Audits**: Penetration testing and vulnerability assessments

## TO DO: Feature Development (Future)
- Implement user login features
- Add WebSocket support for real-time status updates
For more details, see the main monorepo documentation.
