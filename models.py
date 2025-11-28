from datetime import datetime
from flask_login import UserMixin
from extensions import db, bcrypt

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(150), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    requests = db.relationship('Request', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Topic(db.Model):
    __tablename__ = 'topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    color = db.Column(db.String(7), nullable=False, default='#40916c')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    requests = db.relationship('Request', backref='topic', lazy=True)
    
    def __repr__(self):
        return f'<Topic {self.title}>'

class Request(db.Model):
    __tablename__ = 'requests'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    media_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='new')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    STATUS_LABELS = {
        'new': 'Нав',
        'in_progress': 'Дар баррасӣ',
        'completed': 'Иҷро шуд',
        'rejected': 'Рад шуд'
    }
    
    STATUS_CLASSES = {
        'new': 'primary',
        'in_progress': 'warning',
        'completed': 'success',
        'rejected': 'danger'
    }
    
    def get_status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)
    
    def get_status_class(self):
        return self.STATUS_CLASSES.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<Request {self.id}>'
