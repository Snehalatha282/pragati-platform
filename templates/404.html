# utils/validation.py
import re
from datetime import datetime

def validate_name(name):
    """
    Validate name field
    """
    if not name or len(name.strip()) < 2:
        return False, "Name must be at least 2 characters long"
    
    if len(name) > 50:
        return False, "Name cannot exceed 50 characters"
    
    if not re.match(r'^[a-zA-Z\s\-\.\']+$', name):
        return False, "Name can only contain letters, spaces, hyphens, dots, and apostrophes"
    
    return True, "Name is valid"

def validate_date(date_str, date_format='%Y-%m-%d'):
    """
    Validate date string
    """
    try:
        datetime.strptime(date_str, date_format)
        return True, "Date is valid"
    except ValueError:
        return False, f"Date must be in format {date_format}"

def validate_url(url):
    """
    Validate URL format
    """
    pattern = re.compile(
        r'^(https?://)?'  # http:// or https://
        r'(([A-Z0-9][A-Z0-9-]*[A-Z0-9]\.)+[A-Z]{2,}|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ip
        r'(:\d+)?'  # port
        r'(/[-a-zA-Z0-9@:%_\+.~#?&//=]*)?$',  # path
        re.IGNORECASE
    )
    
    if re.match(pattern, url):
        return True, "URL is valid"
    return False, "Invalid URL format"

def validate_json(data_str):
    """
    Validate JSON string
    """
    try:
        json.loads(data_str)
        return True, "Valid JSON"
    except json.JSONDecodeError as e:
        return False, f"Invalid JSON: {str(e)}"

def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    """
    if '.' not in filename:
        return False, "No file extension"
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in allowed_extensions:
        return True, "File extension is allowed"
    
    return False, f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"

def validate_file_size(file_size, max_size_mb=10):
    """
    Validate file size
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_size_bytes:
        return False, f"File size exceeds maximum of {max_size_mb}MB"
    
    return True, "File size is acceptable"

def validate_career_break_duration(years):
    """
    Validate career break duration
    """
    try:
        years_int = int(years)
        if years_int < 0 or years_int > 50:
            return False, "Career break duration must be between 0 and 50 years"
        return True, "Valid career break duration"
    except ValueError:
        return False, "Career break duration must be a number"

def validate_skill_input(skills):
    """
    Validate skills input (comma-separated string or list)
    """
    if isinstance(skills, str):
        skill_list = [s.strip() for s in skills.split(',') if s.strip()]
    elif isinstance(skills, list):
        skill_list = skills
    else:
        return False, "Skills must be a comma-separated string or list", []
    
    if len(skill_list) == 0:
        return False, "At least one skill is required", []
    
    # Validate each skill
    invalid_skills = []
    for skill in skill_list:
        if len(skill) > 100:
            invalid_skills.append(skill)
    
    if invalid_skills:
        return False, f"Skills exceed maximum length: {', '.join(invalid_skills)}", skill_list
    
    return True, "Skills are valid", skill_list