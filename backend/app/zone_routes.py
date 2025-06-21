from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .models import db, Zone, User
from .logging_utils import log_zone_creation, log_zone_deletion

zone_bp = Blueprint('zone', __name__)

def role_required(roles):
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            if not user or user.role not in roles:
                return jsonify({'error': 'Insufficient privileges'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@zone_bp.route('/zones', methods=['GET'])
@jwt_required()
def get_zones():
    zones = Zone.query.all()
    return jsonify({'zones': [
        {
            'sigle': z.sigle,
            'puits': z.puits,
            'bloc': z.bloc,
            'permis': z.permis,
            'zoneId': z.zoneId
        } for z in zones
    ]}), 200

@zone_bp.route('/zones', methods=['POST'])
@jwt_required()
@role_required(['Geophysicien', 'Responsable'])
def add_zone():
    data = request.get_json()
    required = ['sigle', 'puits', 'bloc', 'permis']
    if not data or not all(k in data for k in required):
        return jsonify({'error': 'Missing data'}), 400
    zone = Zone(
        sigle=data['sigle'],
        puits=data['puits'],
        bloc=data['bloc'],
        permis=data['permis']
    )
    db.session.add(zone)
    db.session.commit()
    
    # Log zone creation
    user_id = get_jwt_identity()
    current_user = User.query.get(int(user_id))
    if current_user:
        zone_info = {'sigle': zone.sigle, 'puits': zone.puits, 'bloc': zone.bloc, 'permis': zone.permis}
        log_zone_creation(int(user_id), current_user.email, zone_info)
    
    return jsonify({'message': 'Zone added', 'zoneId': zone.zoneId}), 201

@zone_bp.route('/zones/<int:zone_id>', methods=['DELETE'])
@jwt_required()
@role_required(['Geophysicien', 'Responsable'])
def delete_zone(zone_id):
    zone = Zone.query.get(zone_id)
    if not zone:
        return jsonify({'error': 'Zone not found'}), 404
    db.session.delete(zone)
    db.session.commit()
    
    # Log zone deletion
    user_id = get_jwt_identity()
    current_user = User.query.get(int(user_id))
    if current_user:
        zone_info = {'sigle': zone.sigle, 'puits': zone.puits, 'bloc': zone.bloc, 'permis': zone.permis}
        log_zone_deletion(int(user_id), current_user.email, zone_info)
    
    return jsonify({'message': 'Zone deleted'}), 200 