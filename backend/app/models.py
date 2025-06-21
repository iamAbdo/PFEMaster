from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(32), nullable=False, default='Geologue')  # 'Geologue', 'Geophysicien', 'Responsable'
    certificate_dn = db.Column(db.String(256), unique=True)  # Distinguished Name from client cert
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    owned_files = db.relationship('File', backref='owner', lazy=True,
                                foreign_keys='File.owner_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Association table for file access
file_access = db.Table('file_access',
    db.Column('file_id', db.Integer, db.ForeignKey('file.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True)
)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Many-to-many relationship for file access
    users_with_access = db.relationship('User', secondary=file_access,
                                      lazy='subquery',
                                      backref=db.backref('accessible_files', lazy=True))

class Zone(db.Model):
    __tablename__ = 'zone'
    zoneId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sigle = db.Column(db.String(64), nullable=False)
    puits = db.Column(db.String(64), nullable=False)
    bloc = db.Column(db.String(64), nullable=False)
    permis = db.Column(db.String(64), nullable=False) 

class ActivityLog(db.Model):
    """Model for tracking user activities"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    user_email = db.Column(db.String(120), nullable=False)  # Store email for quick access
    action = db.Column(db.String(200), nullable=False)  # e.g., "File Upload", "User Login", "File Share"
    details = db.Column(db.Text)  # Additional details about the action
    status = db.Column(db.String(50), nullable=False)  # "success", "error", "warning"
    ip_address = db.Column(db.String(45))  # IPv4 or IPv6
    user_agent = db.Column(db.String(500))  # Browser/client info
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('activity_logs', passive_deletes=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'action': self.action,
            'details': self.details,
            'status': self.status,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'created_at': self.created_at.isoformat() if self.created_at else None
        } 