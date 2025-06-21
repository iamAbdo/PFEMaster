from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
#from OpenSSL import SSL, crypto
from .models import db, User
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import timedelta
from .logging_utils import log_login_success, log_login_failure

auth_bp = Blueprint('auth', __name__)

#def verify_certificate(cert_str):
#    """Verify client certificate against CA"""
#    try:
#        cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_str)
#        with open(current_app.config['CA_CERT'], 'rb') as ca_file:
#            ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, ca_file.read())
#        store = crypto.X509Store()
#        store.add_cert(ca_cert)
#        store_ctx = crypto.X509StoreContext(store, cert)
#        store_ctx.verify_certificate()
#        return True, get_cert_dn(cert)
#    except Exception as e:
#        return False, str(e)
#
#def get_cert_dn(cert):
#    """Extract Distinguished Name from certificate"""
#    return str(cert.get_subject())
#
#def require_cert(f):
#    """Decorator to require valid client certificate"""
#    @wraps(f)
#    def decorated_function(*args, **kwargs):
#        if not request.environ.get('SSL_CLIENT_CERT'):
#            return jsonify({'error': 'Client certificate required'}), 401
#        valid, dn = verify_certificate(request.environ['SSL_CLIENT_CERT'])
#        if not valid:
#            return jsonify({'error': 'Invalid certificate'}), 401
#        request.cert_dn = dn
#        return f(*args, **kwargs)
#    return decorated_function

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        log_login_failure(email or "Unknown", "Missing email or password")
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=email).first()
    
    if user and check_password_hash(user.password_hash, password):
        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(hours=24)
        )
        
        # Log successful login
        log_login_success(user.id, user.email)
        
        return jsonify({
            'token': access_token,
            'is_admin': user.role == 'Responsable',
            'role': user.role
        }), 200
    else:
        # Log failed login
        log_login_failure(email, "Invalid credentials")
        return jsonify({'error': 'Invalid email or password'}), 401

#def init_ssl_context():
#    """Initialize SSL context for mutual TLS"""
#    context = SSL.Context(SSL.TLSv1_2_METHOD)
#    context.set_verify(SSL.VERIFY_PEER | SSL.VERIFY_FAIL_IF_NO_PEER_CERT, lambda conn, cert, errno, depth, ok: ok)
#    context.use_privatekey_file(current_app.config['SERVER_KEY'])
#    context.use_certificate_file(current_app.config['SERVER_CERT'])
#    context.load_verify_locations(current_app.config['CA_CERT'])
#    return context 