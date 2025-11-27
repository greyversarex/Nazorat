from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from models import User, Topic, Request
from app import db

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
    
    query = Request.query.order_by(Request.created_at.desc())
    
    if topic_filter:
        query = query.filter_by(topic_id=topic_filter)
    
    requests = query.all()
    topics = Topic.query.order_by(Topic.title).all()
    
    return render_template('admin/dashboard.html', 
                         requests=requests, 
                         topics=topics,
                         selected_topic=topic_filter)

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
        
        if not title:
            flash('Номи мавзӯъ лозим аст.', 'danger')
            return render_template('admin/topic_form.html', topic=None)
        
        existing = Topic.query.filter_by(title=title).first()
        if existing:
            flash('Ин мавзӯъ аллакай мавҷуд аст.', 'danger')
            return render_template('admin/topic_form.html', topic=None)
        
        topic = Topic(title=title)
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
        
        if not title:
            flash('Номи мавзӯъ лозим аст.', 'danger')
            return render_template('admin/topic_form.html', topic=topic)
        
        existing = Topic.query.filter(Topic.title == title, Topic.id != id).first()
        if existing:
            flash('Ин мавзӯъ аллакай мавҷуд аст.', 'danger')
            return render_template('admin/topic_form.html', topic=topic)
        
        topic.title = title
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
