"""
Utility helper functions for VelocityPost.ai
"""

import json
import re
import hashlib
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from flask import jsonify, request
import logging

logger = logging.getLogger(__name__)

def generate_response(success=True, message="", data=None, status_code=200):
    """Generate standardized API response"""
    response = {
        'success': success,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if data is not None:
        response['data'] = data
        
    return jsonify(response), status_code

def generate_error_response(message="An error occurred", status_code=400, error_code=None):
    """Generate standardized error response"""
    response = {
        'success': False,
        'message': message,
        'timestamp': datetime.now(timezone.utc).isoformat()
    }
    
    if error_code:
        response['error_code'] = error_code
        
    return jsonify(response), status_code

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password):
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"

def sanitize_input(text, max_length=255):
    """Sanitize user input"""
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>"\']', '', str(text))
    
    # Truncate to max length
    return sanitized[:max_length].strip()

def generate_unique_id(length=16):
    """Generate a unique ID"""
    return secrets.token_hex(length)

def hash_password(password):
    """Hash password using bcrypt-like method"""
    import hashlib
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${hashed.hex()}"

def verify_password(password, hashed_password):
    """Verify password against hash"""
    try:
        salt, hash_hex = hashed_password.split('$')
        hashed = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hash_hex == hashed.hex()
    except:
        return False

def get_client_ip():
    """Get client IP address"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr

def log_api_request(endpoint, method, user_id=None, additional_data=None):
    """Log API request for monitoring"""
    log_data = {
        'endpoint': endpoint,
        'method': method,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'ip_address': get_client_ip(),
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    if user_id:
        log_data['user_id'] = user_id
    
    if additional_data:
        log_data.update(additional_data)
    
    logger.info(f"API Request: {json.dumps(log_data)}")

def format_currency(amount, currency='USD'):
    """Format currency amount"""
    currency_symbols = {
        'USD': '$',
        'INR': '₹',
        'EUR': '€',
        'GBP': '£'
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:,.2f}"

def calculate_engagement_rate(likes, comments, shares, followers):
    """Calculate engagement rate"""
    if followers == 0:
        return 0
    
    total_engagement = likes + comments + (shares * 2)  # Weight shares more
    return (total_engagement / followers) * 100

def get_optimal_posting_times(timezone='UTC', platform='instagram'):
    """Get optimal posting times for platform"""
    # Default optimal times based on platform
    optimal_times = {
        'instagram': ['09:00', '11:00', '14:00', '17:00', '20:00'],
        'facebook': ['09:00', '13:00', '15:00', '19:00'],
        'twitter': ['08:00', '12:00', '17:00', '19:00'],
        'linkedin': ['08:00', '10:00', '12:00', '14:00', '17:00'],
        'youtube': ['14:00', '17:00', '19:00', '20:00'],
        'tiktok': ['06:00', '10:00', '19:00', '20:00']
    }
    
    return optimal_times.get(platform, optimal_times['instagram'])

def truncate_text(text, max_length, add_ellipsis=True):
    """Truncate text to specified length"""
    if not text or len(text) <= max_length:
        return text
    
    if add_ellipsis:
        return text[:max_length-3] + "..."
    else:
        return text[:max_length]

def validate_url(url):
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))

def extract_hashtags(text):
    """Extract hashtags from text"""
    return re.findall(r'#\w+', text)

def extract_mentions(text):
    """Extract mentions from text"""
    return re.findall(r'@\w+', text)

def clean_filename(filename):
    """Clean filename for safe storage"""
    # Remove potentially dangerous characters
    cleaned = re.sub(r'[^\w\-_\.]', '', filename)
    return cleaned[:100]  # Limit length

def generate_oauth_state():
    """Generate secure OAuth state parameter"""
    return secrets.token_urlsafe(32)

def is_valid_json(json_string):
    """Check if string is valid JSON"""
    try:
        json.loads(json_string)
        return True
    except:
        return False

def merge_dictionaries(*dicts):
    """Merge multiple dictionaries"""
    result = {}
    for d in dicts:
        if isinstance(d, dict):
            result.update(d)
    return result

def get_file_extension(filename):
    """Get file extension"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_image_file(filename):
    """Check if file is an image"""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    return get_file_extension(filename) in image_extensions

def is_video_file(filename):
    """Check if file is a video"""
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    return get_file_extension(filename) in video_extensions

def calculate_text_similarity(text1, text2):
    """Calculate similarity between two texts (simple approach)"""
    if not text1 or not text2:
        return 0
    
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    return intersection / union if union > 0 else 0

def format_large_number(number):
    """Format large numbers (1K, 1M, etc.)"""
    if number < 1000:
        return str(number)
    elif number < 1000000:
        return f"{number/1000:.1f}K"
    elif number < 1000000000:
        return f"{number/1000000:.1f}M"
    else:
        return f"{number/1000000000:.1f}B"

def get_time_ago(timestamp):
    """Get human readable time ago"""
    if not timestamp:
        return "Unknown"
    
    now = datetime.now(timezone.utc)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    
    diff = now - timestamp
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "Just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours}h ago"
    elif seconds < 2592000:  # 30 days
        days = int(seconds / 86400)
        return f"{days}d ago"
    else:
        return timestamp.strftime("%b %d, %Y")

def validate_domain_selection(domains):
    """Validate content domain selection"""
    valid_domains = [
        'memes', 'tech_news', 'coding_tips', 'lifestyle', 
        'business', 'health_fitness', 'travel', 'food',
        'fashion', 'gaming', 'music', 'sports'
    ]
    
    if not isinstance(domains, list):
        return False, "Domains must be a list"
    
    if len(domains) == 0:
        return False, "At least one domain must be selected"
    
    if len(domains) > 5:
        return False, "Maximum 5 domains can be selected"
    
    for domain in domains:
        if domain not in valid_domains:
            return False, f"Invalid domain: {domain}"
    
    return True, "Domains are valid"

def get_platform_limits(plan_type):
    """Get platform limits based on plan"""
    limits = {
        'free': {
            'max_platforms': 2,
            'max_posts_per_day': 2,
            'max_content_generation': 10
        },
        'starter': {
            'max_platforms': 3,
            'max_posts_per_day': 6,
            'max_content_generation': 100
        },
        'pro': {
            'max_platforms': 5,
            'max_posts_per_day': 15,
            'max_content_generation': 500
        },
        'agency': {
            'max_platforms': -1,  # Unlimited
            'max_posts_per_day': -1,  # Unlimited
            'max_content_generation': -1  # Unlimited
        }
    }
    
    return limits.get(plan_type, limits['free'])

def check_rate_limit(user_id, action, limit_per_hour=60):
    """Basic rate limiting check"""
    # This is a simple implementation
    # In production, you'd use Redis or similar
    return True  # Placeholder

def generate_api_key():
    """Generate API key for external integrations"""
    return f"vp_{secrets.token_hex(20)}"

def mask_sensitive_data(data, fields_to_mask=None):
    """Mask sensitive data in logs"""
    if fields_to_mask is None:
        fields_to_mask = ['password', 'token', 'secret', 'key']
    
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if any(field in key.lower() for field in fields_to_mask):
                masked[key] = "*" * len(str(value)) if value else None
            else:
                masked[key] = mask_sensitive_data(value, fields_to_mask) if isinstance(value, (dict, list)) else value
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item, fields_to_mask) for item in data]
    else:
        return data