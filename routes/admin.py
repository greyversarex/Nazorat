from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
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
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'user')
        
        if not username or not password:
            flash('Номи корбар ва рамз лозим аст.', 'danger')
            return render_template('admin/user_form.html', user=None)
        
        if not full_name:
            flash('Номи пурра (ФИО) лозим аст.', 'danger')
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
        
        user = User(username=username, full_name=full_name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', user=None)

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'user')
        
        if not username:
            flash('Номи корбар лозим аст.', 'danger')
            return render_template('admin/user_form.html', user=user)
        
        if not full_name:
            flash('Номи пурра (ФИО) лозим аст.', 'danger')
            return render_template('admin/user_form.html', user=user)
        
        existing_user = User.query.filter(User.username == username, User.id != id).first()
        if existing_user:
            flash('Ин номи корбар аллакай истифода шудааст.', 'danger')
            return render_template('admin/user_form.html', user=user)
        
        if password:
            if len(password) < 6:
                flash('Рамз бояд ҳадди ақал 6 аломат дошта бошад.', 'danger')
                return render_template('admin/user_form.html', user=user)
            
            if password != confirm_password:
                flash('Рамзҳо мувофиқат намекунанд.', 'danger')
                return render_template('admin/user_form.html', user=user)
            
            user.set_password(password)
        
        if user.id != current_user.id:
            if role not in ['user', 'admin']:
                role = 'user'
            user.role = role
        
        user.username = username
        user.full_name = full_name
        db.session.commit()
        
        return redirect(url_for('admin.users'))
    
    return render_template('admin/user_form.html', user=user)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    user = User.query.get_or_404(id)
    
    if user.id == current_user.id:
        flash('Шумо худро нест карда наметавонед.', 'danger')
        return redirect(url_for('admin.users'))
    
    delete_option = request.form.get('delete_option', 'none')
    
    if user.requests:
        if delete_option == 'with_requests':
            for req in user.requests:
                if req.media_filename:
                    import os
                    from flask import current_app
                    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], req.media_filename)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                db.session.delete(req)
        elif delete_option == 'keep_requests':
            for req in user.requests:
                req.user_id = None
        else:
            flash('Интихоб кунед: бо дархостҳо ё бидуни онҳо.', 'warning')
            return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    return redirect(url_for('admin.users'))

@admin_bp.route('/requests/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_request(id):
    req = Request.query.get_or_404(id)
    
    if req.media_filename:
        import os
        from flask import current_app
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], req.media_filename)
        if os.path.exists(filepath):
            os.remove(filepath)
    
    db.session.delete(req)
    db.session.commit()
    flash('Дархост бо муваффақият нест карда шуд.', 'success')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/requests/<int:id>/reply', methods=['POST'])
@login_required
@admin_required
def reply_request(id):
    from datetime import datetime
    req = Request.query.get_or_404(id)
    
    reply_text = request.form.get('reply', '').strip()
    mark_completed = request.form.get('mark_completed') == 'yes'
    
    if reply_text:
        req.reply = reply_text
        req.replied_at = datetime.utcnow()
        flash('Ҷавоб бо муваффақият фиристода шуд.', 'success')
    else:
        req.reply = None
        req.replied_at = None
        flash('Ҷавоб пок карда шуд.', 'info')
    
    if mark_completed:
        req.status = 'completed'
    else:
        req.status = 'under_review'
    
    db.session.commit()
    
    return redirect(url_for('user.view_request', id=id))

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
            'author': req.author.username if req.author else 'Нест шуд',
            'created_at': req.created_at.strftime('%d.%m.%Y %H:%M')
        })
    
    return render_template('admin/map.html', topics=topics, requests_data=requests_data)

@admin_bp.route('/statistics')
@login_required
@admin_required
def statistics():
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    query = Request.query
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(Request.created_at >= from_date)
        except ValueError:
            pass
    
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Request.created_at < to_date)
        except ValueError:
            pass
    
    total_requests = query.count()
    completed_requests = query.filter(Request.status == 'completed').count()
    under_review_requests = query.filter(Request.status == 'under_review').count()
    
    topics = Topic.query.all()
    topic_stats = []
    for topic in topics:
        topic_query = query.filter(Request.topic_id == topic.id)
        count = topic_query.count()
        completed = topic_query.filter(Request.status == 'completed').count()
        percentage = round((count / total_requests * 100), 1) if total_requests > 0 else 0
        topic_stats.append({
            'id': topic.id,
            'title': topic.title,
            'color': topic.color,
            'count': count,
            'completed': completed,
            'pending': count - completed,
            'percentage': percentage
        })
    
    topic_stats.sort(key=lambda x: x['count'], reverse=True)
    
    daily_stats = []
    if date_from and date_to:
        try:
            start = datetime.strptime(date_from, '%Y-%m-%d')
            end = datetime.strptime(date_to, '%Y-%m-%d')
            current = start
            while current <= end:
                next_day = current + timedelta(days=1)
                day_count = Request.query.filter(
                    Request.created_at >= current,
                    Request.created_at < next_day
                ).count()
                daily_stats.append({
                    'date': current.strftime('%d.%m'),
                    'count': day_count
                })
                current = next_day
        except ValueError:
            pass
    else:
        for i in range(29, -1, -1):
            day = datetime.now() - timedelta(days=i)
            next_day = day + timedelta(days=1)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = next_day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_count = Request.query.filter(
                Request.created_at >= day_start,
                Request.created_at < day_end
            ).count()
            daily_stats.append({
                'date': day.strftime('%d.%m'),
                'count': day_count
            })
    
    total_users = User.query.filter(User.role == 'user').count()
    total_admins = User.query.filter(User.role == 'admin').count()
    
    completion_rate = round((completed_requests / total_requests * 100), 1) if total_requests > 0 else 0
    
    return render_template('admin/statistics.html',
                         total_requests=total_requests,
                         completed_requests=completed_requests,
                         under_review_requests=under_review_requests,
                         topic_stats=topic_stats,
                         daily_stats=daily_stats,
                         total_users=total_users,
                         total_admins=total_admins,
                         completion_rate=completion_rate,
                         date_from=date_from,
                         date_to=date_to)
