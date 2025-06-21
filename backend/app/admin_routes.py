from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import User
from functools import wraps
from .models import db
from werkzeug.security import generate_password_hash
from .logging_utils import log_user_creation, log_user_deletion, log_zone_creation, log_zone_deletion

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.all()
    return jsonify({
        'users': [{
            'id': user.id,
            'email': user.email,
            'is_admin': user.is_admin,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        } for user in users]
    }), 200

@admin_bp.route('/create-user', methods=['POST'])
@jwt_required()
def create_user():
    """Create a new user (admin only)"""
    user_id = get_jwt_identity()
    current_user = User.query.get(int(user_id))
    
    if not current_user or current_user.role != 'Responsable':
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'Geologue')
    
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'User already exists'}), 400
    
    try:
        new_user = User(
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        
        # Log user creation
        log_user_creation(int(user_id), current_user.email, email)
        
        return jsonify({'message': 'User created successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error creating user: {str(e)}'}), 500 