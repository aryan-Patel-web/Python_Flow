"""
Authentication Routes for VelocityPost.ai
Handles user registration, login, JWT tokens
"""

from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
from datetime import datetime, timedelta
import re
from bson import ObjectId

from app.utils.database import get_database
from app.utils.validators import validate_email, validate_password
from app.utils.helpers import generate_response

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user with free plan"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return generate_response(False, f'{field.title()} is required', status_code=400)
        
        name = data['name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        
        # Validate email format
        if not validate_email(email):
            return generate_response(False, 'Invalid email format', status_code=400)
        
        # Validate password strength
        if not validate_password(password):
            return generate_response(False, 'Password must be at least 8 characters with uppercase, lowercase, number and special character', status_code=400)
        
        # Check if user already exists
        db = get_database()
        existing_user = db.users.find_one({'email': email})
        
        if existing_user:
            return generate_response(False, 'User already exists with this email', status_code=409)
        
        # Create user with free plan
        hashed_password = generate_password_hash(password)
        
        user_data = {
            'name': name,
            'email': email,
            'password_hash': hashed_password,
            'subscription_plan': 'free',  # Start with free plan
            'plan_limits': {
                'max_platforms': 2,
                'max_posts_per_day': 2,
                'max_domains': 3
            },
            'connected_platforms': [],
            'selected_domains': [],
            'auto_posting_active': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'email_verified': False,
            'is_active': True
        }
        
        result = db.users.insert_one(user_data)
        user_id = str(result.inserted_id)
        
        # Create JWT tokens
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(days=30)
        )
        
        # Return user data (without password)
        user_response = {
            'id': user_id,
            'name': name,
            'email': email,
            'subscription_plan': 'free',
            'plan_limits': user_data['plan_limits'],
            'connected_platforms': [],
            'auto_posting_active': False
        }
        
        return generate_response(
            True, 
            'Registration successful', 
            data={
                'user': user_response,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )
        
    except Exception as e:
        current_app.logger.error(f'Registration error: {str(e)}')
        return generate_response(False, 'Registration failed', status_code=500)

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login with email and password"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return generate_response(False, 'Email and password are required', status_code=400)
        
        # Find user
        db = get_database()
        user = db.users.find_one({'email': email})
        
        if not user:
            return generate_response(False, 'Invalid email or password', status_code=401)
        
        # Check password
        if not check_password_hash(user['password_hash'], password):
            return generate_response(False, 'Invalid email or password', status_code=401)
        
        # Check if user is active
        if not user.get('is_active', True):
            return generate_response(False, 'Account is deactivated', status_code=403)
        
        # Update last login
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'last_login': datetime.utcnow()}}
        )
        
        # Create JWT tokens
        user_id = str(user['_id'])
        access_token = create_access_token(
            identity=user_id,
            expires_delta=timedelta(hours=24)
        )
        refresh_token = create_refresh_token(
            identity=user_id,
            expires_delta=timedelta(days=30)
        )
        
        # Get connected platforms count
        connected_platforms = db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }).count()
        
        # Return user data (without password)
        user_response = {
            'id': user_id,
            'name': user['name'],
            'email': user['email'],
            'subscription_plan': user.get('subscription_plan', 'free'),
            'plan_limits': user.get('plan_limits', {}),
            'connected_platforms_count': connected_platforms,
            'auto_posting_active': user.get('auto_posting_active', False),
            'selected_domains': user.get('selected_domains', [])
        }
        
        return generate_response(
            True,
            'Login successful',
            data={
                'user': user_response,
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        )
        
    except Exception as e:
        current_app.logger.error(f'Login error: {str(e)}')
        return generate_response(False, 'Login failed', status_code=500)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        current_user_id = get_jwt_identity()
        
        # Create new access token
        new_access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=24)
        )
        
        return generate_response(
            True,
            'Token refreshed successfully',
            data={'access_token': new_access_token}
        )
        
    except Exception as e:
        current_app.logger.error(f'Token refresh error: {str(e)}')
        return generate_response(False, 'Token refresh failed', status_code=500)

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Get connected platforms
        connected_platforms = list(db.platform_connections.find({
            'user_id': ObjectId(user_id),
            'is_active': True
        }))
        
        platforms_data = []
        for platform in connected_platforms:
            platforms_data.append({
                'platform': platform['platform'],
                'username': platform['username'],
                'connected_at': platform['created_at'].isoformat(),
                'is_active': platform['is_active']
            })
        
        # Get usage stats for today
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        posts_today = db.posts.find({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today}
        }).count()
        
        user_response = {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'subscription_plan': user.get('subscription_plan', 'free'),
            'plan_limits': user.get('plan_limits', {}),
            'connected_platforms': platforms_data,
            'selected_domains': user.get('selected_domains', []),
            'auto_posting_active': user.get('auto_posting_active', False),
            'posts_today': posts_today,
            'created_at': user['created_at'].isoformat(),
            'email_verified': user.get('email_verified', False)
        }
        
        return generate_response(True, 'User profile retrieved', data={'user': user_response})
        
    except Exception as e:
        current_app.logger.error(f'Get current user error: {str(e)}')
        return generate_response(False, 'Failed to get user profile', status_code=500)

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)"""
    try:
        # In a more complex setup, you might want to blacklist the token
        # For now, we'll just return success and let client remove token
        return generate_response(True, 'Logout successful')
        
    except Exception as e:
        current_app.logger.error(f'Logout error: {str(e)}')
        return generate_response(False, 'Logout failed', status_code=500)

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return generate_response(False, 'Email is required', status_code=400)
        
        db = get_database()
        user = db.users.find_one({'email': email})
        
        if not user:
            # Don't reveal if email exists or not for security
            return generate_response(True, 'If email exists, reset instructions have been sent')
        
        # Generate reset token (in production, use proper token generation)
        reset_token = create_access_token(
            identity=str(user['_id']),
            expires_delta=timedelta(hours=1)
        )
        
        # Store reset token (in production, store hash of token)
        db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'reset_token': reset_token,
                    'reset_token_expires': datetime.utcnow() + timedelta(hours=1)
                }
            }
        )
        
        # TODO: Send email with reset link
        # send_password_reset_email(email, reset_token)
        
        return generate_response(True, 'Password reset instructions sent to your email')
        
    except Exception as e:
        current_app.logger.error(f'Forgot password error: {str(e)}')
        return generate_response(False, 'Failed to process password reset request', status_code=500)

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        token = data.get('token')
        new_password = data.get('password')
        
        if not token or not new_password:
            return generate_response(False, 'Token and new password are required', status_code=400)
        
        if not validate_password(new_password):
            return generate_response(False, 'Password must be at least 8 characters with uppercase, lowercase, number and special character', status_code=400)
        
        db = get_database()
        
        # Find user with valid reset token
        user = db.users.find_one({
            'reset_token': token,
            'reset_token_expires': {'$gt': datetime.utcnow()}
        })
        
        if not user:
            return generate_response(False, 'Invalid or expired reset token', status_code=400)
        
        # Update password and remove reset token
        hashed_password = generate_password_hash(new_password)
        
        db.users.update_one(
            {'_id': user['_id']},
            {
                '$set': {
                    'password_hash': hashed_password,
                    'updated_at': datetime.utcnow()
                },
                '$unset': {
                    'reset_token': '',
                    'reset_token_expires': ''
                }
            }
        )
        
        return generate_response(True, 'Password reset successful')
        
    except Exception as e:
        current_app.logger.error(f'Reset password error: {str(e)}')
        return generate_response(False, 'Failed to reset password', status_code=500)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return generate_response(False, 'Current and new password are required', status_code=400)
        
        if not validate_password(new_password):
            return generate_response(False, 'New password must be at least 8 characters with uppercase, lowercase, number and special character', status_code=400)
        
        db = get_database()
        user = db.users.find_one({'_id': ObjectId(user_id)})
        
        if not user:
            return generate_response(False, 'User not found', status_code=404)
        
        # Verify current password
        if not check_password_hash(user['password_hash'], current_password):
            return generate_response(False, 'Current password is incorrect', status_code=400)
        
        # Update to new password
        hashed_password = generate_password_hash(new_password)
        
        db.users.update_one(
            {'_id': ObjectId(user_id)},
            {
                '$set': {
                    'password_hash': hashed_password,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        return generate_response(True, 'Password changed successfully')
        
    except Exception as e:
        current_app.logger.error(f'Change password error: {str(e)}')
        return generate_response(False, 'Failed to change password', status_code=500)

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Fields that can be updated
        allowed_fields = ['name']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field].strip() if isinstance(data[field], str) else data[field]
        
        if not update_data:
            return generate_response(False, 'No valid fields to update', status_code=400)
        
        # Add update timestamp
        update_data['updated_at'] = datetime.utcnow()
        
        db = get_database()
        result = db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        if result.matched_count == 0:
            return generate_response(False, 'User not found', status_code=404)
        
        # Get updated user
        updated_user = db.users.find_one({'_id': ObjectId(user_id)})
        
        user_response = {
            'id': str(updated_user['_id']),
            'name': updated_user['name'],
            'email': updated_user['email'],
            'updated_at': updated_user['updated_at'].isoformat()
        }
        
        return generate_response(True, 'Profile updated successfully', data={'user': user_response})
        
    except Exception as e:
        current_app.logger.error(f'Update profile error: {str(e)}')
        return generate_response(False, 'Failed to update profile', status_code=500)