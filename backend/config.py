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

        # Generate self-signed certs if they do not exist
        cert_file = Config.SERVER_CERT
        key_file = Config.SERVER_KEY
        if not (os.path.exists(cert_file) and os.path.exists(key_file)):
            try:
                from OpenSSL import crypto
                k = crypto.PKey()
                k.generate_key(crypto.TYPE_RSA, 2048)

                cert = crypto.X509()
                # Country: Algeria
                cert.get_subject().C  = "DZ"
                # Province: Ouargla
                cert.get_subject().ST = "Wilaya de Ouargla"
                # City / Locality: Hassi-Messaoud
                cert.get_subject().L  = "Hassi‑Messaoud"
                # Organization: ENAGEO (Entreprise Nationale de Géophysique)
                cert.get_subject().O  = "Entreprise Nationale de Géophysique"
                # Organizational Unit: IT Department
                cert.get_subject().OU = "IT Department"
                # Common Name: your server’s hostname
                cert.get_subject().CN = "backend.enageo.com"
                
                cert.set_serial_number(1000)
                cert.gmtime_adj_notBefore(0)
                cert.gmtime_adj_notAfter(10*365*24*60*60)  # 10 years
                cert.set_issuer(cert.get_subject())
                cert.set_pubkey(k)
                cert.sign(k, 'sha256')

                with open(cert_file, "wb") as f:
                    f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
                with open(key_file, "wb") as f:
                    f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
                print(f"Generated self-signed SSL certificate and key at {cert_file} and {key_file}")
            except ImportError:
                print("pyOpenSSL is not installed. Cannot generate SSL certificates.") 