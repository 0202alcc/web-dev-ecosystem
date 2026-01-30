import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from supabase import Client
from app.routes.auth import login_required

bp = Blueprint('profile', __name__, url_prefix='/profile')


@bp.route('/')
@login_required
def index():
    """
    Display user profile with identity provider metadata and config editing.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    # Fetch user config
    config_response = supabase.table('user_configs').select('*').eq('user_id', user_id).execute()

    config = config_response.data[0]['config'] if config_response.data else None

    # Get full user identities from session
    identities = session['user'].get('identities', [])

    return render_template(
        'profile.html',
        user=session['user'],
        identities=identities,
        config=config
    )


@bp.route('/config/update', methods=['POST'])
@login_required
def update_config():
    """
    Update user configuration.
    Accepts JSON string from textarea and updates the config.

    Future validation to add:
    - Ensure 'headers' list is not empty
    - Validate eviction method is one of allowed values
    - Validate limit is positive integer
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        # Parse the config JSON from form
        config_str = request.form.get('config')
        config = json.loads(config_str)

        # Update config in database
        supabase.table('user_configs').update({
            'config': config
        }).eq('user_id', user_id).execute()

        flash('Configuration updated successfully! Changes will apply on next page refresh.', 'success')

    except json.JSONDecodeError as e:
        flash(f'Invalid JSON format: {str(e)}', 'error')
    except Exception as e:
        flash(f'Error updating configuration: {str(e)}', 'error')

    return redirect(url_for('profile.index'))


@bp.route('/link-account')
@login_required
def link_account():
    """
    Account linking page.
    Allows users to link multiple OAuth providers to a single account.

    TODO: Implement multi-provider linking
    - Display currently linked providers
    - Provide buttons to link additional providers (Google, Claremont)
    - Handle merging of user data if needed
    """
    return render_template(
        'link_account.html',
        user=session['user']
    )


@bp.route('/link/manual', methods=['POST'])
@login_required
def link_manual():
    """
    Manual account linking via email.
    Fallback for providers without OAuth support (e.g., Claremont SSO if SAML-only).

    TODO: Implement email-based account merging
    - Verify secondary email ownership
    - Merge user data from both accounts
    - Update user_id references in content/config tables
    """
    email = request.form.get('email')

    # Placeholder implementation
    flash(f'Manual linking for {email} is not yet implemented. Coming soon!', 'info')

    return redirect(url_for('profile.link_account'))
