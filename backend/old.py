from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import timedelta
from pymongo import MongoClient
import magic

app = Flask(__name__)
CORS(app)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize JWT
jwt = JWTManager(app)

# Initialize MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['document_sharing']
users_collection = db['users']
files_collection = db['files']

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if the file is a PDF."""
    mime = magic.Magic(mime=True)
    return mime.from_file(filename) == 'application/pdf'

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    if users_collection.find_one({'email': data['email']}):
        return jsonify({'error': 'Email already registered'}), 400
    
    hashed_password = generate_password_hash(data['password'])
    user = {
        'email': data['email'],
        'password': hashed_password
    }
    
    users_collection.insert_one(user)
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Missing email or password'}), 400
    
    user = users_collection.find_one({'email': data['email']})
    if not user or not check_password_hash(user['password'], data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    access_token = create_access_token(identity=str(user['_id']))
    return jsonify({'token': access_token}), 200

@app.route('/api/upload', methods=['POST'])
@jwt_required()
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    access_list = request.form.getlist('access')
    if not access_list:
        return jsonify({'error': 'No users with access specified'}), 400
    
    # Verify all users exist
    for email in access_list:
        if not users_collection.find_one({'email': email}):
            return jsonify({'error': f'User {email} does not exist'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    if not allowed_file(filepath):
        os.remove(filepath)
        return jsonify({'error': 'File must be a PDF'}), 400
    
    # Save file information to database
    file_info = {
        'filename': filename,
        'path': filepath,
        'uploaded_by': get_jwt_identity(),
        'access_list': access_list
    }
    files_collection.insert_one(file_info)
    
    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'access_list': access_list
    }), 201

@app.route('/api/files', methods=['GET'])
@jwt_required()
def get_user_files():
    user_email = users_collection.find_one({'_id': get_jwt_identity()})['email']
    files = files_collection.find({
        '$or': [
            {'uploaded_by': get_jwt_identity()},
            {'access_list': user_email}
        ]
    })
    
    file_list = [{
        'filename': file['filename'],
        'uploaded_by': file['uploaded_by'],
        'access_list': file['access_list']
    } for file in files]
    
    return jsonify({'files': file_list}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000) 