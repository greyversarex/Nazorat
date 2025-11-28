import os
from flask import Flask
from extensions import db, bcrypt, login_manager, csrf

def migrate_add_topic_color():
    from sqlalchemy import text, inspect
    try:
        inspector = inspect(db.engine)
        if 'topics' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('topics')]
            if 'color' not in columns:
                db.session.execute(text("ALTER TABLE topics ADD COLUMN color VARCHAR(7) DEFAULT '#40916c'"))
                db.session.execute(text("UPDATE topics SET color = '#40916c' WHERE color IS NULL"))
                db.session.commit()
                print('Migration: Added color column to topics table')
    except Exception as e:
        print(f'Migration check: {e}')

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
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'webm'}
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(basedir, 'instance'), exist_ok=True)
    
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
    
    with app.app_context():
        db.create_all()
        migrate_add_topic_color()
        create_default_admin()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
