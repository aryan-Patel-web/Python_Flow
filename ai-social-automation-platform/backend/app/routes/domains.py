# app/routes/domains.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
domains_bp = Blueprint('domains', __name__)

@domains_bp.route('/', methods=['GET'])
def get_available_domains():
    """Get all available content domains"""
    try:
        domains = current_app.config['CONTENT_DOMAINS']
        return jsonify({
            'success': True,
            'domains': domains
        }), 200
        
        
    except Exception as e:
        logger.error(f"Get domains error: {str(e)}")
        return jsonify({'error': 'Failed to fetch domains'}), 500

@domains_bp.route('/select', methods=['POST'])
@jwt_required()
def select_domains():
    """Select content domains for user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        selected_domains = data.get('domains', [])
        posting_schedule = data.get('posting_schedule', {})
        daily_limits = data.get('daily_limits', {})
        
        if not selected_domains:
            return jsonify({'error': 'At least one domain must be selected'}), 400
        
        # Validate domains
        available_domains = current_app.config['CONTENT_DOMAINS']
        for domain in selected_domains:
            if domain not in available_domains:
                return jsonify({'error': f'Domain {domain} is not available'}), 400
        
        # Save user domain preferences
        domain_config = {
            'user_id': ObjectId(user_id),
            'selected_domains': selected_domains,
            'posting_schedule': posting_schedule,
            'daily_limits': daily_limits,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'active': True
        }
        
        # Upsert domain configuration
        current_app.db.user_domains.update_one(
            {'user_id': ObjectId(user_id)},
            {'$set': domain_config},
            upsert=True
        )
        
        logger.info(f"Domains selected for user {user_id}: {selected_domains}")
        
        return jsonify({
            'success': True,
            'message': 'Content domains selected successfully',
            'selected_domains': selected_domains
        }), 201
        
    except Exception as e:
        logger.error(f"Select domains error: {str(e)}")
        return jsonify({'error': 'Failed to select domains'}), 500

@domains_bp.route('/user', methods=['GET'])
@jwt_required()
def get_user_domains():
    """Get user's selected domains"""
    try:
        user_id = get_jwt_identity()
        
        user_domains = current_app.db.user_domains.find_one({
            'user_id': ObjectId(user_id),
            'active': True
        })
        
        if not user_domains:
            return jsonify({
                'success': True,
                'selected_domains': [],
                'posting_schedule': {},
                'daily_limits': {}
            }), 200
        
        return jsonify({
            'success': True,
            'selected_domains': user_domains.get('selected_domains', []),
            'posting_schedule': user_domains.get('posting_schedule', {}),
            'daily_limits': user_domains.get('daily_limits', {}),
            'updated_at': user_domains.get('updated_at')
        }), 200
        
    except Exception as e:
        logger.error(f"Get user domains error: {str(e)}")
        return jsonify({'error': 'Failed to fetch user domains'}), 500

@domains_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_domain_settings():
    """Update domain settings for user"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        update_fields = {}
        
        if 'posting_schedule' in data:
            update_fields['posting_schedule'] = data['posting_schedule']
        
        if 'daily_limits' in data:
            update_fields['daily_limits'] = data['daily_limits']
        
        if 'selected_domains' in data:
            update_fields['selected_domains'] = data['selected_domains']
        
        if update_fields:
            update_fields['updated_at'] = datetime.utcnow()
            
            current_app.db.user_domains.update_one(
                {'user_id': ObjectId(user_id)},
                {'$set': update_fields}
            )
        
        return jsonify({
            'success': True,
            'message': 'Domain settings updated successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Update domain settings error: {str(e)}")
        return jsonify({'error': 'Failed to update domain settings'}), 500

@domains_bp.route('/preview', methods=['POST'])
@jwt_required()
def preview_domain_content():
    """Preview content for a specific domain"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        domain = data.get('domain')
        platform = data.get('platform', 'instagram')
        
        if not domain:
            return jsonify({'error': 'Domain is required'}), 400
        
        # Import here to avoid circular imports
        from app.ai.content_generators.base_generator import ContentGenerator
        
        # Initialize content generator
        content_generator = ContentGenerator(
            current_app.config['MISTRAL_API_KEY'],
            current_app.config['GROQ_API_KEY']
        )
        
        # Generate preview content
        result = content_generator.generate_content(domain, platform)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'preview_content': result['content'],
                'domain': domain,
                'platform': platform,
                'provider': result.get('provider')
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to generate preview')
            }), 500
        
    except Exception as e:
        logger.error(f"Preview content error: {str(e)}")
        return jsonify({'error': 'Failed to generate preview content'}), 500