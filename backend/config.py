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

        # Check for CA-signed certificates
        cert_file = Config.SERVER_CERT
        key_file = Config.SERVER_KEY
        ca_file = Config.CA_CERT
        
        missing_files = []
        if not os.path.exists(cert_file):
            missing_files.append("server.cert.pem")
        if not os.path.exists(key_file):
            missing_files.append("server.key.pem")
        if not os.path.exists(ca_file):
            missing_files.append("ca.cert.pem")
            
        if missing_files:
            print("=" * 60)
            print("SSL CERTIFICATES MISSING!")
            print("=" * 60)
            print(f"Missing files: {', '.join(missing_files)}")
            print("\nTo create the required certificates:")
            print("1. Run 'create_ca.bat' to create the ENAGEO Certificate Authority")
            print("2. Run 'create_server_cert.bat' to create the server certificate")
            print("\nThese batch files will:")
            print("- Create a proper CA with encrypted private key")
            print("- Generate server certificate signed by the CA")
            print("- Place all certificates in the correct locations")
            print("=" * 60)
            raise FileNotFoundError(f"SSL certificates not found: {', '.join(missing_files)}")
        
        print("✓ SSL certificates found and ready to use")
        print(f"  - Server certificate: {cert_file}")
        print(f"  - Server private key: {key_file}")
        print(f"  - CA certificate: {ca_file}") 