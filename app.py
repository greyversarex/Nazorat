import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from extensions import db, bcrypt, login_manager, csrf

def migrate_add_topic_color():
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'topics' in tables:
            columns = [col['name'] for col in inspector.get_columns('topics')]
            if 'color' not in columns:
                db.session.execute(text("ALTER TABLE topics ADD COLUMN color VARCHAR(7) DEFAULT '#40916c'"))
                db.session.execute(text("UPDATE topics SET color = '#40916c' WHERE color IS NULL"))
                db.session.commit()
                print('Migration: Added color column to topics table')
    except Exception as e:
        db.session.rollback()
        print(f'Migration check: {e}')

def migrate_add_user_full_name():
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'users' in tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'full_name' not in columns:
                db.session.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(150)"))
                db.session.commit()
                print('Migration: Added full_name column to users table')
    except Exception as e:
        db.session.rollback()
        print(f'Migration check: {e}')

def migrate_nullable_user_id():
    pass

def migrate_add_reply_fields():
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'requests' not in tables:
            return
        columns = [col['name'] for col in inspector.get_columns('requests')]
        
        if 'reply' not in columns:
            db.session.execute(text("ALTER TABLE requests ADD COLUMN reply TEXT"))
            db.session.commit()
            print('Migration: Added reply column to requests')
        
        if 'replied_at' not in columns:
            db.session.execute(text("ALTER TABLE requests ADD COLUMN replied_at TIMESTAMP"))
            db.session.commit()
            print('Migration: Added replied_at column to requests')
        
        db.session.execute(text("UPDATE requests SET status = 'under_review' WHERE status IN ('new', 'in_progress', 'rejected')"))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f'Migration reply fields: {e}')

def migrate_add_reg_number():
    from sqlalchemy import inspect, text
    from models import Request
    from datetime import datetime
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'requests' not in tables:
            return
        columns = [col['name'] for col in inspector.get_columns('requests')]
        
        if 'reg_number' not in columns:
            db.session.execute(text("ALTER TABLE requests ADD COLUMN reg_number VARCHAR(20) UNIQUE"))
            db.session.commit()
            print('Migration: Added reg_number column to requests')
        
        requests_without_reg = Request.query.filter(Request.reg_number.is_(None)).order_by(Request.id).all()
        for req in requests_without_reg:
            year = req.created_at.year if req.created_at else datetime.now().year
            count = Request.query.filter(
                Request.reg_number.like(f'NAZ-{year}-%'),
                Request.id < req.id
            ).count() + 1
            req.reg_number = f'NAZ-{year}-{count:04d}'
        
        if requests_without_reg:
            db.session.commit()
            print(f'Migration: Generated reg_numbers for {len(requests_without_reg)} existing requests')
    except Exception as e:
        db.session.rollback()
        print(f'Migration reg_number: {e}')

def migrate_add_document_number():
    from sqlalchemy import inspect, text
    try:
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        if 'requests' not in tables:
            return
        columns = [col['name'] for col in inspector.get_columns('requests')]
        
        if 'document_number' not in columns:
            db.session.execute(text("ALTER TABLE requests ADD COLUMN document_number VARCHAR(100)"))
            db.session.commit()
            print('Migration: Added document_number column to requests')
    except Exception as e:
        db.session.rollback()
        print(f'Migration document_number: {e}')

def create_default_admin():
    from models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: username=admin, password=admin123')

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')
    
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_recycle': 300,
        'pool_pre_ping': True
    }
    
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm', 'pdf', 'doc', 'docx'}
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    from models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.user import user_bp
    from routes.main import main_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    
    @app.after_request
    def add_cache_control(response):
        if 'text/html' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
        elif 'text/css' in response.content_type or 'application/javascript' in response.content_type:
            response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        return response
    
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    with app.app_context():
        db.create_all()
        migrate_add_topic_color()
        migrate_add_user_full_name()
        migrate_nullable_user_id()
        migrate_add_reply_fields()
        migrate_add_reg_number()
        migrate_add_document_number()
        create_default_admin()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
