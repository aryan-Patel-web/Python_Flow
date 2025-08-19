import uuid
import datetime

def generate_uuid() -> str:
    """Generate a unique identifier."""
    return str(uuid.uuid4())

def current_timestamp() -> str:
    """Return current UTC timestamp as string."""
    return datetime.datetime.utcnow().isoformat()

def paginate_query(query, page: int, per_page: int):
    """Paginate a SQLAlchemy query."""
    return query.limit(per_page).offset((page - 1) * per_page)
"""
Helper utilities for common operations
"""
import uuid
import re
import hashlib
import secrets
import string
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any, Union
import json
import base64
from urllib.parse import urlparse
import bleach

def generate_uuid() -> str:
    """Generate a UUID4 string"""
    return str(uuid.uuid4())

def generate_short_id(length: int = 8) -> str:
    """Generate a short random ID"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_api_key(prefix: str = 'ai_social', length: int = 32) -> str:
    """Generate an API key with prefix"""
    key = secrets.token_urlsafe(length)
    return f"{prefix}_{key}"

def hash_password(password: str, salt: str = None) -> tuple:
    """Hash a password with salt"""
    if salt is None:
        salt = secrets.token_hex(16)
    
    # Use PBKDF2 for password hashing
    from hashlib import pbkdf2_hmac
    hashed = pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return base64.b64encode(hashed).decode(), salt

def verify_password(password: str, hashed: str, salt: str) -> bool:
    """Verify a password against its hash"""
    test_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(test_hash, hashed)

def format_datetime(dt: datetime, format_type: str = 'iso') -> str:
    """Format datetime for different use cases"""
    if dt is None:
        return None
    
    if format_type == 'iso':
        return dt.isoformat()
    elif format_type == 'human':
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif format_type == 'date':
        return dt.strftime('%Y-%m-%d')
    elif format_type == 'time':
        return dt.strftime('%H:%M:%S')
    elif format_type == 'relative':
        return format_relative_time(dt)
    else:
        return dt.isoformat()

def format_relative_time(dt: datetime) -> str:
    """Format time relative to now (e.g., '2 hours ago')"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        return f"{diff.days} days ago"
    
    hours = diff.seconds // 3600
    if hours > 0:
        if hours == 1:
            return "1 hour ago"
        return f"{hours} hours ago"
    
    minutes = diff.seconds // 60
    if minutes > 0:
        if minutes == 1:
            return "1 minute ago"
        return f"{minutes} minutes ago"
    
    return "Just now"

def parse_datetime(date_string: str) -> Optional[datetime]:
    """Parse various datetime formats"""
    if not date_string:
        return None
    
    formats = [
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y'
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue
    
    return None

def sanitize_text(text: str, max_length: Optional[int] = None, 
                 allow_html: bool = False) -> str:
    """Sanitize text input"""
    if not isinstance(text, str):
        return ""
    
    # Remove or escape HTML if not allowed
    if not allow_html:
        text = bleach.clean(text, strip=True)
    else:
        # Allow basic HTML tags
        allowed_tags = ['b', 'i', 'u', 'em', 'strong', 'a', 'br', 'p']
        text = bleach.clean(text, tags=allowed_tags, strip=True)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Truncate if necessary
    if max_length and len(text) > max_length:
        text = text[:max_length].strip()
        if not text.endswith('...'):
            text += '...'
    
    return text

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text"""
    hashtag_pattern = r'#[a-zA-Z0-9_]+'
    hashtags = re.findall(hashtag_pattern, text)
    return [tag.lower() for tag in hashtags]

def extract_mentions(text: str) -> List[str]:
    """Extract @mentions from text"""
    mention_pattern = r'@[a-zA-Z0-9_.]+'
    mentions = re.findall(mention_pattern, text)
    return [mention.lower() for mention in mentions]

def extract_urls(text: str) -> List[str]:
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    return urls

def shorten_url(url: str, max_length: int = 30) -> str:
    """Shorten URL for display"""
    if len(url) <= max_length:
        return url
    
    parsed = urlparse(url)
    domain = parsed.netloc
    
    if len(domain) > max_length - 3:
        return domain[:max_length-3] + "..."
    
    return domain + "..."

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_number(number: Union[int, float], compact: bool = False) -> str:
    """Format number for display"""
    if compact:
        if number >= 1000000:
            return f"{number/1000000:.1f}M"
        elif number >= 1000:
            return f"{number/1000:.1f}K"
    
    return f"{number:,}"

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    # Convert to lowercase and replace spaces with hyphens
    slug = re.sub(r'[^\w\s-]', '', text.lower())
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """Deep merge two dictionaries"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def safe_json_loads(json_string: str, default: Any = None) -> Any:
    """Safely parse JSON string"""
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default

def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """Safely serialize object to JSON"""
    try:
        return json.dumps(obj, default=str)
    except (TypeError, ValueError):
        return default

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """Mask sensitive data (passwords, tokens, etc.)"""
    if not data or len(data) <= visible_chars:
        return mask_char * len(data) if data else ""
    
    visible_part = data[:visible_chars]
    masked_part = mask_char * (len(data) - visible_chars)
    return visible_part + masked_part

def validate_and_normalize_email(email: str) -> Optional[str]:
    """Validate and normalize email address"""
    if not email:
        return None
    
    # Basic email validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return None
    
    # Normalize: lowercase and strip whitespace
    return email.lower().strip()

def generate_filename(original_filename: str, user_id: str = None, 
                     timestamp: bool = True) -> str:
    """Generate a safe filename for uploads"""
    # Extract extension
    name, ext = os.path.splitext(original_filename)
    
    # Sanitize filename
    safe_name = re.sub(r'[^\w\-_.]', '_', name)
    safe_name = safe_name[:50]  # Limit length
    
    # Add components
    components = []
    
    if user_id:
        components.append(user_id[:8])  # First 8 chars of user ID
    
    if timestamp:
        components.append(datetime.utcnow().strftime('%Y%m%d_%H%M%S'))
    
    components.append(safe_name)
    
    # Add random suffix to avoid collisions
    components.append(generate_short_id(6))
    
    return '_'.join(components) + ext

def calculate_content_hash(content: str) -> str:
    """Calculate hash of content for deduplication"""
    return hashlib.sha256(content.encode()).hexdigest()

def is_business_hours(timezone_str: str = 'UTC') -> bool:
    """Check if current time is within business hours"""
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone_str)
    except:
        tz = timezone.utc
    
    now = datetime.now(tz)
    return 9 <= now.hour < 17 and now.weekday() < 5  # 9 AM - 5 PM, Mon-Fri

def get_optimal_posting_time(platform: str, timezone_str: str = 'UTC') -> datetime:
    """Get optimal posting time for platform"""
    # Platform-specific optimal times (in 24-hour format)
    optimal_times = {
        'instagram': [9, 11, 13, 15, 17, 19],  # Multiple good times
        'facebook': [9, 13, 15],
        'twitter': [8, 12, 17, 19],
        'linkedin': [8, 10, 12, 14, 17],
        'youtube': [14, 15, 16, 17, 18, 19, 20]
    }
    
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo(timezone_str)
    except:
        tz = timezone.utc
    
    now = datetime.now(tz)
    times = optimal_times.get(platform, [12])  # Default to noon
    
    # Find next optimal time
    for hour in times:
        optimal_time = now.replace(hour=hour, minute=0, second=0, microsecond=0)
        if optimal_time > now:
            return optimal_time
    
    # If no time today, use first time tomorrow
    tomorrow = now + timedelta(days=1)
    return tomorrow.replace(hour=times[0], minute=0, second=0, microsecond=0)

def calculate_engagement_rate(likes: int, comments: int, shares: int, 
                            followers: int) -> float:
    """Calculate engagement rate"""
    if followers == 0:
        return 0.0
    
    total_engagement = likes + comments + (shares * 2)  # Weight shares more
    return (total_engagement / followers) * 100

def calculate_growth_rate(current: int, previous: int) -> float:
    """Calculate growth rate percentage"""
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    
    return ((current - previous) / previous) * 100

def format_currency(amount: float, currency: str = 'USD') -> str:
    """Format currency amount"""
    currency_symbols = {
        'USD': ',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def truncate_text(text: str, max_length: int, suffix: str = '...') -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def remove_duplicates(lst: List, key_func=None) -> List:
    """Remove duplicates from list while preserving order"""
    if key_func is None:
        # Simple deduplication
        seen = set()
        result = []
        for item in lst:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result
    else:
        # Deduplication with key function
        seen = set()
        result = []
        for item in lst:
            key = key_func(item)
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result

def batch_process(items: List, batch_size: int, process_func, *args, **kwargs):
    """Process items in batches"""
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = process_func(batch, *args, **kwargs)
        if isinstance(batch_results, list):
            results.extend(batch_results)
        else:
            results.append(batch_results)
    return results

def retry_on_failure(max_attempts: int = 3, delay: float = 1.0, 
                    backoff_multiplier: float = 2.0, exceptions=(Exception,)):
    """Decorator to retry function on failure"""
    def decorator(func):
        import time
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            current_delay = delay
            
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_attempts:
                        raise e
                    
                    time.sleep(current_delay)
                    current_delay *= backoff_multiplier
                    attempt += 1
            
        return wrapper
    return decorator

def memoize(maxsize: int = 128):
    """Simple memoization decorator"""
    def decorator(func):
        from functools import lru_cache
        return lru_cache(maxsize=maxsize)(func)
    return decorator

def rate_limited_call(func, rate_limit: int, time_window: int = 60):
    """Execute function with rate limiting"""
    import time
    
    if not hasattr(rate_limited_call, 'calls'):
        rate_limited_call.calls = {}
    
    func_name = func.__name__
    current_time = time.time()
    
    # Initialize or clean old calls
    if func_name not in rate_limited_call.calls:
        rate_limited_call.calls[func_name] = []
    
    # Remove calls outside time window
    rate_limited_call.calls[func_name] = [
        call_time for call_time in rate_limited_call.calls[func_name]
        if current_time - call_time < time_window
    ]
    
    # Check rate limit
    if len(rate_limited_call.calls[func_name]) >= rate_limit:
        oldest_call = min(rate_limited_call.calls[func_name])
        wait_time = time_window - (current_time - oldest_call)
        raise Exception(f"Rate limit exceeded. Try again in {wait_time:.1f} seconds")
    
    # Record call and execute
    rate_limited_call.calls[func_name].append(current_time)
    return func()

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return filename.split('.')[-1].lower() if '.' in filename else ''

def is_valid_file_type(filename: str, allowed_types: List[str]) -> bool:
    """Check if file type is allowed"""
    extension = get_file_extension(filename)
    return extension in [t.lower() for t in allowed_types]

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure token"""
    return secrets.token_urlsafe(length)

def time_function(func):
    """Decorator to time function execution"""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        execution_time = end_time - start_time
        print(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        return result
    
    return wrapper

def validate_json_schema(data: Dict, schema: Dict) -> List[str]:
    """Basic JSON schema validation"""
    errors = []
    
    for field, field_schema in schema.items():
        if field_schema.get('required', False) and field not in data:
            errors.append(f"Required field '{field}' is missing")
            continue
        
        if field in data:
            value = data[field]
            expected_type = field_schema.get('type')
            
            if expected_type and not isinstance(value, expected_type):
                errors.append(f"Field '{field}' must be of type {expected_type.__name__}")
            
            min_length = field_schema.get('min_length')
            if min_length and isinstance(value, str) and len(value) < min_length:
                errors.append(f"Field '{field}' must be at least {min_length} characters")
            
            max_length = field_schema.get('max_length')
            if max_length and isinstance(value, str) and len(value) > max_length:
                errors.append(f"Field '{field}' must be at most {max_length} characters")
    
    return errors

def create_thumbnail_filename(original_filename: str, size: str = 'thumb') -> str:
    """Create thumbnail filename from original"""
    name, ext = os.path.splitext(original_filename)
    return f"{name}_{size}{ext}"

def get_mime_type(filename: str) -> str:
    """Get MIME type from filename"""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'

def is_image_file(filename: str) -> bool:
    """Check if file is an image"""
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
    return get_file_extension(filename) in image_extensions

def is_video_file(filename: str) -> bool:
    """Check if file is a video"""
    video_extensions = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    return get_file_extension(filename) in video_extensions

def normalize_phone_number(phone: str, country_code: str = '+1') -> str:
    """Normalize phone number format"""
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # Add country code if not present
    if not digits.startswith(country_code.replace('+', '')):
        digits = country_code.replace('+', '') + digits
    
    return '+' + digits

def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes}m {seconds % 60}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"

def get_current_timestamp() -> int:
    """Get current Unix timestamp"""
    return int(datetime.utcnow().timestamp())

def timestamp_to_datetime(timestamp: Union[int, float]) -> datetime:
    """Convert Unix timestamp to datetime"""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)

import os