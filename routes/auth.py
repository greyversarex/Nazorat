from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

def is_safe_url(target):
    if not target:
        return False
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('', 'http', 'https') and ref_url.netloc == test_url.netloc

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Номи корбар ва рамз лозим аст.', 'danger')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Шумо бо муваффақият ворид шудед!', 'success')
            
            next_page = request.args.get('next')
            if next_page and is_safe_url(next_page):
                return redirect(next_page)
            
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('user.dashboard'))
        else:
            flash('Номи корбар ё рамз нодуруст аст.', 'danger')
    
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not password:
            flash('Номи корбар ва рамз лозим аст.', 'danger')
            return render_template('auth/register.html')
        
        if len(password) < 6:
            flash('Рамз бояд ҳадди ақал 6 аломат дошта бошад.', 'danger')
            return render_template('auth/register.html')
        
        if password != confirm_password:
            flash('Рамзҳо мувофиқат намекунанд.', 'danger')
            return render_template('auth/register.html')
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ин номи корбар аллакай истифода шудааст.', 'danger')
            return render_template('auth/register.html')
        
        user = User(username=username, role='user')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Бақайдгирӣ бо муваффақият анҷом ёфт! Акнун ворид шавед.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Шумо аз система баромадед.', 'info')
    return redirect(url_for('auth.login'))
