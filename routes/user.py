import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import Topic, Request
from extensions import db
import uuid

user_bp = Blueprint('user', __name__)

def allowed_file(filename):
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config['ALLOWED_EXTENSIONS']

def get_file_extension(filename):
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

@user_bp.route('/dashboard')
@login_required
def dashboard():
    requests = Request.query.filter_by(user_id=current_user.id)\
                           .order_by(Request.created_at.desc()).all()
    return render_template('user/dashboard.html', requests=requests)

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_request():
    topics = Topic.query.order_by(Topic.title).all()
    
    if not topics:
        flash('Ҳоло мавзӯъҳо нестанд. Лутфан баъдтар кӯшиш кунед.', 'warning')
        return redirect(url_for('user.dashboard'))
    
    if request.method == 'POST':
        topic_id = request.form.get('topic_id', type=int)
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)
        comment = request.form.get('comment', '').strip()
        
        if not topic_id:
            flash('Мавзӯъро интихоб кунед.', 'danger')
            return render_template('user/create_request.html', topics=topics)
        
        topic = Topic.query.get(topic_id)
        if not topic:
            flash('Мавзӯъи интихобшуда ёфт нашуд.', 'danger')
            return render_template('user/create_request.html', topics=topics)
        
        media_filename = None
        if 'media' in request.files:
            file = request.files['media']
            if file and file.filename and allowed_file(file.filename):
                ext = get_file_extension(file.filename)
                unique_filename = f"{uuid.uuid4().hex}.{ext}"
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                media_filename = unique_filename
            elif file and file.filename and not allowed_file(file.filename):
                flash('Формати файл иҷозат дода нашудааст. Танҳо расм ва видео иҷозат аст.', 'danger')
                return render_template('user/create_request.html', topics=topics)
        
        new_request = Request(
            user_id=current_user.id,
            topic_id=topic_id,
            latitude=latitude,
            longitude=longitude,
            comment=comment,
            media_filename=media_filename,
            status='new'
        )
        
        db.session.add(new_request)
        db.session.commit()
        
        flash('Дархости шумо бо муваффақият фиристода шуд!', 'success')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/create_request.html', topics=topics)

@user_bp.route('/request/<int:id>')
@login_required
def view_request(id):
    req = Request.query.get_or_404(id)
    
    if req.user_id != current_user.id and not current_user.is_admin():
        flash('Шумо ба ин дархост дастрасӣ надоред.', 'danger')
        return redirect(url_for('user.dashboard'))
    
    return render_template('user/view_request.html', request=req)
