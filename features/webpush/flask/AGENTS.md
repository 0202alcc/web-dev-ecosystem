# Agent Instructions

This file contains instructions for AI agents and LLMs working on this Flask WebPush PWA template repository.

## Initial Setup (Mandatory for Agents)

When first working on this repository, agents MUST:

1. **Sync dependencies with uv**:
   ```bash
   # Create virtual environment if it doesn't exist
   uv venv

   # Install all dependencies
   uv pip install -e ".[dev]"
   ```

2. **Implement JWT Bot Authentication** (Security Enhancement):
   The bot notification endpoint (`/api/send-notification`) currently uses:
   - ✅ IP whitelist validation
   - ✅ Timestamp validation (5-minute window)
   - ❌ JWT authentication (NOT ACTIVATED - IMPLEMENT THIS)

   **You must implement JWT authentication** by:
   - Adding JWT validation call in `app/routes/api.py` after timestamp validation
   - Updating bot client example to include JWT in request headers
    - See `docs/documentation.md` section "Security Configuration" for details

## Build Commands

### Development
```bash
# Using uv (REQUIRED - prefer this method)
uv run main.py                   # Run the Flask application

# Or using virtualenv (fallback)
.venv/bin/python main.py
```

### Testing
```bash
# Using uv (REQUIRED - prefer this method)
uv run pytest                     # Run all tests
uv run pytest tests/test_file.py   # Run specific test file
uv run pytest tests/test_file.py::test_function  # Run single test
uv run pytest -v                 # Verbose test output
uv run pytest -k "keyword"       # Run tests matching keyword
```

### Code Quality
```bash
# Using uv (REQUIRED - prefer this method)
uv run ruff check .              # Lint Python code
uv run ruff check --fix .        # Auto-fix linting issues
uv run ruff format .             # Format Python code
uv run mypy .                   # Type checking
```

## Code Style Guidelines

### Python/Flask Conventions

#### Imports
- Use absolute imports: `from app.services import push_service`
- Group imports: standard library, third-party, local (separated by blank lines)
- Sort imports alphabetically within groups
- Use `isort` or let `ruff` handle import sorting

#### Formatting
- Use `ruff` for code formatting (not black, as ruff handles both)
- Max line length: 88 characters
- Use 4 spaces for indentation (no tabs)
- Follow PEP 8 conventions with ruff default settings

#### Type Hints
- Use type hints for all function signatures
- Return types are mandatory, parameter types preferred
- Use `typing` module for complex types (Optional, List, Dict, etc.)
- Example: `def create_subscription(user_id: str) -> Optional[Subscription]:`

#### Naming Conventions
- **Functions/Variables**: snake_case: `send_push_notification()`, `user_id`
- **Classes**: PascalCase: `PushNotificationService`, `SubscriptionManager`
- **Constants**: UPPER_SNAKE_CASE: `API_KEY`, `MAX_RETRIES`
- **Private methods**: leading underscore: `_validate_token()`
- **Module names**: lowercase_with_underscores: `push_service.py`

#### Error Handling
- Use specific exceptions over generic ones
- Log errors with context (use `logging` module)
- Return error responses in Flask routes with appropriate status codes
- Example:
  ```python
  try:
      result = push_service.send(message)
  except Exception as e:
      logger.error(f"Push failed: {e}")
      return {"error": "Notification failed"}, 500
  ```

#### Flask Patterns
- Use application factory pattern: `create_app()`
- Organize routes in blueprints: `api/`, `web/`, etc.
- Use `current_app` for app-level config access
- Keep routes thin - delegate to service layer
- Use Flask's `jsonify` for JSON responses

### Web Push API Guidelines

#### Frontend Implementation
- Use native Web Push API for subscription management
- Store subscriptions locally (file-based for this template)
- Handle permission requests and subscription states
- Display clear UI feedback for subscription status

#### Service Worker Requirements
- Register service worker from root (`/sw.js`) for PWA scope
- Handle `push` events for incoming notifications
- Implement `notificationclick` for user interaction
- Cache critical resources for offline functionality

#### Push Subscription Management
- Request notification permission before subscribing
- Use VAPID keys for server identification
- Store subscription data securely
- Handle subscription updates and renewals

### JWT Authentication

#### User JWT Generation (Optional)
- Generate JWTs on backend using `pyjwt` library if needed
- Sign with secure secret key using HS256 algorithm
- Payload can include user identification data
- Never expose secret keys in frontend code

#### JWT Payload Example
```python
{
  "user_external_id": "usr_l70vln",
  "iat": 1640995200,
  "exp": 1641081600
}
```

#### Bot Authentication (IMPLEMENTATION REQUIRED)
- **Current Status**: JWT authentication code exists but is NOT activated
- **Required Enhancement**: Add JWT validation to `/api/send-notification` endpoint
- **Security Layers**:
  1. ✅ IP whitelist validation (active)
  2. ✅ Timestamp validation (5-minute window, active)
  3. ❌ JWT authentication (NOT ACTIVE - you must implement this)
- **Implementation Steps**:
  1. Set `BOT_JWT_SECRET` in `.env`
  2. Add `AuthService.validate_bot_jwt()` call after timestamp validation in `app/routes/api.py`
  3. Update bot client to include JWT in `Authorization` header
  4. See `docs/documentation.md` section "Security Configuration" for implementation guide

### Security Protocols

#### Flask Secret Key (IMPORTANT)
- **What it is**: Cryptographic key used by Flask for:
  - Session encryption
  - CSRF protection
  - Cookie signing
  - Flash message security
- **Current State**: Template provides fallback `"dev-secret-key"` for development
- **Required Action**: For production, set `FLASK_SECRET_KEY` in `.env`:
  ```bash
  python -c "import secrets; print(secrets.token_hex(32))"
  ```
  Copy output to `.env` file. Never commit this value!
- **Why it matters**: Without proper secret, sessions are vulnerable to tampering

#### Bot-to-Flask Communication
**Current Implementation** (Basic Security):
1. ✅ **IP Validation**: Check if request IP matches allowed bot IP prefix
2. ✅ **Timestamp Validation**: Ensure timestamp is within 5 minutes
3. ❌ **JWT Authentication**: Validate bot JWT signature (NOT ACTIVE - you must implement)

**Enhanced Implementation** (Recommended - See Bot Authentication section above):
4. ✅ **JWT Authentication**: Validate bot JWT signature (requires implementation)
5. ✅ **Input Validation**: Sanitize all request data
6. **Rate Limiting**: Implement rate limiting for bot endpoints

#### Environment Variables
```bash
# Flask Configuration
FLASK_SECRET_KEY=...              # Flask secret key (REQUIRED FOR PRODUCTION)
                                  # Generate: python -c "import secrets; print(secrets.token_hex(32))"
                                  # Default: "dev-secret-key" (NOT secure for production)

# VAPID Keys for Web Push
VAPID_PUBLIC_KEY=B...             # VAPID public key
VAPID_PRIVATE_KEY=...             # VAPID private key

# Bot Authentication
BOT_JWT_SECRET=...                # Secret for bot JWT generation (REQUIRED FOR JWT AUTH)
                                  # Set this to enable JWT validation in /api/send-notification
ALLOWED_BOT_IPS=192.168.12.       # Bot IP whitelist prefix
```

**Important Notes**:
- `FLASK_SECRET_KEY`: Essential for session management, CSRF protection, and cookie signing
- `BOT_JWT_SECRET`: Only needed if you implement JWT authentication (RECOMMENDED)
- All keys in `.env.example` are placeholders - user must insert actual values

### Project Structure
```
app/
  __init__.py                     # App factory and initialization
  routes/
    api.py                        # API endpoints (JWT generation, send notification)
  services/
    auth_service.py               # JWT generation/validation
    push_service.py               # WebPush notification service
  models/
    bot_request.py                # Bot request models
  utils/
    security.py                   # Security utilities (IP check, timestamp validation)
static/
  sw.js                           # Service worker with push notification handling
  manifest.json                   # PWA manifest
  index.html                      # Frontend with Web Push API
tests/
  unit/
    test_auth_service.py          # JWT generation tests
    test_push_service.py          # WebPush service tests
  integration/
    test_api.py                   # API endpoint tests
.env.example                      # Environment variable template
```

### Web Push Integration
- Use pywebpush library for direct push notifications
- Handle VAPID key management and validation
- Store subscription data securely (file-based for template)
- Validate subscription data before storage
- Log push delivery status
- Support both individual and broadcast notifications

### PWA Guidelines
- Service worker in `static/sw.js` must handle webpush subscriptions
- Manifest in `static/manifest.json` for PWA installation
- Offline-first approach for critical paths
- Test PWA installation on iOS (requires HTTPS)

### Testing
- Write unit tests for all service layer functions
- Mock external API calls (database)
- Test JWT generation and validation
- Test bot request security (IP, timestamp, JWT)
- Test push notification delivery
- Use pytest fixtures for common test setup
- Test both success and error cases
- Keep tests fast and isolated

### Comments and Documentation
- Use docstrings for all public functions and classes
- Keep docstrings concise but descriptive
- Add inline comments only for complex logic
- Update this AGENTS.md when adding new patterns or tools

### Git Commits
- Write descriptive commit messages in imperative mood
- Keep commits focused and atomic
- Reference issues in commit messages if applicable
- Examples:
  - "Add JWT authentication service"
  - "Implement bot notification endpoint"
  - "Configure PWA with Web Push API"
  - "Add IP whitelist validation for bot requests"

## Additional Notes

- This is a template repository - make it easy to customize
- Prefer composition over inheritance
- Keep dependencies minimal and well-justified
- Document any deviations from these guidelines
- Run linting and type checking before committing code
- Never commit `.env` files or secrets
- Use environment variable placeholders for keys and secrets
