from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import User, Topic, Request
from extensions import db

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Шумо ба ин саҳифа дастрасӣ надоред.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    topic_filter = request.args.get('topic', type=int)
    status_filter = request.args.get('status', type=str)
    
    query = Request.query.order_by(Request.created_at.desc())
    
    if topic_filter:
        query = query.filter_by(topic_id=topic_filter)
    
    if status_filter and status_filter in Request.STATUS_LABELS:
        query = query.filter_by(status=status_filter)
    
    requests = query.all()
    topics = Topic.query.order_by(Topic.title).all()
    statuses = Request.STATUS_LABELS
    
    return render_template('admin/dashboard.html', 
                         requests=requests, 
                         topics=topics,
                         statuses=statuses,
                         selected_topic=topic_filter,
                         selected_status=status_filter)

@admin_bp.route('/topics')
@login_required
@admin_required
def topics():
    topics = Topic.query.order_by(Topic.created_at.desc()).all()
    return render_template('admin/topics.html', topics=topics)

@admin_bp.route('/topics/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_topic():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        color = request.form.get('color', '#40916c').strip()
        
        if not title:
            flash('Номи мавзӯъ лозим аст.', 'danger')
            return render_template('admin/topic_form.html', topic=None)
        
        existing = Topic.query.filter_by(title=title).first()
        if existing:
            flash('Ин мавзӯъ аллакай мавҷуд аст.', 'danger')
            return render_template('admin/topic_form.html', topic=None)
        
        topic = Topic(title=title, color=color)
        db.session.add(topic)
        db.session.commit()
        
        flash('Мавзӯъ бо муваффақият илова карда шуд.', 'success')
        return redirect(url_for('admin.topics'))
    
    return render_template('admin/topic_form.html', topic=None)

@admin_bp.route('/topics/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_topic(id):
    topic = Topic.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        color = request.form.get('color', '#40916c').strip()
        
        if not title:
            flash('Номи мавзӯъ лозим аст.', 'danger')
            return render_template('admin/topic_form.html', topic=topic)
        
        existing = Topic.query.filter(Topic.title == title, Topic.id != id).first()
        if existing:
            flash('Ин мавзӯъ аллакай мавҷуд аст.', 'danger')
            return render_template('admin/topic_form.html', topic=topic)
        
        topic.title = title
        topic.color = color
        db.session.commit()
        
        flash('Мавзӯъ бо муваффақият таҳрир карда шуд.', 'success')
        return redirect(url_for('admin.topics'))
    
    return render_template('admin/topic_form.html', topic=topic)

@admin_bp.route('/topics/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_topic(id):
    topic = Topic.query.get_or_404(id)
    
    if topic.requests:
        flash('Ин мавзӯъро нест кардан мумкин нест, зеро дархостҳо доранд.', 'danger')
        return redirect(url_for('admin.topics'))
    
    db.session.delete(topic)
    db.session.commit()
    
    flash('Мавзӯъ бо муваффақият нест карда шуд.', 'success')
    return redirect(url_for('admin.topics'))

@admin_bp.route('/requests/<int:id>/status', methods=['POST'])
@login_required
@admin_required
def update_status(id):
    req = Request.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in Request.STATUS_LABELS:
        req.status = new_status
        db.session.commit()
        flash('Ҳолати дархост бо муваффақият тағйир дода шуд.', 'success')
    else:
        flash('Ҳолати нодуруст интихоб шуд.', 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('Номи корбар ва рамз лозим аст.', 'danger')
            return render_template('admin/user_form.html', user=None)
        
        if len(password) < 6:
            flash('Рамз бояд ҳадди ақал 6 аломат дошта бошад.', 'danger')
            return render_template('admin/user_form.html', user=None)
        
        if password != confirm_password:
            flash('Рамзҳо мувофиқат намекунанд.', 'danger')
            return render_template('admin/user_form.html', user=None)
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Ин номи корбар аллакай истифода шудааст.', 'danger')
            return render_template('admin/user_form.html', user=None)
        
        if role not in ['user', 'admin']:
            role = 'user'
        
        user = User(username=username, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Корбар бо муваффақият илова карда шуд.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', user=None)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('Шумо худро нест карда наметавонед.', 'danger')
        return redirect(url_for('admin.users'))
    
    if user.requests:
        flash('Ин корбарро нест кардан мумкин нест, зеро дархостҳо доранд.', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('Корбар бо муваффақият нест карда шуд.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/map')
@login_required
@admin_required
def admin_map():
    topics = Topic.query.order_by(Topic.title).all()
    requests_with_location = Request.query.filter(
        Request.latitude.isnot(None),
        Request.longitude.isnot(None)
    ).all()
    
    requests_data = []
    for req in requests_with_location:
        requests_data.append({
            'id': req.id,
            'lat': req.latitude,
            'lng': req.longitude,
            'topic_id': req.topic_id,
            'topic_title': req.topic.title,
            'topic_color': req.topic.color,
            'status': req.status,
            'status_label': req.get_status_label(),
            'comment': req.comment or '',
            'author': req.author.username,
            'created_at': req.created_at.strftime('%d.%m.%Y %H:%M')
        })
    
    return render_template('admin/map.html', topics=topics, requests_data=requests_data)
