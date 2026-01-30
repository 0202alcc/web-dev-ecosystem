import uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, session, current_app
from supabase import Client
from app.routes.auth import login_required

bp = Blueprint('data', __name__, url_prefix='/api')


@bp.route('/content', methods=['GET'])
@login_required
def get_content():
    """
    Get all content for the current user.
    Returns JSON array of content rows filtered by user_id via RLS.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        response = supabase.table('user_content').select('*').eq('user_id', user_id).order('timestamp', desc=True).execute()

        return jsonify({
            'success': True,
            'data': response.data
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/content', methods=['POST'])
@login_required
def add_content():
    """
    Add new content row for the current user.
    Auto-generates ID and timestamp.

    Expected JSON body:
    {
        "content": "markdown text"
    }
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        data = request.get_json()
        content = data.get('content', '')

        # Create new row with auto-generated ID and timestamp
        new_row = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': content
        }

        response = supabase.table('user_content').insert(new_row).execute()

        return jsonify({
            'success': True,
            'data': response.data[0] if response.data else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/content/<content_id>', methods=['PUT'])
@login_required
def update_content(content_id):
    """
    Update existing content row.
    RLS ensures users can only update their own content.

    Expected JSON body:
    {
        "content": "updated markdown text"
    }
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        data = request.get_json()
        content = data.get('content')

        if content is None:
            return jsonify({
                'success': False,
                'error': 'Content field is required'
            }), 400

        # Update content (RLS ensures user owns this row)
        response = supabase.table('user_content').update({
            'content': content,
            'timestamp': datetime.now(timezone.utc).isoformat()  # Update timestamp
        }).eq('id', content_id).eq('user_id', user_id).execute()

        return jsonify({
            'success': True,
            'data': response.data[0] if response.data else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/content/<content_id>', methods=['DELETE'])
@login_required
def delete_content(content_id):
    """
    Delete content row.
    RLS ensures users can only delete their own content.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        # Delete content (RLS ensures user owns this row)
        response = supabase.table('user_content').delete().eq('id', content_id).eq('user_id', user_id).execute()

        return jsonify({
            'success': True,
            'message': 'Content deleted successfully'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/config', methods=['GET'])
@login_required
def get_config():
    """
    Get user configuration.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        response = supabase.table('user_configs').select('config').eq('user_id', user_id).execute()

        if response.data:
            return jsonify({
                'success': True,
                'config': response.data[0]['config']
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Config not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@bp.route('/dummy', methods=['POST'])
@login_required
def generate_dummy():
    """
    Generate dummy content for testing.
    Creates a sample row with auto-generated data.
    """
    supabase: Client = current_app.supabase
    user_id = session['user']['id']

    try:
        # Get custom content from request or use default
        data = request.get_json() or {}
        custom_content = data.get('content', f'# Auto-generated Content\n\nThis is dummy content generated at {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")} UTC.\n\nYou can customize this via the form or API.')

        new_row = {
            'id': str(uuid.uuid4()),
            'user_id': user_id,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'content': custom_content
        }

        response = supabase.table('user_content').insert(new_row).execute()

        return jsonify({
            'success': True,
            'data': response.data[0] if response.data else None
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
