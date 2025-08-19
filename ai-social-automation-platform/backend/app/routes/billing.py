# app/routes/billing.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
billing_bp = Blueprint('billing', __name__)

@billing_bp.route('/plans', methods=['GET'])
def get_subscription_plans():
    """Get all available subscription plans"""
    try:
        plans = current_app.config['SUBSCRIPTION_PLANS']
        
        # Add features list for each plan
        enhanced_plans = {}
        for plan_name, plan_data in plans.items():
            enhanced_plans[plan_name] = {
                **plan_data,
                'features': get_plan_features(plan_name)
            }
        
        return jsonify({
            'success': True,
            'plans': enhanced_plans
        }), 200
        
    except Exception as e:
        logger.error(f"Get subscription plans error: {str(e)}")
        return jsonify({'error': 'Failed to fetch subscription plans'}), 500

def get_plan_features(plan_name):
    """Get features list for a specific plan"""
    features = {
        'starter': [
            '2 social media platforms',
            '3 posts per day',
            '3 content domains',
            'Basic automation',
            'Email support',
            'Content library access'
        ],
        'pro': [
            '5 social media platforms',
            '6 posts per day',
            '10 content domains',
            'Advanced automation',
            'Priority support',
            'Analytics dashboard',
            'Custom posting schedules',
            'Content optimization'
        ],
        'agency': [
            'Unlimited platforms',
            '20 posts per day',
            'All content domains',
            'Full automation suite',
            '24/7 priority support',
            'Advanced analytics',
            'API access',
            'White-label options',
            'Team management',
            'Custom integrations'
        ]
    }
    return features.get(plan_name, [])

@billing_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_current_subscription():
    """Get user's current subscription details"""
    try:
        user_id = get_jwt_identity()
        
        # Get user data
        user = current_app.db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get subscription data
        subscription = current_app.db.subscriptions.find_one({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
        
        current_plan = user.get('subscription_plan', 'starter')
        plan_details = current_app.config['SUBSCRIPTION_PLANS'].get(current_plan, {})
        
        # Calculate usage statistics
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        today_posts = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': today_start}
        })
        
        # Count connected platforms
        connected_platforms = current_app.db.credentials.count_documents({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
        
        # Get selected domains
        user_domains = current_app.db.user_domains.find_one({
            'user_id': ObjectId(user_id),
            'active': True
        })
        selected_domains_count = len(user_domains.get('selected_domains', [])) if user_domains else 0
        
        subscription_data = {
            'current_plan': current_plan,
            'plan_details': {
                **plan_details,
                'features': get_plan_features(current_plan)
            },
            'usage': {
                'posts_today': today_posts,
                'posts_limit': plan_details.get('max_posts_per_day', 0),
                'connected_platforms': connected_platforms,
                'platforms_limit': plan_details.get('max_platforms', 0),
                'selected_domains': selected_domains_count,
                'domains_limit': plan_details.get('max_domains', 0)
            },
            'subscription_status': 'active',
            'next_billing_date': None,
            'subscription_id': None
        }
        
        if subscription:
            subscription_data.update({
                'subscription_status': subscription.get('status', 'active'),
                'next_billing_date': subscription.get('next_billing_date'),
                'subscription_id': str(subscription['_id']),
                'created_at': subscription.get('created_at'),
                'billing_cycle': subscription.get('billing_cycle', 'monthly')
            })
        
        return jsonify({
            'success': True,
            'subscription': subscription_data
        }), 200
        
    except Exception as e:
        logger.error(f"Get current subscription error: {str(e)}")
        return jsonify({'error': 'Failed to fetch subscription details'}), 500

@billing_bp.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_plan():
    """Subscribe user to a new plan"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        plan_name = data.get('plan')
        billing_cycle = data.get('billing_cycle', 'monthly')  # 'monthly' or 'yearly'
        payment_method = data.get('payment_method', {})
        
        if not plan_name:
            return jsonify({'error': 'Plan name is required'}), 400
        
        if plan_name not in current_app.config['SUBSCRIPTION_PLANS']:
            return jsonify({'error': 'Invalid plan name'}), 400
        
        plan_details = current_app.config['SUBSCRIPTION_PLANS'][plan_name]
        
        # Calculate pricing based on billing cycle
        monthly_price = plan_details['price']
        if billing_cycle == 'yearly':
            # 20% discount for yearly billing
            total_price = monthly_price * 12 * 0.8
        else:
            total_price = monthly_price
        
        # In a real implementation, you would:
        # 1. Process payment using Stripe/PayPal/etc.
        # 2. Handle payment failures
        # 3. Send confirmation emails
        
        # For now, we'll create a mock subscription
        subscription_data = {
            'user_id': ObjectId(user_id),
            'plan_name': plan_name,
            'billing_cycle': billing_cycle,
            'price': total_price,
            'status': 'active',
            'created_at': datetime.utcnow(),
            'next_billing_date': datetime.utcnow() + timedelta(days=30 if billing_cycle == 'monthly' else 365),
            'payment_method': payment_method
        }
        
        # Cancel any existing active subscription
        current_app.db.subscriptions.update_many(
            {'user_id': ObjectId(user_id), 'status': 'active'},
            {'$set': {'status': 'cancelled', 'cancelled_at': datetime.utcnow()}}
        )
        
        # Create new subscription
        result = current_app.db.subscriptions.insert_one(subscription_data)
        
        # Update user's plan
        current_app.db.users.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'subscription_plan': plan_name, 'updated_at': datetime.utcnow()}}
        )
        
        logger.info(f"User {user_id} subscribed to {plan_name} plan")
        
        return jsonify({
            'success': True,
            'message': f'Successfully subscribed to {plan_name} plan',
            'subscription_id': str(result.inserted_id),
            'plan': plan_name,
            'billing_cycle': billing_cycle,
            'next_billing_date': subscription_data['next_billing_date'].isoformat()
        }), 201
        
    except Exception as e:
        logger.error(f"Subscribe to plan error: {str(e)}")
        return jsonify({'error': 'Failed to process subscription'}), 500

@billing_bp.route('/usage', methods=['GET'])
@jwt_required()
def get_usage_statistics():
    """Get detailed usage statistics for billing"""
    try:
        user_id = get_jwt_identity()
        
        # Get date range
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Daily usage breakdown
        daily_usage = list(current_app.db.posts.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'},
                    'day': {'$dayOfMonth': '$created_at'}
                },
                'posts_count': {'$sum': 1},
                'platforms': {'$addToSet': '$platform'}
            }},
            {'$sort': {'_id': 1}}
        ]))
        
        # Platform usage
        platform_usage = list(current_app.db.posts.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': '$platform',
                'posts_count': {'$sum': 1},
                'success_count': {
                    '$sum': {'$cond': [{'$eq': ['$status', 'posted']}, 1, 0]}
                }
            }}
        ]))
        
        # Content generation usage
        content_generation = current_app.db.generated_content.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': '$provider',
                'count': {'$sum': 1},
                'tokens_used': {'$sum': '$tokens_used'}
            }}
        ])
        
        # Current month usage
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        current_month_posts = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': month_start}
        })
        
        # Get user's plan limits
        user = current_app.db.users.find_one({'_id': ObjectId(user_id)})
        plan_name = user.get('subscription_plan', 'starter')
        plan_limits = current_app.config['SUBSCRIPTION_PLANS'].get(plan_name, {})
        
        return jsonify({
            'success': True,
            'usage_statistics': {
                'current_month_posts': current_month_posts,
                'daily_usage': daily_usage,
                'platform_usage': platform_usage,
                'content_generation': list(content_generation),
                'plan_limits': plan_limits,
                'usage_percentage': {
                    'posts': round((current_month_posts / (plan_limits.get('max_posts_per_day', 1) * 30)) * 100, 2)
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get usage statistics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch usage statistics'}), 500

@billing_bp.route('/invoices', methods=['GET'])
@jwt_required()
def get_billing_history():
    """Get user's billing history"""
    try:
        user_id = get_jwt_identity()
        
        # Get subscription history
        subscriptions = list(current_app.db.subscriptions.find({
            'user_id': ObjectId(user_id)
        }).sort('created_at', -1))
        
        # Convert to invoice format
        invoices = []
        for subscription in subscriptions:
            invoice = {
                'id': str(subscription['_id']),
                'plan_name': subscription.get('plan_name'),
                'amount': subscription.get('price'),
                'billing_cycle': subscription.get('billing_cycle'),
                'status': subscription.get('status'),
                'date': subscription.get('created_at').isoformat(),
                'next_billing_date': subscription.get('next_billing_date').isoformat() if subscription.get('next_billing_date') else None
            }
            invoices.append(invoice)
        
        return jsonify({
            'success': True,
            'invoices': invoices
        }), 200
        
    except Exception as e:
        logger.error(f"Get billing history error: {str(e)}")
        return jsonify({'error': 'Failed to fetch billing history'}), 500

@billing_bp.route('/cancel', methods=['POST'])
@jwt_required()
def cancel_subscription():
    """Cancel user's current subscription"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        cancellation_reason = data.get('reason', '')
        immediate = data.get('immediate', False)  # Cancel immediately or at end of billing period
        
        # Find active subscription
        subscription = current_app.db.subscriptions.find_one({
            'user_id': ObjectId(user_id),
            'status': 'active'
        })
        
        if not subscription:
            return jsonify({'error': 'No active subscription found'}), 404
        
        if immediate:
            # Cancel immediately - downgrade to starter plan
            current_app.db.subscriptions.update_one(
                {'_id': subscription['_id']},
                {
                    '$set': {
                        'status': 'cancelled',
                        'cancelled_at': datetime.utcnow(),
                        'cancellation_reason': cancellation_reason
                    }
                }
            )
            
            # Downgrade user to starter plan
            current_app.db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'subscription_plan': 'starter'}}
            )
            
            message = 'Subscription cancelled immediately. Account downgraded to Starter plan.'
        else:
            # Cancel at end of billing period
            current_app.db.subscriptions.update_one(
                {'_id': subscription['_id']},
                {
                    '$set': {
                        'status': 'cancelled_pending',
                        'cancellation_scheduled': subscription.get('next_billing_date'),
                        'cancellation_reason': cancellation_reason
                    }
                }
            )
            
            message = f'Subscription will be cancelled on {subscription.get("next_billing_date").strftime("%Y-%m-%d")}'
        
        logger.info(f"User {user_id} cancelled subscription. Reason: {cancellation_reason}")
        
        return jsonify({
            'success': True,
            'message': message,
            'immediate': immediate
        }), 200
        
    except Exception as e:
        logger.error(f"Cancel subscription error: {str(e)}")
        return jsonify({'error': 'Failed to cancel subscription'}), 500