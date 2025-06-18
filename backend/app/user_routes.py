import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import magic
from .models import db, File, User
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
    filename = secure_filename(file.filename)
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

@user_bp.route('/files', methods=['GET'])
@jwt_required()
#@require_cert
def get_user_files():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    owned_files = [{
        'id': file.id,
        'filename': file.filename,
        'created_at': file.created_at.isoformat(),
        'access_list': [u.email for u in file.users_with_access],
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

@user_bp.route('/files/<int:file_id>', methods=['DELETE'])
@jwt_required()
#@require_cert
def delete_file(file_id):
    user_id = int(get_jwt_identity())
    file = File.query.get_or_404(file_id)
    if file.owner_id != user_id:
        return jsonify({'error': 'Not authorized'}), 403
    try:
        os.remove(file.path)
    except OSError:
        pass
    db.session.delete(file)
    db.session.commit()
    return jsonify({'message': 'File deleted successfully'}), 200

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
    file = File.query.get_or_404(file_id)
    if file.owner_id != user_id and user_id not in [u.id for u in file.users_with_access]:
        return jsonify({'error': 'Not authorized'}), 403
    return send_file(
        file.path,
        as_attachment=True,
        download_name=file.filename,
        mimetype='application/pdf'
    ) 