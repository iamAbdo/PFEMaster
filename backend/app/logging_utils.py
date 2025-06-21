from flask import request, g
from .models import db, ActivityLog, User
from datetime import datetime
import json

def log_activity(action, details=None, status="success", user_id=None, user_email=None):
    """
    Log user activity to the database
    
    Args:
        action (str): The action performed (e.g., "File Upload", "User Login")
        details (str, optional): Additional details about the action
        status (str): "success", "error", or "warning"
        user_id (int, optional): User ID (if not provided, tries to get from g.user)
        user_email (str, optional): User email (if not provided, tries to get from g.user)
    """
    try:
        # Get user info if not provided
        if user_id is None and hasattr(g, 'user'):
            user_id = g.user.id
            user_email = g.user.email
        
        # Get request info
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        # Create log entry
        log_entry = ActivityLog(
            user_id=user_id,
            user_email=user_email or "Unknown",
            action=action,
            details=details,
            status=status,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.session.add(log_entry)
        db.session.commit()
        
    except Exception as e:
        # If logging fails, don't break the main functionality
        print(f"Error logging activity: {e}")
        db.session.rollback()

def log_login_success(user_id, user_email):
    """Log successful user login"""
    log_activity(
        action="User Login",
        details=f"Successful login for user {user_email}",
        status="success",
        user_id=user_id,
        user_email=user_email
    )

def log_login_failure(email, reason="Invalid credentials"):
    """Log failed login attempt"""
    log_activity(
        action="Login Failed",
        details=f"Failed login attempt for {email}: {reason}",
        status="error",
        user_email=email
    )

def log_file_upload(user_id, user_email, filename, status="success"):
    """Log file upload activity"""
    log_activity(
        action="File Upload",
        details=f"Uploaded file: {filename}",
        status=status,
        user_id=user_id,
        user_email=user_email
    )

def log_file_download(user_id, user_email, filename, status="success"):
    """Log file download activity"""
    log_activity(
        action="File Download",
        details=f"Downloaded file: {filename}",
        status=status,
        user_id=user_id,
        user_email=user_email
    )

def log_file_share(user_id, user_email, filename, shared_with_users, status="success"):
    """Log file sharing activity"""
    details = f"Shared file '{filename}' with {len(shared_with_users)} user(s): {', '.join(shared_with_users)}"
    log_activity(
        action="File Share",
        details=details,
        status=status,
        user_id=user_id,
        user_email=user_email
    )

def log_file_delete(user_id, user_email, filename, status="success"):
    """Log file deletion activity"""
    log_activity(
        action="File Delete",
        details=f"Deleted file: {filename}",
        status=status,
        user_id=user_id,
        user_email=user_email
    )

def log_user_creation(admin_id, admin_email, new_user_email, status="success"):
    """Log user creation activity"""
    log_activity(
        action="User Creation",
        details=f"Created new user: {new_user_email}",
        status=status,
        user_id=admin_id,
        user_email=admin_email
    )

def log_user_deletion(admin_id, admin_email, deleted_user_email, status="success"):
    """Log user deletion activity"""
    log_activity(
        action="User Deletion",
        details=f"Deleted user: {deleted_user_email}",
        status=status,
        user_id=admin_id,
        user_email=admin_email
    )

def log_zone_creation(user_id, user_email, zone_info, status="success"):
    """Log zone creation activity"""
    details = f"Created zone: {zone_info.get('sigle', 'Unknown')} - {zone_info.get('puits', 'Unknown')}"
    log_activity(
        action="Zone Creation",
        details=details,
        status=status,
        user_id=user_id,
        user_email=user_email
    )

def log_zone_deletion(user_id, user_email, zone_info, status="success"):
    """Log zone deletion activity"""
    details = f"Deleted zone: {zone_info.get('sigle', 'Unknown')} - {zone_info.get('puits', 'Unknown')}"
    log_activity(
        action="Zone Deletion",
        details=details,
        status=status,
        user_id=user_id,
        user_email=user_email
    ) 