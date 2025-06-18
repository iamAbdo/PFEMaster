import os
from datetime import timedelta

class Config:
    # Base directory of the application
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    # Database
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dev-secret-key')  # Change in production
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # File upload settings
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # SSL/TLS Configuration
    SSL_CERT_DIR = os.path.join(BASE_DIR, 'certs')
    SERVER_CERT = os.path.join(SSL_CERT_DIR, 'server.cert.pem')
    SERVER_KEY = os.path.join(SSL_CERT_DIR, 'server.key.pem')
    CA_CERT = os.path.join(SSL_CERT_DIR, 'ca.cert.pem')
    
    # Server settings
    HOST = 'localhost'
    PORT = 5000
    
    # Create required directories
    @staticmethod
    def init_app():
        os.makedirs(os.path.join(Config.BASE_DIR, 'instance'), exist_ok=True)
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(Config.SSL_CERT_DIR, exist_ok=True) 