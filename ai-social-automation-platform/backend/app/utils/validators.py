"""
Validation utilities for user input, credentials, and content
"""
import re
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation exception"""
    pass

def validate_email(email: str) -> bool:
    """Validate email address format"""
    try:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    except:
        return False

def validate_username(username: str) -> bool:
    """Validate username format"""
    if not username or len(username) < 3 or len(username) > 50:
        return False
    
    # Allow alphanumeric, underscore, and period
    pattern = r'^[a-zA-Z0-9._]+$'
    return bool(re.match(pattern, username))

def validate_password(password: str) -> Dict[str, Any]:
    """Validate password strength"""
    errors = []
    score = 0
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    else:
        score += 1
    
    if len(password) >= 12:
        score += 1
    
    if re.search(r'[a-z]', password):
        score += 1
    else:
        errors.append("Password must contain lowercase letters")
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        errors.append("Password must contain uppercase letters")
    
    if re.search(r'\d', password):
        score += 1
    else:
        errors.append("Password must contain numbers")
    
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    else:
        errors.append("Password must contain special characters")
    
    strength_levels = {
        0: 'very_weak',
        1: 'weak', 
        2: 'weak',
        3: 'medium',
        4: 'strong',
        5: 'very_strong',
        6: 'very_strong'
    }
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'strength': strength_levels.get(score, 'very_weak'),
        'score': score
    }

def validate_url(url: str) -> bool:
    """Validate URL format"""
    try:
        from urllib.parse import urlparse
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def validate_hashtags(hashtags: List[str]) -> Dict[str, Any]:
    """Validate hashtag format"""
    errors = []
    valid_hashtags = []
    
    for hashtag in hashtags:
        # Remove # if present
        clean_tag = hashtag.lstrip('#').strip()
        
        if not clean_tag:
            errors.append("Empty hashtag found")
            continue
        
        if len(clean_tag) > 30:
            errors.append(f"Hashtag '{clean_tag}' is too long (max 30 characters)")
            continue
        
        # Check for valid characters (alphanumeric and underscore)
        if not re.match(r'^[a-zA-Z0-9_]+$', clean_tag):
            errors.append(f"Hashtag '{clean_tag}' contains invalid characters")
            continue
        
        valid_hashtags.append(f"#{clean_tag}")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'valid_hashtags': valid_hashtags
    }

def validate_content_length(content: str, platform: str) -> Dict[str, Any]:
    """Validate content length for specific platforms"""
    platform_limits = {
        'instagram': {
            'caption': 2200,
            'story_text': 500
        },
        'facebook': {
            'post': 63206,
            'comment': 8000
        },
        'youtube': {
            'title': 100,
            'description': 5000
        },
        'twitter': {
            'tweet': 280,
            'thread': 280
        },
        'linkedin': {
            'post': 3000,
            'article': 110000
        }
    }
    
    limits = platform_limits.get(platform, {})
    if not limits:
        return {'is_valid': True, 'errors': [], 'length': len(content)}
    
    errors = []
    length = len(content)
    
    # Check against the first limit (usually the main content type)
    main_limit = next(iter(limits.values()))
    
    if length > main_limit:
        errors.append(f"Content too long for {platform} (max {main_limit} characters, got {length})")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'length': length,
        'limit': main_limit
    }

def validate_credentials(platform: str, credentials: Dict[str, str]) -> Dict[str, Any]:
    """Validate credentials for specific platforms"""
    errors = []
    
    if platform == 'instagram':
        if not credentials.get('username'):
            errors.append("Instagram username is required")
        elif not validate_username(credentials['username']):
            errors.append("Invalid Instagram username format")
        
        if not credentials.get('password'):
            errors.append("Instagram password is required")
        elif len(credentials['password']) < 6:
            errors.append("Instagram password is too short")
    
    elif platform == 'facebook':
        if not credentials.get('email'):
            errors.append("Facebook email is required")
        elif not validate_email(credentials['email']):
            errors.append("Invalid Facebook email format")
        
        if not credentials.get('password'):
            errors.append("Facebook password is required")
    
    elif platform == 'youtube':
        if not credentials.get('email'):
            errors.append("YouTube email is required")
        elif not validate_email(credentials['email']):
            errors.append("Invalid YouTube email format")
        
        if not credentials.get('password'):
            errors.append("YouTube password is required")
    
    elif platform == 'twitter':
        if not credentials.get('username'):
            errors.append("Twitter username is required")
        
        if not credentials.get('password'):
            errors.append("Twitter password is required")
    
    elif platform == 'linkedin':
        if not credentials.get('email'):
            errors.append("LinkedIn email is required")
        elif not validate_email(credentials['email']):
            errors.append("Invalid LinkedIn email format")
        
        if not credentials.get('password'):
            errors.append("LinkedIn password is required")
    
    else:
        errors.append(f"Unsupported platform: {platform}")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'platform': platform
    }

def validate_content(content_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate content data before posting"""
    errors = []
    
    # Validate required fields
    if not content_data.get('text') and not content_data.get('media_url'):
        errors.append("Content must have either text or media")
    
    # Validate text content
    if content_data.get('text'):
        text = content_data['text']
        if len(text.strip()) == 0:
            errors.append("Text content cannot be empty")
        elif len(text) > 10000:  # General limit
            errors.append("Text content is too long")
    
    # Validate platform
    platform = content_data.get('platform')
    if not platform:
        errors.append("Platform is required")
    elif platform not in ['instagram', 'facebook', 'youtube', 'twitter', 'linkedin']:
        errors.append(f"Unsupported platform: {platform}")
    
    # Platform-specific validation
    if platform and content_data.get('text'):
        platform_validation = validate_content_length(content_data['text'], platform)
        if not platform_validation['is_valid']:
            errors.extend(platform_validation['errors'])
    
    # Validate hashtags if present
    if content_data.get('hashtags'):
        hashtag_validation = validate_hashtags(content_data['hashtags'])
        if not hashtag_validation['is_valid']:
            errors.extend(hashtag_validation['errors'])
    
    # Validate media URL if present
    if content_data.get('media_url'):
        if not validate_url(content_data['media_url']):
            errors.append("Invalid media URL format")
    
    # Validate scheduled time if present
    if content_data.get('scheduled_time'):
        try:
            from datetime import datetime
            if isinstance(content_data['scheduled_time'], str):
                datetime.fromisoformat(content_data['scheduled_time'].replace('Z', '+00:00'))
        except ValueError:
            errors.append("Invalid scheduled time format")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'data': content_data
    }

def validate_user_registration(user_data: Dict[str, str]) -> Dict[str, Any]:
    """Validate user registration data"""
    errors = []
    
    # Validate email
    email = user_data.get('email', '').strip()
    if not email:
        errors.append("Email is required")
    elif not validate_email(email):
        errors.append("Invalid email format")
    
    # Validate username
    username = user_data.get('username', '').strip()
    if not username:
        errors.append("Username is required")
    elif not validate_username(username):
        errors.append("Invalid username format (3-50 chars, alphanumeric and . _ only)")
    
    # Validate password
    password = user_data.get('password', '')
    if not password:
        errors.append("Password is required")
    else:
        password_validation = validate_password(password)
        if not password_validation['is_valid']:
            errors.extend(password_validation['errors'])
    
    # Validate full name
    full_name = user_data.get('full_name', '').strip()
    if not full_name:
        errors.append("Full name is required")
    elif len(full_name) < 2 or len(full_name) > 100:
        errors.append("Full name must be 2-100 characters long")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'data': {
            'email': email,
            'username': username,
            'full_name': full_name,
            'password': password
        }
    }

def validate_domain_settings(domain_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate domain configuration settings"""
    errors = []
    
    # Validate domain name - FIXED THE SYNTAX ERROR
    name = domain_data.get('name', '').strip()
    if not name:
        errors.append("Domain name is required")
    elif not re.match(r'^[a-z0-9_]+$', name):  # FIXED: Added closing quote and $
        errors.append("Domain name must be lowercase alphanumeric with underscores")
    
    # Validate display name
    display_name = domain_data.get('display_name', '').strip()
    if not display_name:
        errors.append("Display name is required")
    elif len(display_name) > 100:
        errors.append("Display name too long (max 100 characters)")
    
    # Validate category
    valid_categories = [
        'entertainment', 'technology', 'business', 'lifestyle',
        'education', 'news', 'sports', 'health', 'fashion'
    ]
    category = domain_data.get('category')
    if not category:
        errors.append("Category is required")
    elif category not in valid_categories:
        errors.append(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
    
    # Validate keywords
    keywords = domain_data.get('keywords', [])
    if isinstance(keywords, list):
        for keyword in keywords:
            if not isinstance(keyword, str) or len(keyword.strip()) == 0:
                errors.append("Invalid keyword found")
            elif len(keyword) > 50:
                errors.append(f"Keyword '{keyword}' too long (max 50 characters)")
    
    # Validate hashtags
    hashtags = domain_data.get('hashtags', [])
    if hashtags:
        hashtag_validation = validate_hashtags(hashtags)
        if not hashtag_validation['is_valid']:
            errors.extend(hashtag_validation['errors'])
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'data': domain_data
    }

def sanitize_input(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize user input text"""
    if not isinstance(text, str):
        return ""
    
    # Remove potentially harmful characters
    sanitized = re.sub(r'[<>"\']', '', text)
    
    # Normalize whitespace
    sanitized = ' '.join(sanitized.split())
    
    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length].strip()
    
    return sanitized

def validate_file_upload(file_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate file upload data"""
    errors = []
    
    # Check file size
    max_size = 50 * 1024 * 1024  # 50MB
    file_size = file_data.get('size', 0)
    if file_size > max_size:
        errors.append(f"File too large (max {max_size // (1024*1024)}MB)")
    
    # Check file type
    allowed_types = {
        'image': ['jpg', 'jpeg', 'png', 'gif', 'webp'],
        'video': ['mp4', 'mov', 'avi', 'mkv', 'webm'],
        'document': ['pdf', 'doc', 'docx', 'txt']
    }
    
    filename = file_data.get('filename', '')
    if not filename:
        errors.append("Filename is required")
    else:
        extension = filename.split('.')[-1].lower()
        file_type = file_data.get('type', 'image')
        
        if file_type not in allowed_types:
            errors.append(f"Unsupported file type: {file_type}")
        elif extension not in allowed_types[file_type]:
            errors.append(f"Invalid file extension for {file_type}: {extension}")
    
    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'data': file_data
    }