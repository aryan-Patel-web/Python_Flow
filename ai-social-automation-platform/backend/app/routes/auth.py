#!/usr/bin/env python3
"""
Authentication Routes for VelocityPost.ai
Handles user registration, login, password reset, and JWT token management
"""

import os
import re
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from bson.objectid import ObjectId
from functools import wraps

# Import from the correct path
from app.utils.database import get_collection

logger = logging.getLogger(__name__)

# Create Blueprint
auth_bp = Blueprint('auth', __name__)

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRY_HOURS = 24  # 24 hours
REFRESH_TOKEN_EXPIRY_DAYS = 30  # 30 days

# Password requirements
PASSWORD_MIN_LENGTH = 8

def validate_email(email):
    """Validate email format"""
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))

def validate_password(password):
    """Validate password strength"""
    if len(password) < PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {PASSWORD_MIN_LENGTH} characters long"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[@$!%*?&]', password):
        return False, "Password must contain at least one special character (@$!%*?&)"
    
    return True, "Password is valid"

def generate_jwt_token(user_id, email, token_type='access'):
    """Generate JWT access or refresh token"""
    if token_type == 'refresh':
        exp_delta = timedelta(days=REFRESH_TOKEN_EXPIRY_DAYS)
    else:
        exp_delta = timedelta(hours=JWT_EXPIRY_HOURS)
    
    payload = {
        'user_id': str(user_id),
        'email': email,
        'token_type': token_type,
        'exp': datetime.utcnow() + exp_delta,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token, token_type='access'):
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        if payload.get('token_type') != token_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': 'Authentication required',
                'error': 'Missing or invalid authorization header'
            }), 401
        
        token = auth_header.split(' ')[1]
        payload = verify_jwt_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'message': 'Invalid or expired token',
                'error': 'Authentication failed'
            }), 401
        
        # Add user info to request
        request.user_id = payload['user_id']
        request.user_email = payload['email']
        
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'error': 'Request body is required'
            }), 400
        
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validation
        if not name:
            return jsonify({
                'success': False,
                'message': 'Name is required',
                'error': 'Please provide your full name'
            }), 400
        
        if not email or not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Valid email is required',
                'error': 'Please provide a valid email address'
            }), 400
        
        is_valid, password_message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': 'Password validation failed',
                'error': password_message
            }), 400
        
        # Check if user already exists
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        existing_user = users_collection.find_one({'email': email})
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'Email already registered',
                'error': 'An account with this email already exists'
            }), 409
        
        # Create user
        hashed_password = generate_password_hash(password)
        user_doc = {
            'name': name,
            'email': email,
            'password': hashed_password,
            'plan_type': 'free',
            'is_active': True,
            'email_verified': False,
            'connected_platforms': [],
            'posts_this_month': 0,
            'total_posts': 0,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'preferences': {
                'timezone': 'UTC',
                'email_notifications': True,
                'auto_posting_enabled': False
            }
        }
        
        result = users_collection.insert_one(user_doc)
        user_id = result.inserted_id
        
        # Generate access token
        access_token = generate_jwt_token(user_id, email)
        
        # Return user data (without password)
        user_data = {
            'id': str(user_id),
            'name': name,
            'email': email,
            'plan_type': 'free',
            'is_active': True,
            'connected_platforms': [],
            'posts_this_month': 0,
            'total_posts': 0,
            'created_at': user_doc['created_at'].isoformat(),
            'preferences': user_doc['preferences']
        }
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRY_HOURS * 3600,
            'user': user_data
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Registration failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'message': 'No data provided',
                'error': 'Email and password are required'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required',
                'error': 'Please provide both email and password'
            }), 400
        
        # Find user
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'email': email})
        
        if not user or not check_password_hash(user['password'], password):
            return jsonify({
                'success': False,
                'message': 'Invalid credentials',
                'error': 'Email or password is incorrect'
            }), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({
                'success': False,
                'message': 'Account deactivated',
                'error': 'Please contact support to reactivate your account'
            }), 403
        
        # Update last login
        users_collection.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'last_login': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        # Generate access token
        access_token = generate_jwt_token(user['_id'], email)
        
        # Prepare user data
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'plan_type': user.get('plan_type', 'free'),
            'is_active': user.get('is_active', True),
            'connected_platforms': user.get('connected_platforms', []),
            'posts_this_month': user.get('posts_this_month', 0),
            'total_posts': user.get('total_posts', 0),
            'created_at': user['created_at'].isoformat(),
            'last_login': datetime.utcnow().isoformat(),
            'preferences': user.get('preferences', {})
        }
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_EXPIRY_HOURS * 3600,
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get user profile"""
    try:
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'_id': ObjectId(request.user_id)})
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'Your account may have been deleted'
            }), 404
        
        # Get connected platforms count
        social_accounts = get_collection('social_accounts')
        connected_count = 0
        if social_accounts:
            connected_count = social_accounts.count_documents({
                'user_id': ObjectId(request.user_id),
                'is_active': True
            })
        
        # Get recent posts count
        posts_collection = get_collection('posts')
        recent_posts = 0
        if posts_collection:
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_posts = posts_collection.count_documents({
                'user_id': ObjectId(request.user_id),
                'created_at': {'$gte': thirty_days_ago}
            })
        
        user_data = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'plan_type': user.get('plan_type', 'free'),
            'is_active': user.get('is_active', True),
            'email_verified': user.get('email_verified', False),
            'connected_platforms': user.get('connected_platforms', []),
            'connected_platforms_count': connected_count,
            'posts_this_month': user.get('posts_this_month', 0),
            'total_posts': user.get('total_posts', 0),
            'recent_posts_30_days': recent_posts,
            'created_at': user['created_at'].isoformat(),
            'updated_at': user.get('updated_at', user['created_at']).isoformat(),
            'last_login': user.get('last_login').isoformat() if user.get('last_login') else None,
            'preferences': user.get('preferences', {})
        }
        
        return jsonify({
            'success': True,
            'message': 'Profile retrieved successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to retrieve profile',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update user profile"""
    try:
        current_user_id = request.user_id
        data = request.get_json()
        
        # Get user
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'User not found'
            }), 404
        
        # Allowed fields to update
        allowed_fields = ['name', 'preferences']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        # Validate name if provided
        if 'name' in update_data:
            if not update_data['name'] or len(update_data['name'].strip()) < 2:
                return jsonify({
                    'success': False,
                    'message': 'Invalid name',
                    'error': 'Name must be at least 2 characters long'
                }), 400
            update_data['name'] = update_data['name'].strip()
        
        # Validate preferences if provided
        if 'preferences' in update_data:
            allowed_prefs = ['timezone', 'email_notifications', 'auto_posting_enabled']
            preferences = {}
            for pref in allowed_prefs:
                if pref in update_data['preferences']:
                    preferences[pref] = update_data['preferences'][pref]
            update_data['preferences'] = {**user.get('preferences', {}), **preferences}
        
        if not update_data:
            return jsonify({
                'success': False,
                'message': 'No data to update',
                'error': 'Please provide data to update'
            }), 400
        
        # Update user
        update_data['updated_at'] = datetime.utcnow()
        
        result = users_collection.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': update_data}
        )
        
        if result.modified_count == 0:
            return jsonify({
                'success': False,
                'message': 'Update failed',
                'error': 'No changes were made'
            }), 400
        
        # Get updated user data
        updated_user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        user_data = {
            'id': str(updated_user['_id']),
            'email': updated_user['email'],
            'name': updated_user['name'],
            'plan_type': updated_user['plan_type'],
            'is_active': updated_user['is_active'],
            'preferences': updated_user.get('preferences', {}),
            'updated_at': updated_user['updated_at'].isoformat()
        }
        
        logger.info(f"Profile updated for user: {updated_user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user_data
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Profile update failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change password for authenticated user"""
    try:
        current_user_id = request.user_id
        data = request.get_json()
        
        required_fields = ['current_password', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required',
                    'error': f'Please provide {field}'
                }), 400
        
        current_password = data['current_password']
        new_password = data['new_password']
        
        # Get user
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'User not found'
            }), 404
        
        # Verify current password
        if not check_password_hash(user['password'], current_password):
            return jsonify({
                'success': False,
                'message': 'Invalid password',
                'error': 'Current password is incorrect'
            }), 400
        
        # Validate new password
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': 'Password validation failed',
                'error': password_message
            }), 400
        
        # Check if new password is different
        if current_password == new_password:
            return jsonify({
                'success': False,
                'message': 'Same password',
                'error': 'New password must be different from current password'
            }), 400
        
        # Update password
        new_password_hash = generate_password_hash(new_password)
        
        users_collection.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {
                'password': new_password_hash,
                'updated_at': datetime.utcnow()
            }}
        )
        
        logger.info(f"Password changed for user: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Password change failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email"""
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({
                'success': False,
                'message': 'Email required',
                'error': 'Please provide your email address'
            }), 400
        
        email = data['email'].lower().strip()
        
        # Check if user exists
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'email': email})
        if not user:
            # Don't reveal if email exists or not (security best practice)
            return jsonify({
                'success': True,
                'message': 'If an account with this email exists, you will receive password reset instructions.'
            }), 200
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Save reset token to database
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password_reset_token': reset_token,
                'password_reset_expires': reset_expires,
                'updated_at': datetime.utcnow()
            }}
        )
        
        # In production, send actual email here
        # For development, just log the token
        logger.info(f"Password reset token for {email}: {reset_token}")
        
        return jsonify({
            'success': True,
            'message': 'If an account with this email exists, you will receive password reset instructions.',
            'reset_token': reset_token  # Remove this in production
        }), 200
        
    except Exception as e:
        logger.error(f"Password reset request error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Reset request failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        required_fields = ['token', 'new_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required',
                    'error': f'Please provide {field}'
                }), 400
        
        token = data['token']
        new_password = data['new_password']
        
        # Validate new password
        is_valid, password_message = validate_password(new_password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': 'Password validation failed',
                'error': password_message
            }), 400
        
        # Find user with valid reset token
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({
            'password_reset_token': token,
            'password_reset_expires': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'Invalid token',
                'error': 'Password reset token is invalid or expired'
            }), 400
        
        # Update password and remove reset token
        new_password_hash = generate_password_hash(new_password)
        
        users_collection.update_one(
            {'_id': user['_id']},
            {'$set': {
                'password': new_password_hash,
                'updated_at': datetime.utcnow()
            }, '$unset': {
                'password_reset_token': '',
                'password_reset_expires': ''
            }}
        )
        
        logger.info(f"Password reset successful for user: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Password reset successful. You can now login with your new password.'
        }), 200
        
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Password reset failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/verify-token', methods=['POST'])
@require_auth
def verify_token():
    """Verify if JWT token is valid"""
    try:
        current_user_id = request.user_id
        
        # Get user to ensure they still exist and are active
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        if not user or not user.get('is_active', True):
            return jsonify({
                'success': False,
                'message': 'Invalid token',
                'error': 'Token is invalid or user is disabled'
            }), 401
        
        return jsonify({
            'success': True,
            'valid': True,
            'user_id': current_user_id,
            'email': user['email']
        }), 200
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({
            'success': False,
            'valid': False,
            'error': 'Token verification failed'
        }), 401

@auth_bp.route('/logout', methods=['POST'])
@require_auth
def logout():
    """Logout user (client-side token invalidation)"""
    try:
        # In a production app, you might want to blacklist the token
        # For now, we'll rely on client-side token removal
        
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed',
            'error': 'An unexpected error occurred'
        }), 500

@auth_bp.route('/delete-account', methods=['DELETE'])
@require_auth
def delete_account():
    """Delete user account (soft delete)"""
    try:
        current_user_id = request.user_id
        
        # Get user
        users_collection = get_collection('users')
        if not users_collection:
            return jsonify({
                'success': False,
                'message': 'Database unavailable',
                'error': 'Please try again later'
            }), 503
        
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found',
                'error': 'User not found'
            }), 404
        
        # Soft delete - deactivate account instead of deleting
        users_collection.update_one(
            {'_id': ObjectId(current_user_id)},
            {'$set': {
                'is_active': False,
                'deactivated_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }}
        )
        
        # Deactivate all social accounts
        social_accounts_collection = get_collection('social_accounts')
        if social_accounts_collection:
            social_accounts_collection.update_many(
                {'user_id': ObjectId(current_user_id)},
                {'$set': {'is_active': False, 'updated_at': datetime.utcnow()}}
            )
        
        logger.info(f"Account deleted for user: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Account deleted successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Account deletion error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Account deletion failed',
            'error': 'An unexpected error occurred'
        }), 500

# Error handlers specific to auth blueprint
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'message': 'Bad request',
        'error': 'The request was invalid'
    }), 400

@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'message': 'Unauthorized',
        'error': 'Authentication required'
    }), 401

@auth_bp.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
        'success': False,
        'message': 'Unprocessable entity',
        'error': 'The request contains semantic errors'
    }), 422