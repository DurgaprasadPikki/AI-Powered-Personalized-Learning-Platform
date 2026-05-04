import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config.settings import Config

class JWTHandler:
    """JWT token handling"""
    
    @staticmethod
    def create_token(user_id):
        """Create JWT token"""
        payload = {
            'user_id': str(user_id),
            'exp': datetime.utcnow() + Config.JWT_EXPIRATION,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    
    @staticmethod
    def verify_token(token):
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def get_token_from_request():
        """Extract token from Authorization header"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0] != 'Bearer':
            return None
        
        return parts[1]

def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = JWTHandler.get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Missing authentication token'}), 401
        
        payload = JWTHandler.verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        request.user_id = payload['user_id']
        return f(*args, **kwargs)
    
    return decorated_function

class PasswordHandler:
    """Password hashing and verification"""
    
    @staticmethod
    def hash_password(password):
        """Hash password with bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password, hash_value):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hash_value.encode('utf-8'))

class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not any(c.isupper() for c in password):
            return False, "Password must contain uppercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain digit"
        return True, "Valid"
    
    @staticmethod
    def validate_username(username):
        """Validate username format"""
        if len(username) < 3 or len(username) > 20:
            return False
        import re
        pattern = r'^[a-zA-Z0-9_-]+$'
        return re.match(pattern, username) is not None
