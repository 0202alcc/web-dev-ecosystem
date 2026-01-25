# Flask WebPush PWA Template - Documentation

This comprehensive guide covers everything you need to know about setting up, configuring, and using the Flask WebPush PWA template.

## Overview

This is a **template repository** designed for building Progressive Web Apps (PWAs) with direct web push notification support using pywebpush. It provides a solid foundation for local network deployments where any device can access the PWA, but only verified bots can trigger notifications.

## Key Features

### Backend
- **Flask**: Python-based REST API server with application factory pattern
- Modular, scalable architecture with clean separation of concerns
- JWT authentication support for users and bots
- Comprehensive error handling and logging

### WebPush Notifications
- **pywebpush library**: Direct Web Push API integration (no external services required)
- **Cross-platform support**: iOS and Android push notifications
- **VAPID key management**: Server identification for push services
- **Subscription management**: Register and manage user push subscriptions

### Security
- **IP Whitelist**: Bot request validation by IP prefix (supports local network + Tailscale)
- **Timestamp Validation**: 5-minute window prevents replay attacks
- **JWT Authentication**: Optional but recommended bot authentication
- **Flask Secret Key**: Session management and CSRF protection

### PWA Features
- Progressive Web App standards compliance
- Service worker for offline support and push handling
- Web App Manifest for installation
- Responsive HTML frontend for testing

### Deployment
- **Local Network Focus**: Designed for home network servers
- **Tailscale Support**: Works with Tailscale VPN for remote access
- **Any Device Access**: PWA accessible from any device on network
- **Bot Restrictions**: Only verified bots (same network/Tailscale) can send notifications

## Setup Guide

### Prerequisites

- Python 3.14 or higher
- uv (recommended) or pip for dependency management
- VAPID keys for web push notifications

### 1. Install uv (Recommended)

```bash
# macOS with Homebrew
brew install uv

# Or with curl
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Install Dependencies

```bash
# Clone the repository
git clone <your-repo-url>
cd flask-webpush-template

# Create virtual environment and install dependencies
uv venv
uv pip install -e ".[dev]"

# Alternative with pip
pip install -e ".[dev]"
```

### 3. Generate VAPID Keys

VAPID keys are required for web push notifications. Generate them using one of these methods:

**Option A: Online Generator**
- Go to [https://vapidkeys.com/](https://vapidkeys.com/)
- Or [https://www.attheminute.com/vapid-key-generator](https://www.attheminute.com/vapid-key-generator)
- Generate new keys
- Copy both public and private keys

**Option B: Command Line**
```bash
# Install pywebpush if not already installed
uv run python -c "from pywebpush import vapid; keys = vapid.generate_vapid_keypair(); print('Public:', keys['public_key']); print('Private:', keys['private_key'])"
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Flask Configuration
# Generate a secure key for production
FLASK_SECRET_KEY=your_secure_random_key_here

# VAPID Keys for Web Push (REQUIRED)
VAPID_PUBLIC_KEY=B_your_vapid_public_key_here
VAPID_PRIVATE_KEY=your_vapid_private_key_here

# Bot Authentication (Optional but Recommended)
BOT_JWT_SECRET=your_bot_jwt_secret_here
ALLOWED_BOT_IPS=192.168.12.   # Your local network subnet

# Application Settings
FLASK_ENV=development
FLASK_DEBUG=True
```

### 5. Run the Application

```bash
# Using uv (recommended)
uv run main.py

# Or using virtualenv
.venv/bin/python main.py
```

The application will be available at `http://localhost:3000`

### Security Configuration

#### Flask Secret Key
**Required for production deployments:**
```bash
# Generate a secure key
python -c "import secrets; print(secrets.token_hex(32))"
```
Set this in your `.env` file as `FLASK_SECRET_KEY`. It enables:
- Session management
- CSRF protection
- Cookie signing

#### Bot Authentication
The template uses **IP whitelist + timestamp validation** by default:

- `ALLOWED_BOT_IPS`: IP prefix for allowed bots (e.g., `192.168.12.` for local network)
- Timestamp validation: 5-minute window prevents replay attacks

**Optional JWT Enhancement:**
Set `BOT_JWT_SECRET` to enable additional JWT authentication for bots. See AGENTS.md for implementation details.

#### Network Security Model
- **Any device** can access the PWA interface
- **Only verified bots** (matching IP whitelist) can trigger notifications
- Supports both local network and Tailscale VPN configurations

## Project Structure

```
flask-webpush-template/
├── app/
│   ├── __init__.py              # Flask app factory and configuration
│   ├── routes/
│   │   └── api.py              # API endpoints (health, JWT, notifications)
│   ├── services/
│   │   ├── auth_service.py     # JWT generation/validation
│   │   └── push_service.py     # pywebpush integration
│   ├── models/
│   │   └── bot_request.py     # Pydantic request models
│   ├── utils/
│   │   └── security.py         # IP/timestamp validation
│   └── config.py              # Environment configuration
├── static/
│   ├── index.html               # PWA frontend interface
│   ├── sw.js                   # Service worker for push notifications
│   └── manifest.json           # PWA manifest for installation
├── tests/
│   ├── unit/                   # Unit tests for services and utilities
│   └── integration/            # Integration tests for API endpoints
├── docs/
│   ├── LLM_Context.md          # AI agent context and instructions
│   └── documentation.md        # This comprehensive documentation
├── .env.example                # Environment variable template
├── main.py                     # Flask application entry point
├── pyproject.toml              # Python dependencies and configuration
├── README.md                   # Project overview and quick start
└── AGENTS.md                   # Instructions for AI agents and LLMs
```

## API Documentation

### Health Check
```http
GET /api/health
```

Returns server status:
```json
{
  "status": "healthy",
  "service": "flask-webpush"
}
```

### Generate User JWT (Optional)
```http
GET /api/jwt?user_email=user@example.com
GET /api/jwt?user_external_id=usr_123
```

Returns JWT token for optional user authentication:
```json
{
  "success": true,
  "token": "eyJ0eXAi...",
  "api_key": "",
  "vapid_public_key": "B_..."
}
```

### Register Push Subscription
```http
POST /api/register-push-subscription
Content-Type: application/json

{
  "subscription": {
    "endpoint": "https://fcm.googleapis.com/fcm/send/...",
    "keys": {
      "p256dh": "...",
      "auth": "..."
    }
  },
  "user_external_id": "usr_123"
}
```

### Send Bot Notification (IP + Timestamp Secured)
```http
POST /api/send-notification
Content-Type: application/json

{
  "bot_id": "bot_001",
  "title": "Notification Title",
  "content": "Notification content",
  "timestamp": 1737302400000
}
```

**Security Requirements:**
- Request must come from IP matching `ALLOWED_BOT_IPS`
- Timestamp must be within 5-minute window
- Optional JWT authentication available

Returns:
```json
{
  "success": true,
  "message": "Notification sent successfully"
}
```

## Testing Push Notifications

### Prerequisites

1. Flask server running (`uv run main.py`)
2. VAPID keys configured in `.env`
3. Bot running on same network as Flask server (or via Tailscale)

### Test Flow Overview

```
Bot Script → Flask Server → pywebpush → Push Service → User's Device(s)
   (Local network)     (Your server)    (Direct)       (Anywhere)
```

### Step 1: Subscribe to Notifications

#### Option A: Test on Desktop (Mac/Windows/Linux)

1. Open `http://localhost:3000` in your browser
2. Click "Enable notifications"
3. Grant permission when prompted
4. Verify "Push Subscription: Subscribed" appears in footer

#### Option B: Test on Mobile (iOS/Android)

**For iOS:**
1. Open Safari on your device
2. Go to your server's URL (may need ngrok for HTTPS)
3. Tap Share → "Add to Home Screen"
4. Open the installed PWA
5. Click "Enable notifications" and grant permission

**For Android:**
1. Open Chrome
2. Go to your server's URL
3. Follow the same steps as desktop

### Step 2: Send Test Notifications

#### Option A: Use the Web Interface
Click the "Send Test Notification" button on the PWA. This sends a local notification to verify your subscription works.

#### Option B: Use the Example Bot Script

1. **Edit the bot script** (`example_bot.py`):
   ```python
   FLASK_SERVER_URL = "http://192.168.12.100:3000"  # Your server's IP
   RECIPIENT_EXTERNAL_ID = None  # Set to broadcast, or specific user ID
   ```

2. **Run the bot**:
   ```bash
   # Default test message
   uv run python example_bot.py

   # Custom title
   uv run python example_bot.py "Hello from Bot"

   # Custom title and content
   uv run python example_bot.py "Server Alert" "Backup completed"
   ```

#### Option C: Use curl

```bash
# Get current timestamp in milliseconds
TIMESTAMP=$(date +%s000)

curl -X POST http://localhost:3000/api/send-notification \
  -H "Content-Type: application/json" \
  -d "{
    \"bot_id\": \"test_bot\",
    \"title\": \"Test Notification\",
    \"content\": \"Testing from curl\",
    \"timestamp\": $TIMESTAMP
  }"
```

### Step 3: Verify Notifications

- **Desktop**: Notification appears in system notification area
- **Mobile**: Push notification banner appears
- **PWA**: Local notification may also appear within the app

### Troubleshooting

#### Subscription Issues
- Check browser console for JavaScript errors
- Verify VAPID keys are correctly configured in `.env`
- Ensure you're using HTTPS for mobile testing (localhost works for desktop)

#### Notification Delivery Issues
- Check Flask server logs for errors
- Verify bot is running on allowed IP (matches `ALLOWED_BOT_IPS`)
- Check timestamp is within 5-minute window
- Ensure user external ID matches subscribed user

#### Bot Connection Issues
- Verify Flask server is running on port 3000
- Check `FLASK_SERVER_URL` in `example_bot.py` matches your server
- Ensure bot can reach server (same network or Tailscale)

#### pywebpush Errors
- Verify VAPID keys are valid and properly formatted
- Check subscription data is correctly stored/retrieved
- Ensure push service (FCM/APNs) can reach your device

### Automated Testing

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/unit/test_auth_service.py

# Run single test
uv run pytest tests/unit/test_auth_service.py::TestAuthService::test_generate_user_jwt_with_email

# Run with verbose output
uv run pytest -v

# Run tests matching keyword
uv run pytest -k "jwt"
```

## Development & Code Quality

### Code Quality Tools

```bash
# Linting and auto-fix
uv run ruff check .
uv run ruff check --fix .

# Code formatting
uv run ruff format .

# Type checking
uv run mypy .
```

### Architecture Overview

#### Backend Architecture
- **Application Factory Pattern**: Clean Flask app initialization
- **Service Layer**: Separates business logic from routes
- **Configuration Management**: Environment-based configuration
- **Security Utilities**: IP validation and timestamp checking

#### Push Notification Flow
1. **Frontend**: User subscribes via Web Push API
2. **Service Worker**: Handles push events and displays notifications
3. **Backend**: Stores subscriptions and processes bot requests
4. **pywebpush**: Sends notifications directly to push services (FCM/APNs)

#### Security Model
- **Frontend**: Any device can access PWA (no authentication required)
- **Bot API**: IP whitelist + timestamp validation + optional JWT
- **Push Subscriptions**: Stored locally with user external IDs
- **Network Security**: Designed for local networks with Tailscale support

### Deployment Considerations

#### Local Network Deployment
- Run Flask server on local machine (`localhost:3000`)
- Configure `ALLOWED_BOT_IPS` to match your network subnet
- Any device on network can access PWA
- Only authorized bots can send notifications

#### Tailscale VPN Deployment
- Configure `ALLOWED_BOT_IPS` to match Tailscale subnet (usually `100.64.0.`)
- Enables secure remote access for both PWA and bot scripts
- Maintains same security model across networks

#### Production Considerations
- Set `FLASK_SECRET_KEY` for session security
- Consider enabling JWT authentication for bot requests
- Use HTTPS for mobile PWA installation
- Monitor server logs for security events

## Contributing

This is a template repository designed for easy customization. Key areas for extension:

- User authentication system (Google/GitHub OAuth)
- Database integration for user management
- Advanced notification scheduling
- Push notification analytics
- Multi-device user management

## License

This template is provided as-is for building your own PWA applications. Modify and distribute according to your needs.
