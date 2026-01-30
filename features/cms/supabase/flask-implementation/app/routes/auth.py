import uuid
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, session, request, current_app
from supabase import Client

bp = Blueprint('auth', __name__)


def login_required(f):
    """
    Decorator to protect routes that require authentication.
    Redirects to login page if user is not authenticated.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/login')
def login():
    """
    Login page with OAuth provider buttons.
    """
    return render_template('login.html')


@bp.route('/login/google')
def login_google():
    """
    Initiate Google OAuth flow.
    """
    supabase: Client = current_app.supabase

    # Get the base URL for redirect
    base_url = request.host_url.rstrip('/')

    response = supabase.auth.sign_in_with_oauth({
        "provider": "google",
        "options": {
            "redirect_to": f"{base_url}/auth/callback"
        }
    })

    return redirect(response.url)


@bp.route('/login/claremont')
def login_claremont():
    """
    Placeholder for Claremont SSO OAuth flow.
    Currently redirects to manual linking page.

    TODO: Implement when IT provides OAuth credentials
    - Get client ID, secret, auth/token endpoints from IT
    - Configure as custom OAuth provider in Supabase
    - If SAML-only, implement via Supabase Enterprise or custom proxy
    """
    return redirect(url_for('profile.link_account'))


@bp.route('/auth/callback')
def callback():
    """
    Handle OAuth callback and establish user session.
    On first login, auto-insert default config and sample data.
    """
    supabase: Client = current_app.supabase

    # Get the authorization code from query parameters
    code = request.args.get('code')
    if not code:
        return "Authentication failed: No authorization code", 400

    try:
        # Exchange code for session
        response = supabase.auth.exchange_code_for_session({
            "auth_code": code
        })

        user = response.user

        # Convert identities to JSON-serializable format
        identities_data = []
        if user.identities:
            for identity in user.identities:
                # Convert UserIdentity object to dict
                identities_data.append({
                    'id': identity.id,
                    'user_id': identity.user_id,
                    'provider': identity.provider,
                    'identity_data': identity.identity_data,
                    'created_at': identity.created_at,
                    'updated_at': identity.updated_at
                })

        # Store user info in Flask session (must be JSON serializable)
        session['user'] = {
            'id': user.id,
            'email': user.email,
            'identities': identities_data,  # Full provider metadata as dicts
            'created_at': user.created_at
        }

        # Store access token for API calls
        session['access_token'] = response.session.access_token

        # Check if this is first login by looking for existing config
        config_response = supabase.table('user_configs').select('*').eq('user_id', user.id).execute()

        if not config_response.data:
            # First login - insert default config and sample data
            _initialize_new_user(supabase, user.id)

        return redirect(url_for('dashboard.index'))

    except Exception as e:
        print(f"Authentication error: {e}")
        return f"Authentication failed: {str(e)}", 400


@bp.route('/logout')
def logout():
    """
    Log out the current user and clear session.
    """
    supabase: Client = current_app.supabase

    try:
        supabase.auth.sign_out()
    except Exception as e:
        print(f"Logout error: {e}")

    # Clear Flask session
    session.clear()

    return redirect(url_for('auth.login'))


def _initialize_new_user(supabase: Client, user_id: str):
    """
    Initialize a new user with default config and sample data.
    Called on first login.

    Args:
        supabase: Supabase client instance
        user_id: The user's UUID
    """
    # Insert default config
    default_config = {
        "headers": ["timestamp", "id", "content"],
        "eviction": {
            "method": "fifo",
            "enabled": True,
            "limit": 10
        }
    }

    supabase.table('user_configs').insert({
        'user_id': user_id,
        'config': default_config
    }).execute()

    # Insert 3 sample rows
    now = datetime.now(timezone.utc).isoformat()
    sample_data = [
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': now,
            'content': '# Sample 1\nThis is sample markdown content for testing.'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': now,
            'content': '# Sample 2\nAnother piece of content to demonstrate the CMS.'
        },
        {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': now,
            'content': '# Sample 3\nYou can edit or delete this content from the dashboard.'
        }
    ]

    for row in sample_data:
        supabase.table('user_content').insert(row).execute()

    print(f"Initialized new user {user_id} with default config and sample data")
