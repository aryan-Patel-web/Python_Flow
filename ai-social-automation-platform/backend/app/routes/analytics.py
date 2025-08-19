# app/routes/analytics.py
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/overview', methods=['GET'])
@jwt_required()
def get_analytics_overview():
    """Get analytics overview for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get date range from query params
        days = int(request.args.get('days', 30))
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Total posts count
        total_posts = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': start_date}
        })
        
        # Posts by platform
        posts_by_platform = list(current_app.db.posts.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': '$platform',
                'count': {'$sum': 1}
            }}
        ]))
        
        # Posts by domain
        posts_by_domain = list(current_app.db.posts.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }},
            {'$group': {
                '_id': '$domain',
                'count': {'$sum': 1}
            }}
        ]))
        
        # Recent activity (last 7 days)
        week_start = datetime.utcnow() - timedelta(days=7)
        recent_posts = list(current_app.db.posts.aggregate([
            {'$match': {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': week_start}
            }},
            {'$group': {
                '_id': {
                    'year': {'$year': '$created_at'},
                    'month': {'$month': '$created_at'},
                    'day': {'$dayOfMonth': '$created_at'}
                },
                'count': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]))
        
        # Success rate
        successful_posts = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'status': 'posted',
            'created_at': {'$gte': start_date}
        })
        
        success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
        
        # Content generation stats
        generated_content = current_app.db.generated_content.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': start_date}
        })
        
        return jsonify({
            'success': True,
            'overview': {
                'total_posts': total_posts,
                'successful_posts': successful_posts,
                'success_rate': round(success_rate, 2),
                'generated_content': generated_content,
                'posts_by_platform': {item['_id']: item['count'] for item in posts_by_platform},
                'posts_by_domain': {item['_id']: item['count'] for item in posts_by_domain},
                'recent_activity': recent_posts,
                'date_range': {
                    'start_date': start_date.isoformat(),
                    'end_date': datetime.utcnow().isoformat(),
                    'days': days
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get analytics overview error: {str(e)}")
        return jsonify({'error': 'Failed to fetch analytics overview'}), 500

@analytics_bp.route('/engagement', methods=['GET'])
@jwt_required()
def get_engagement_metrics():
    """Get engagement metrics for user's posts"""
    try:
        user_id = get_jwt_identity()
        platform = request.args.get('platform')
        days = int(request.args.get('days', 30))
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Build query
        query = {
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': start_date},
            'status': 'posted'
        }
        
        if platform:
            query['platform'] = platform
        
        # Get posts with engagement data
        posts_with_engagement = list(current_app.db.posts.find(query).sort('created_at', -1))
        
        # Calculate engagement metrics
        total_likes = 0
        total_comments = 0
        total_shares = 0
        post_count = len(posts_with_engagement)
        
        engagement_by_platform = {}
        top_performing_posts = []
        
        for post in posts_with_engagement:
            # Extract engagement data (mock data for now)
            likes = post.get('engagement', {}).get('likes', 0)
            comments = post.get('engagement', {}).get('comments', 0)
            shares = post.get('engagement', {}).get('shares', 0)
            
            total_likes += likes
            total_comments += comments
            total_shares += shares
            
            # Group by platform
            platform_name = post['platform']
            if platform_name not in engagement_by_platform:
                engagement_by_platform[platform_name] = {
                    'posts': 0, 'likes': 0, 'comments': 0, 'shares': 0
                }
            
            engagement_by_platform[platform_name]['posts'] += 1
            engagement_by_platform[platform_name]['likes'] += likes
            engagement_by_platform[platform_name]['comments'] += comments
            engagement_by_platform[platform_name]['shares'] += shares
            
            # Track top performing posts
            total_engagement = likes + comments + shares
            top_performing_posts.append({
                'id': str(post['_id']),
                'platform': platform_name,
                'content': post.get('content', '')[:100] + '...',
                'total_engagement': total_engagement,
                'likes': likes,
                'comments': comments,
                'shares': shares,
                'posted_at': post.get('posted_at', post['created_at']).isoformat()
            })
        
        # Sort top performing posts
        top_performing_posts.sort(key=lambda x: x['total_engagement'], reverse=True)
        top_performing_posts = top_performing_posts[:10]
        
        # Calculate averages
        avg_likes = total_likes / post_count if post_count > 0 else 0
        avg_comments = total_comments / post_count if post_count > 0 else 0
        avg_shares = total_shares / post_count if post_count > 0 else 0
        
        return jsonify({
            'success': True,
            'engagement_metrics': {
                'total_engagement': {
                    'likes': total_likes,
                    'comments': total_comments,
                    'shares': total_shares,
                    'posts': post_count
                },
                'average_engagement': {
                    'likes': round(avg_likes, 2),
                    'comments': round(avg_comments, 2),
                    'shares': round(avg_shares, 2)
                },
                'engagement_by_platform': engagement_by_platform,
                'top_performing_posts': top_performing_posts
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get engagement metrics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch engagement metrics'}), 500

@analytics_bp.route('/growth', methods=['GET'])
@jwt_required()
def get_growth_statistics():
    """Get growth statistics for user"""
    try:
        user_id = get_jwt_identity()
        
        # Get follower growth data (mock data for now)
        # In production, this would fetch from social media APIs
        
        current_date = datetime.utcnow()
        growth_data = []
        
        # Generate mock growth data for the last 30 days
        for i in range(30):
            date = current_date - timedelta(days=29-i)
            
            # Mock follower counts (would be real data from APIs)
            instagram_followers = 1000 + i * 5
            facebook_followers = 800 + i * 3
            youtube_subscribers = 500 + i * 2
            
            growth_data.append({
                'date': date.strftime('%Y-%m-%d'),
                'instagram_followers': instagram_followers,
                'facebook_followers': facebook_followers,
                'youtube_subscribers': youtube_subscribers,
                'total_followers': instagram_followers + facebook_followers + youtube_subscribers
            })
        
        # Calculate growth rates
        if len(growth_data) >= 2:
            latest = growth_data[-1]
            previous = growth_data[-2]
            
            instagram_growth = latest['instagram_followers'] - growth_data[0]['instagram_followers']
            facebook_growth = latest['facebook_followers'] - growth_data[0]['facebook_followers']
            youtube_growth = latest['youtube_subscribers'] - growth_data[0]['youtube_subscribers']
            
            growth_rates = {
                'instagram': round((instagram_growth / growth_data[0]['instagram_followers']) * 100, 2),
                'facebook': round((facebook_growth / growth_data[0]['facebook_followers']) * 100, 2),
                'youtube': round((youtube_growth / growth_data[0]['youtube_subscribers']) * 100, 2)
            }
        else:
            growth_rates = {'instagram': 0, 'facebook': 0, 'youtube': 0}
        
        # Content performance correlation
        posts_last_30_days = current_app.db.posts.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': current_date - timedelta(days=30)},
            'status': 'posted'
        })
        
        return jsonify({
            'success': True,
            'growth_statistics': {
                'follower_growth': growth_data,
                'growth_rates': growth_rates,
                'current_totals': {
                    'instagram_followers': growth_data[-1]['instagram_followers'] if growth_data else 0,
                    'facebook_followers': growth_data[-1]['facebook_followers'] if growth_data else 0,
                    'youtube_subscribers': growth_data[-1]['youtube_subscribers'] if growth_data else 0,
                    'total_followers': growth_data[-1]['total_followers'] if growth_data else 0
                },
                'content_correlation': {
                    'posts_last_30_days': posts_last_30_days,
                    'avg_posts_per_day': round(posts_last_30_days / 30, 2)
                }
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get growth statistics error: {str(e)}")
        return jsonify({'error': 'Failed to fetch growth statistics'}), 500

@analytics_bp.route('/platform/<platform>', methods=['GET'])
@jwt_required()
def get_platform_analytics(platform):
    """Get analytics for specific platform"""
    try:
        user_id = get_jwt_identity()
        days = int(request.args.get('days', 30))
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Get posts for this platform
        posts = list(current_app.db.posts.find({
            'user_id': ObjectId(user_id),
            'platform': platform,
            'created_at': {'$gte': start_date}
        }).sort('created_at', -1))
        
        # Calculate platform-specific metrics
        total_posts = len(posts)
        successful_posts = len([p for p in posts if p.get('status') == 'posted'])
        
        # Best performing content types
        content_type_performance = {}
        domain_performance = {}
        
        for post in posts:
            content_type = post.get('content_type', 'text')
            domain = post.get('domain', 'unknown')
            
            # Mock engagement data
            engagement = post.get('engagement', {})
            total_engagement = sum(engagement.values()) if engagement else 0
            
            if content_type not in content_type_performance:
                content_type_performance[content_type] = {'count': 0, 'total_engagement': 0}
            content_type_performance[content_type]['count'] += 1
            content_type_performance[content_type]['total_engagement'] += total_engagement
            
            if domain not in domain_performance:
                domain_performance[domain] = {'count': 0, 'total_engagement': 0}
            domain_performance[domain]['count'] += 1
            domain_performance[domain]['total_engagement'] += total_engagement
        
        # Calculate averages
        for content_type in content_type_performance:
            count = content_type_performance[content_type]['count']
            if count > 0:
                content_type_performance[content_type]['avg_engagement'] = round(
                    content_type_performance[content_type]['total_engagement'] / count, 2
                )
        
        for domain in domain_performance:
            count = domain_performance[domain]['count']
            if count > 0:
                domain_performance[domain]['avg_engagement'] = round(
                    domain_performance[domain]['total_engagement'] / count, 2
                )
        
        # Posting schedule analysis
        posting_times = {}
        for post in posts:
            hour = post['created_at'].hour
            if hour not in posting_times:
                posting_times[hour] = 0
            posting_times[hour] += 1
        
        # Recent posts with details
        recent_posts = []
        for post in posts[:10]:
            recent_posts.append({
                'id': str(post['_id']),
                'content': post.get('content', '')[:100] + '...',
                'content_type': post.get('content_type', 'text'),
                'domain': post.get('domain', 'unknown'),
                'status': post.get('status', 'unknown'),
                'engagement': post.get('engagement', {}),
                'posted_at': post.get('posted_at', post['created_at']).isoformat(),
                'platform_url': post.get('platform_url')
            })
        
        return jsonify({
            'success': True,
            'platform_analytics': {
                'platform': platform,
                'summary': {
                    'total_posts': total_posts,
                    'successful_posts': successful_posts,
                    'success_rate': round((successful_posts / total_posts * 100) if total_posts > 0 else 0, 2)
                },
                'content_type_performance': content_type_performance,
                'domain_performance': domain_performance,
                'posting_schedule': posting_times,
                'recent_posts': recent_posts
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get platform analytics error: {str(e)}")
        return jsonify({'error': f'Failed to fetch {platform} analytics'}), 500

@analytics_bp.route('/export', methods=['POST'])
@jwt_required()
def export_analytics_data():
    """Export analytics data as CSV"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        export_type = data.get('type', 'posts')  # 'posts', 'engagement', 'growth'
        date_range = data.get('date_range', 30)
        platforms = data.get('platforms', [])
        
        start_date = datetime.utcnow() - timedelta(days=date_range)
        
        if export_type == 'posts':
            # Export posts data
            query = {
                'user_id': ObjectId(user_id),
                'created_at': {'$gte': start_date}
            }
            
            if platforms:
                query['platform'] = {'$in': platforms}
            
            posts = list(current_app.db.posts.find(query).sort('created_at', -1))
            
            # Convert to CSV format
            csv_data = []
            headers = ['Date', 'Platform', 'Content Type', 'Domain', 'Status', 'Likes', 'Comments', 'Shares', 'URL']
            csv_data.append(headers)
            
            for post in posts:
                engagement = post.get('engagement', {})
                row = [
                    post['created_at'].strftime('%Y-%m-%d %H:%M:%S'),
                    post.get('platform', ''),
                    post.get('content_type', ''),
                    post.get('domain', ''),
                    post.get('status', ''),
                    engagement.get('likes', 0),
                    engagement.get('comments', 0),
                    engagement.get('shares', 0),
                    post.get('platform_url', '')
                ]
                csv_data.append(row)
            
            return jsonify({
                'success': True,
                'export_data': csv_data,
                'filename': f'posts_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'
            }), 200
        
        else:
            return jsonify({'error': 'Export type not supported yet'}), 400
        
    except Exception as e:
        logger.error(f"Export analytics data error: {str(e)}")
        return jsonify({'error': 'Failed to export analytics data'}), 500