import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import magic
from .models import db, File, User
from datetime import datetime
# from .auth import require_cert

user_bp = Blueprint('user', __name__)

def allowed_file(filename):
    """Check if the file is a PDF."""
    mime = magic.Magic(mime=True)
    return mime.from_file(filename) == 'application/pdf'

@user_bp.route('/files/upload', methods=['POST'])
@jwt_required()
#@require_cert
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    access_list = request.form.getlist('access')
    user_id = int(get_jwt_identity())
    user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    filename = secure_filename(file.filename or 'unknown.pdf')
    filepath = os.path.join(user_upload_dir, filename)
    file.save(filepath)
    if not allowed_file(filepath):
        os.remove(filepath)
        return jsonify({'error': 'File must be a PDF'}), 400
    new_file = File(
        filename=filename,
        path=filepath,
        owner_id=user_id
    )
    if access_list:
        users = User.query.filter(User.email.in_(access_list)).all()
        new_file.users_with_access.extend(users)
    db.session.add(new_file)
    db.session.commit()
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'access_list': [user.email for user in new_file.users_with_access]
    }), 201

@user_bp.route('/files/export-pdf', methods=['POST'])
@jwt_required()
#@require_cert
def export_pdf():
    """Special endpoint for PDF exports from the frontend application"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Create user-specific upload directory
    user_upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id))
    os.makedirs(user_upload_dir, exist_ok=True)
    
    # Generate filename with timestamp if not provided
    if file.filename == 'export.pdf':
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.pdf"
    else:
        filename = secure_filename(file.filename or 'export.pdf')
    
    filepath = os.path.join(user_upload_dir, filename)
    file.save(filepath)
    
    # Verify it's a PDF
    if not allowed_file(filepath):
        os.remove(filepath)
        return jsonify({'error': 'File must be a PDF'}), 400
    
    # Save to database
    new_file = File(
        filename=filename,
        path=filepath,
        owner_id=user_id
    )
    db.session.add(new_file)
    db.session.commit()
    
    return jsonify({
        'message': 'PDF exported successfully',
        'filename': filename,
        'file_id': new_file.id,
        'exported_at': new_file.created_at.isoformat(),
        'user_email': user.email
    }), 201

@user_bp.route('/files', methods=['GET'])
@jwt_required()
#@require_cert
def get_user_files():
    """Get files owned by or shared with the current user"""
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    
    owned_files = [{
        'id': file.id,
        'filename': file.filename,
        'created_at': file.created_at.isoformat(),
        'owner': file.owner.email,
        'is_owner': True
    } for file in user.owned_files]
    
    shared_files = [{
        'id': file.id,
        'filename': file.filename,
        'created_at': file.created_at.isoformat(),
        'owner': file.owner.email,
        'is_owner': False
    } for file in user.accessible_files]
    return jsonify({
        'owned_files': owned_files,
        'shared_files': shared_files
    }), 200

@user_bp.route('/admin/files', methods=['GET'])
@jwt_required()
def get_all_files():
    """Get all files in the system (admin only)"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Only Responsable users can access this endpoint
    if current_user.role != 'Responsable':
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    # Get all files in the system
    all_files = File.query.all()
    
    files_data = []
    for file in all_files:
        is_owner = file.owner_id == user_id
        files_data.append({
            'id': file.id,
            'filename': file.filename,
            'created_at': file.created_at.isoformat(),
            'owner': file.owner.email,
            'is_owner': is_owner
        })
    
    return jsonify({
        'files': files_data,
        'total_count': len(files_data)
    }), 200

@user_bp.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
def delete_file(file_id):
    """Delete a file"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file OR is an admin (Responsable)
    if file.owner_id != user_id and current_user.role != 'Responsable':
        return jsonify({'error': 'You can only delete files you own'}), 403
    
    try:
        # Remove file from disk
        if os.path.exists(file.path):
            os.remove(file.path)
        
        # Remove from database
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'message': 'File deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error deleting file: {str(e)}'}), 500

@user_bp.route('/files/<int:file_id>/access', methods=['PUT'])
@jwt_required()
#@require_cert
def update_access(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.get_or_404(file_id)
    if file.owner_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    data = request.get_json()
    if not data or 'access_list' not in data:
        return jsonify({'error': 'No access list provided'}), 400
    users = User.query.filter(User.email.in_(data['access_list'])).all()
    file.users_with_access = users
    db.session.commit()
    return jsonify({
        'message': 'Access list updated',
        'access_list': [user.email for user in file.users_with_access]
    }), 200

@user_bp.route('/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
#@require_cert
def download_file(file_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file, has access, OR is an admin (Responsable)
    has_access = (file.owner_id == user_id or 
                  user_id in [u.id for u in file.users_with_access] or
                  current_user.role == 'Responsable')
    
    if not has_access:
        return jsonify({'error': 'Not authorized'}), 403
    
    return send_file(
        file.path,
        as_attachment=True,
        download_name=file.filename,
        mimetype='application/pdf'
    )

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_user_profile():
    """Get current user's profile information"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'id': user.id,
        'email': user.email,
        'is_admin': user.is_admin,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    }), 200

@user_bp.route('/users/geologues', methods=['GET'])
@jwt_required()
def get_geologues():
    """Get all Geologue users for file sharing"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Only Responsable users can access this endpoint
    if current_user.role != 'Responsable':
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    geologues = User.query.filter_by(role='Geologue').all()
    return jsonify({
        'geologues': [{
            'id': user.id,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        } for user in geologues]
    }), 200

@user_bp.route('/users/available', methods=['GET'])
@jwt_required()
def get_available_users():
    """Get all available users (Geologues and Geophysiciens) for file sharing"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Only Responsable users can access this endpoint
    if current_user.role != 'Responsable':
        return jsonify({'error': 'Insufficient privileges'}), 403
    
    # Get both Geologues and Geophysiciens
    available_users = User.query.filter(User.role.in_(['Geologue', 'Geophysicien'])).all()
    return jsonify({
        'available_users': [{
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        } for user in available_users]
    }), 200

@user_bp.route('/files/<int:file_id>/share', methods=['POST'])
@jwt_required()
def share_file(file_id):
    """Share a file with other users"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file OR is an admin (Responsable)
    if file.owner_id != user_id and current_user.role != 'Responsable':
        return jsonify({'error': 'You can only share files you own'}), 403
    
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'No users specified'}), 400
    
    # Get the users to share with
    users_to_share_with = User.query.filter(User.id.in_(user_ids)).all()
    
    if not users_to_share_with:
        return jsonify({'error': 'No valid users found'}), 400
    
    # Add users to file access
    shared_with = []
    for user in users_to_share_with:
        if user not in file.users_with_access:
            file.users_with_access.append(user)
            shared_with.append(user.email)
    
    db.session.commit()
    
    return jsonify({
        'message': f'File shared with {len(shared_with)} user(s)',
        'shared_with': shared_with
    }), 200

@user_bp.route('/files/<int:file_id>/unshare', methods=['POST'])
@jwt_required()
def unshare_file(file_id):
    """Unshare a file from specific users"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file OR is an admin (Responsable)
    if file.owner_id != user_id and current_user.role != 'Responsable':
        return jsonify({'error': 'You can only unshare files you own'}), 403
    
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'No users specified'}), 400
    
    # Get the users to remove access from
    users_to_remove = User.query.filter(User.id.in_(user_ids)).all()
    
    if not users_to_remove:
        return jsonify({'error': 'No valid users found'}), 400
    
    # Remove users from file access
    removed_from = []
    for user in users_to_remove:
        if user in file.users_with_access:
            file.users_with_access.remove(user)
            removed_from.append(user.email)
    
    db.session.commit()
    
    return jsonify({
        'message': f'Access removed for {len(removed_from)} user(s)',
        'removed_from': removed_from
    }), 200

@user_bp.route('/files/<int:file_id>/shared-users', methods=['GET'])
@jwt_required()
def get_shared_users(file_id):
    """Get list of users who have access to a specific file"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file OR is an admin (Responsable)
    if file.owner_id != user_id and current_user.role != 'Responsable':
        return jsonify({'error': 'Not authorized to view shared users'}), 403
    
    return jsonify({
        'shared_users': [{
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat()
        } for user in file.users_with_access]
    }), 200

@user_bp.route('/files/<int:file_id>/users-for-sharing', methods=['GET'])
@jwt_required()
def get_users_for_sharing(file_id):
    """Get all users for file sharing, including the file owner"""
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)
    
    if not current_user:
        return jsonify({'error': 'User not found'}), 404
    
    file = File.query.get_or_404(file_id)
    
    # Check if user owns the file OR is an admin (Responsable)
    if file.owner_id != user_id and current_user.role != 'Responsable':
        return jsonify({'error': 'Not authorized to share this file'}), 403
    
    # Get all users (Geologues and Geophysiciens)
    all_users = User.query.filter(User.role.in_(['Geologue', 'Geophysicien'])).all()
    
    # Get shared users for this file
    shared_user_ids = {user.id for user in file.users_with_access}
    
    # Prepare user list with owner information
    users_for_sharing = []
    for user in all_users:
        is_owner = user.id == file.owner_id
        has_access = user.id in shared_user_ids
        
        users_for_sharing.append({
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'created_at': user.created_at.isoformat(),
            'is_owner': is_owner,
            'has_access': has_access
        })
    
    return jsonify({
        'users_for_sharing': users_for_sharing,
        'file_owner_id': file.owner_id
    }), 200 