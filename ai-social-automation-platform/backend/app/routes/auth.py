# app/routes/auth.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import User
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '').strip()
        
        if not all([email, password, name]):
            return jsonify({'error': 'Email, password, and name are required'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long'}), 400
        
        user_model = User(current_app.db)
        
        # Check if user exists
        if user_model.find_by_email(email):
            return jsonify({'error': 'User already exists with this email'}), 400
        
        # Create user
        user_id = user_model.create_user(email, password, name)
        
        # Create access token
        access_token = create_access_token(identity=user_id)
        
        logger.info(f"New user registered: {email}")
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user_id,
                'email': email,
                'name': name,
                'subscription_plan': 'starter'
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password are required'}), 400
        
        user_model = User(current_app.db)
        user = user_model.verify_password(email, password)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        access_token = create_access_token(identity=str(user['_id']))
        
        logger.info(f"User logged in: {email}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'subscription_plan': user.get('subscription_plan', 'starter'),
                'daily_post_count': user.get('daily_post_count', 0),
                'settings': user.get('settings', {})
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed. Please try again.'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = get_jwt_identity()
        user_model = User(current_app.db)
        user = user_model.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': str(user['_id']),
                'email': user['email'],
                'name': user['name'],
                'subscription_plan': user.get('subscription_plan', 'starter'),
                'daily_post_count': user.get('daily_post_count', 0),
                'credits_used': user.get('credits_used', 0),
                'settings': user.get('settings', {}),
                'created_at': user['created_at'].isoformat()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return jsonify({'error': 'Failed to fetch profile'}), 500

@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        user_model = User(current_app.db)
        
        # Update allowed fields
        update_fields = {}
        if 'name' in data:
            update_fields['name'] = data['name'].strip()
        if 'settings' in data:
            update_fields['settings'] = data['settings']
        
        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            user_model.collection.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': update_fields}
            )
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Failed to update profile'}), 500