from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from .models import db
#from .auth import auth_bp, init_ssl_context
from .auth import auth_bp
from .user_routes import user_bp
from .admin_routes import admin_bp
from .user_management import user_management_bp
from .zone_routes import zone_bp

def create_app(config_object):
    app = Flask(__name__)
    app.config.from_object(config_object)
    
    # Initialize extensions
    CORS(app)
    JWTManager(app)
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        from .models import User, Zone
        db.create_all()
        
        # Create admin user if none exists
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                email='admin@example.com',
                is_admin=True,
                role='Responsable'
            )
            admin.set_password('admin123')  # Change this in production
            db.session.add(admin)
            db.session.commit()
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_management_bp, url_prefix='/api/user-management')
    app.register_blueprint(zone_bp, url_prefix='/api/zone')
    
    @app.route('/chrome')
    def chrome_debug():
        return 'Debug: Chrome route is working!'
    
    return app 