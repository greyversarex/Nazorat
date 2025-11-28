from flask import Blueprint, redirect, url_for, send_from_directory, current_app, request
from flask_login import current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    user_agent = request.headers.get('User-Agent', '').lower()
    if 'healthcheck' in user_agent or 'replit' in user_agent or request.args.get('health') == '1':
        return 'OK', 200
    
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/health')
def health_check():
    return 'OK', 200

@main_bp.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@main_bp.route('/sw.js')
def service_worker():
    response = send_from_directory('static/js', 'sw.js')
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Cache-Control'] = 'no-cache'
    return response
