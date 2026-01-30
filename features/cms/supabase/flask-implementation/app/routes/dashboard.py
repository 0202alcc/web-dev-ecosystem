from flask import Blueprint, render_template, session, current_app
from supabase import Client
from app.routes.auth import login_required

bp = Blueprint('dashboard', __name__)


@bp.route('/')
@bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard page.
    Displays both local cache (client-side) and remote database sections.
    Fetches user config and remote data for server-side rendering.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    # Fetch user config
    config_response = supabase.table('user_configs').select('config').eq('user_id', user_id).execute()
    config = config_response.data[0]['config'] if config_response.data else {
        "headers": ["timestamp", "id", "content"],
        "eviction": {
            "method": "fifo",
            "enabled": True,
            "limit": 10
        }
    }

    # Fetch remote data
    content_response = supabase.table('user_content').select('*').eq('user_id', user_id).order('timestamp', desc=True).execute()
    remote_data = content_response.data

    return render_template(
        'dashboard.html',
        user=session['user'],
        config=config,
        remote_data=remote_data
    )
