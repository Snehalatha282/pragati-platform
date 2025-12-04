# utils/auth_utils.py
import re
from werkzeug.security import generate_password_hash, check_password_hash

def validate_password(password):
    """
    Validate password strength
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def validate_email(email):
    """
    Validate email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_reset_token():
    """
    Generate password reset token
    """
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))

def hash_password(password):
    """
    Hash password for storage
    """
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    """
    Verify password against hash
    """
    return check_password_hash(hashed_password, password)

def validate_phone(phone):
    """
    Validate phone number format
    """
    # Simple validation - can be enhanced based on requirements
    pattern = r'^[\+]?[1-9][\d]{0,15}$'
    return bool(re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))

def sanitize_input(text):
    """
    Sanitize user input to prevent XSS attacks
    """
    if not text:
        return text
    
    # Remove dangerous HTML tags
    import html
    text = html.escape(text)
    
    # Additional sanitization can be added here
    return text