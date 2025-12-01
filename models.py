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
    reg_number = db.Column(db.String(20), unique=True, nullable=True)
    document_number = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    media_filename = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='under_review')
    reply = db.Column(db.Text, nullable=True)
    replied_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @staticmethod
    def generate_reg_number():
        """Generate registration number like NAZ-2025-0001"""
        from datetime import datetime
        year = datetime.now().year
        last_request = Request.query.filter(
            Request.reg_number.like(f'NAZ-{year}-%')
        ).order_by(Request.id.desc()).first()
        
        if last_request and last_request.reg_number:
            try:
                last_num = int(last_request.reg_number.split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'NAZ-{year}-{new_num:04d}'
    
    @staticmethod
    def generate_document_number():
        """Generate document number like DOC-2025-0001"""
        from datetime import datetime
        year = datetime.now().year
        last_request = Request.query.filter(
            Request.document_number.like(f'DOC-{year}-%')
        ).order_by(Request.id.desc()).first()
        
        if last_request and last_request.document_number:
            try:
                last_num = int(last_request.document_number.split('-')[-1])
                new_num = last_num + 1
            except:
                new_num = 1
        else:
            new_num = 1
        
        return f'DOC-{year}-{new_num:04d}'
    
    STATUS_LABELS = {
        'under_review': 'Дар тафтиш',
        'completed': 'Иҷро шуд'
    }
    
    STATUS_CLASSES = {
        'under_review': 'warning',
        'completed': 'success'
    }
    
    def get_status_label(self):
        return self.STATUS_LABELS.get(self.status, self.status)
    
    def get_status_class(self):
        return self.STATUS_CLASSES.get(self.status, 'secondary')
    
    def __repr__(self):
        return f'<Request {self.id}>'
