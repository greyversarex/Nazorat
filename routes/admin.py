from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, send_file
from flask_login import login_required, current_user
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func
from models import User, Topic, Request
from extensions import db
from services.statistics_export import (
    create_statistics_word_document,
    create_statistics_excel_document,
    create_worker_statistics_word_document,
    create_worker_statistics_excel_document
)

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
    return redirect(url_for('admin.admin_home'))

@admin_bp.route('/search')
@login_required
@admin_required
def search_requests():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])
    
    search_term = f'%{q}%'
    results = Request.query.outerjoin(User, Request.user_id == User.id).outerjoin(Topic, Request.topic_id == Topic.id).filter(
        db.or_(
            Request.reg_number.ilike(search_term),
            Request.document_number.ilike(search_term),
            Request.comment.ilike(search_term),
            User.username.ilike(search_term),
            User.full_name.ilike(search_term),
            Topic.title.ilike(search_term)
        )
    ).order_by(Request.created_at.desc()).limit(10).all()
    
    suggestions = []
    for req in results:
        suggestions.append({
            'id': req.id,
            'reg_number': req.reg_number or f'#{req.id}',
            'document_number': req.document_number or '',
            'topic': req.topic.title if req.topic else '',
            'author': req.author.full_name or req.author.username if req.author else 'Нест шуд',
            'comment': (req.comment[:50] + '...' if req.comment and len(req.comment) > 50 else req.comment) or '',
            'status': req.get_status_label(),
            'status_class': req.get_status_class(),
            'date': req.created_at.strftime('%d.%m.%Y')
        })
    
    return jsonify(suggestions)

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
    
    if new_status in ['under_review', 'completed']:
        req.status = new_status
        if new_status == 'completed' and req.admin_read_at is None:
            req.admin_read_at = datetime.utcnow()
        db.session.commit()
        flash('Ҳолати дархост бо муваффақият тағйир дода шуд.', 'success')
    else:
        flash('Ҳолати нодуруст интихоб шуд.', 'danger')
    
    return redirect(url_for('admin.protocols'))

@admin_bp.route('/requests/<int:id>/complete', methods=['POST'])
@login_required
@admin_required
def complete_request(id):
    req = Request.query.get_or_404(id)
    req.status = 'completed'
    if req.admin_read_at is None:
        req.admin_read_at = datetime.utcnow()
    db.session.commit()
    flash('Дархост иҷро шуд.', 'success')
    redirect_to = request.form.get('redirect_to')
    if redirect_to:
        return redirect(redirect_to)
    return redirect(url_for('admin.protocols'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/<int:id>/requests')
@login_required
@admin_required
def user_requests(id):
    user = User.query.get_or_404(id)
    requests_list = Request.query.filter_by(user_id=id).order_by(Request.created_at.desc()).all()
    topics = Topic.query.order_by(Topic.title).all()
    return render_template('admin/user_requests.html', user=user, requests=requests_list, topics=topics)

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
        
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            from werkzeug.utils import secure_filename
            import uuid
            filename = secure_filename(avatar_file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
            if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                new_filename = f"avatar_{uuid.uuid4().hex}.{ext}"
                avatar_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename))
                user.avatar = new_filename
        
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
        
        avatar_file = request.files.get('avatar')
        if avatar_file and avatar_file.filename:
            from werkzeug.utils import secure_filename
            import uuid
            filename = secure_filename(avatar_file.filename)
            ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
            if ext in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                if user.avatar:
                    old_avatar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], user.avatar)
                    if os.path.exists(old_avatar_path):
                        os.remove(old_avatar_path)
                new_filename = f"avatar_{uuid.uuid4().hex}.{ext}"
                avatar_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], new_filename))
                user.avatar = new_filename
        
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

@admin_bp.route('/requests/<int:id>/update-reg-number', methods=['POST'])
@login_required
@admin_required
def update_reg_number(id):
    req = Request.query.get_or_404(id)
    new_reg_number = request.form.get('reg_number', '').strip()
    
    if not new_reg_number:
        return jsonify({'success': False, 'error': 'Рақами қайд холӣ аст'}), 400
    
    existing = Request.query.filter(Request.reg_number == new_reg_number, Request.id != id).first()
    if existing:
        return jsonify({'success': False, 'error': 'Ин рақам аллакай истифода шудааст'}), 400
    
    req.reg_number = new_reg_number
    db.session.commit()
    
    return jsonify({'success': True, 'reg_number': new_reg_number})

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
    
    return redirect(url_for('admin.protocols'))

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


@admin_bp.route('/statistics/download/<format>')
@login_required
@admin_required
def download_statistics(format):
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
    
    total_users = User.query.filter(User.role == 'user').count()
    total_admins = User.query.filter(User.role == 'admin').count()
    completion_rate = round((completed_requests / total_requests * 100), 1) if total_requests > 0 else 0
    
    stats_data = {
        'total_requests': total_requests,
        'completed_requests': completed_requests,
        'under_review_requests': under_review_requests,
        'completion_rate': completion_rate,
        'topic_stats': topic_stats,
        'total_users': total_users,
        'total_admins': total_admins
    }
    
    date_range = None
    if date_from and date_to:
        date_range = f"{date_from} - {date_to}"
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'word':
        buffer = create_statistics_word_document(stats_data, date_range=date_range)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'omor_{timestamp}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    elif format == 'excel':
        buffer = create_statistics_excel_document(stats_data, date_range=date_range)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'omor_{timestamp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash('Формати нодуруст интихоб шуд.', 'danger')
        return redirect(url_for('admin.statistics'))


@admin_bp.route('/users/<int:id>/statistics/download/<format>')
@login_required
@admin_required
def download_user_statistics(id, format):
    user = User.query.get_or_404(id)
    
    requests_list = Request.query.filter_by(user_id=id).order_by(Request.created_at.desc()).all()
    
    worker_data = {
        'username': user.username,
        'full_name': user.full_name or user.username,
        'role': user.role,
        'created_at': user.created_at.strftime('%d.%m.%Y') if user.created_at else ''
    }
    
    requests_data = []
    for req in requests_list:
        requests_data.append({
            'reg_number': req.reg_number or f'#{req.id}',
            'topic': req.topic.title if req.topic else '',
            'created_at': req.created_at.strftime('%d.%m.%Y %H:%M') if req.created_at else '',
            'status': req.status,
            'status_label': req.get_status_label(),
            'comment': req.comment or ''
        })
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    safe_username = user.username.replace(' ', '_')
    
    if format == 'word':
        buffer = create_worker_statistics_word_document(worker_data, requests_data)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'omor_{safe_username}_{timestamp}.docx',
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    elif format == 'excel':
        buffer = create_worker_statistics_excel_document(worker_data, requests_data)
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f'omor_{safe_username}_{timestamp}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash('Формати нодуруст интихоб шуд.', 'danger')
        return redirect(url_for('admin.user_requests', id=id))


@admin_bp.route('/home')
@login_required
@admin_required
def admin_home():
    workers = User.query.filter(User.role == 'user').order_by(User.full_name, User.username).all()
    
    worker_cards = []
    for worker in workers:
        new_count = Request.query.filter(
            Request.user_id == worker.id,
            Request.admin_read_at.is_(None),
            Request.status != 'completed'
        ).count()
        
        total_requests = Request.query.filter(Request.user_id == worker.id).count()
        
        worker_cards.append({
            'id': worker.id,
            'username': worker.username,
            'full_name': worker.full_name or worker.username,
            'avatar': worker.avatar,
            'new_count': new_count,
            'total_requests': total_requests
        })
    
    return render_template('admin/home.html', worker_cards=worker_cards)


@admin_bp.route('/protocols')
@login_required
@admin_required
def protocols():
    topic_filter = request.args.get('topic', type=int)
    status_filter = request.args.get('status', type=str)
    search_query = request.args.get('q', '').strip()
    
    query = Request.query.order_by(Request.created_at.desc())
    
    if search_query:
        search_term = f'%{search_query}%'
        query = query.outerjoin(User, Request.user_id == User.id).outerjoin(Topic, Request.topic_id == Topic.id).filter(
            db.or_(
                Request.reg_number.ilike(search_term),
                Request.document_number.ilike(search_term),
                Request.comment.ilike(search_term),
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
                Topic.title.ilike(search_term)
            )
        )
    
    if topic_filter:
        query = query.filter(Request.topic_id == topic_filter)
    
    if status_filter and status_filter in Request.STATUS_LABELS:
        if status_filter == 'new':
            query = query.filter(Request.admin_read_at.is_(None), Request.status != 'completed')
        elif status_filter == 'under_review':
            query = query.filter(Request.admin_read_at.isnot(None), Request.status != 'completed')
        elif status_filter == 'completed':
            query = query.filter(Request.status == 'completed')
    
    requests_list = query.all()
    topics = Topic.query.order_by(Topic.title).all()
    statuses = Request.STATUS_LABELS
    
    return render_template('admin/protocols.html', 
                         requests=requests_list, 
                         topics=topics,
                         statuses=statuses,
                         selected_topic=topic_filter,
                         selected_status=status_filter,
                         search_query=search_query)


@admin_bp.route('/requests/<int:id>/mark-read', methods=['POST'])
@login_required
@admin_required
def mark_request_read(id):
    req = Request.query.get_or_404(id)
    if req.admin_read_at is None:
        req.admin_read_at = datetime.utcnow()
        db.session.commit()
    return jsonify({'success': True})
