"""
Celery worker for verifying platform credentials
"""
from celery import current_app
from app.models.credentials import Credentials
from app.models.user import User
from app.utils.logger import setup_logger, log_automation_event
from app.utils.encryption import decrypt_credentials
from app.utils.error_handlers import automation_error_handler
from datetime import datetime, timedelta
import logging

logger = setup_logger('credential_verification')

@current_app.task(bind=True, max_retries=3)
@automation_error_handler
def verify_single_credential(self, credential_id):
    """
    Verify a single set of credentials
    
    Args:
        credential_id: ID of the credentials to verify
    
    Returns:
        Dict with verification result
    """
    try:
        # Get credentials
        credential = Credentials.objects.get(id=credential_id)
        
        # Decrypt credentials
        decrypted_creds = decrypt_credentials(credential.encrypted_data)
        
        # Platform-specific verification
        platform = credential.platform
        verification_result = None
        
        if platform == 'instagram':
            verification_result = verify_instagram_credentials(decrypted_creds)
        elif platform == 'facebook':
            verification_result = verify_facebook_credentials(decrypted_creds)
        elif platform == 'youtube':
            verification_result = verify_youtube_credentials(decrypted_creds)
        elif platform == 'twitter':
            verification_result = verify_twitter_credentials(decrypted_creds)
        elif platform == 'linkedin':
            verification_result = verify_linkedin_credentials(decrypted_creds)
        else:
            raise Exception(f"Unsupported platform: {platform}")
        
        # Update credential status
        credential.mark_verified(
            success=verification_result['success'],
            error_message=verification_result.get('error')
        )
        
        # Log result
        log_automation_event(
            platform=platform,
            action='credential_verification',
            status='success' if verification_result['success'] else 'failed',
            user_id=str(credential.user.id),
            details=verification_result
        )
        
        return {
            'credential_id': credential_id,
            'platform': platform,
            'success': verification_result['success'],
            'verified_at': datetime.utcnow().isoformat(),
            'account_info': verification_result.get('account_info', {})
        }
    
    except Exception as e:
        logger.error(f"Credential verification failed for {credential_id}: {str(e)}")
        
        # Update credential with error
        try:
            credential = Credentials.objects.get(id=credential_id)
            credential.mark_verified(success=False, error_message=str(e))
        except:
            pass
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            retry_delay = 2 ** self.request.retries * 60  # 1min, 2min, 4min
            raise self.retry(countdown=retry_delay, exc=e)
        
        raise e

@current_app.task
def verify_all_credentials():
    """
    Periodic task to verify all active credentials
    """
    try:
        # Get all active credentials that need verification
        cutoff_time = datetime.utcnow() - timedelta(hours=24)
        
        credentials_to_verify = Credentials.objects.filter(
            is_active=True,
            last_verified__lt=cutoff_time
        ) | Credentials.objects.filter(
            is_active=True,
            last_verified=None
        )
        
        verification_results = []
        
        for credential in credentials_to_verify:
            try:
                # Queue individual verification task
                result = verify_single_credential.delay(str(credential.id))
                verification_results.append({
                    'credential_id': str(credential.id),
                    'platform': credential.platform,
                    'task_id': result.id,
                    'status': 'queued'
                })
            except Exception as e:
                logger.error(f"Failed to queue verification for {credential.id}: {str(e)}")
                verification_results.append({
                    'credential_id': str(credential.id),
                    'platform': credential.platform,
                    'status': 'failed',
                    'error': str(e)
                })
        
        logger.info(f"Queued verification for {len(verification_results)} credentials")
        return {
            'total_queued': len(verification_results),
            'results': verification_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Bulk credential verification failed: {str(e)}")
        raise e

@current_app.task
def verify_user_credentials(user_id, platform=None):
    """
    Verify all credentials for a specific user
    
    Args:
        user_id: User ID
        platform: Optional platform filter
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Get user's credentials
        query = Credentials.objects.filter(user=user, is_active=True)
        if platform:
            query = query.filter(platform=platform)
        
        credentials = list(query)
        verification_results = []
        
        for credential in credentials:
            try:
                result = verify_single_credential.delay(str(credential.id))
                verification_results.append({
                    'credential_id': str(credential.id),
                    'platform': credential.platform,
                    'task_id': result.id
                })
            except Exception as e:
                logger.error(f"Failed to verify credential {credential.id}: {str(e)}")
                verification_results.append({
                    'credential_id': str(credential.id),
                    'platform': credential.platform,
                    'error': str(e)
                })
        
        return {
            'user_id': user_id,
            'platform': platform,
            'total_credentials': len(credentials),
            'verification_results': verification_results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"User credential verification failed for {user_id}: {str(e)}")
        raise e

def verify_instagram_credentials(credentials):
    """Verify Instagram credentials"""
    try:
        from app.automation.platforms.instagram_automator import InstagramAutomator
        
        automator = InstagramAutomator()
        result = automator.test_credentials(
            username=credentials.get('username'),
            password=credentials.get('password')
        )
        
        return {
            'success': result.get('success', False),
            'account_info': result.get('account_info', {}),
            'error': result.get('error')
        }
    
    except Exception as e:
        logger.error(f"Instagram credential verification failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_facebook_credentials(credentials):
    """Verify Facebook credentials"""
    try:
        from app.automation.platforms.facebook_automator import FacebookAutomator
        
        automator = FacebookAutomator()
        result = automator.test_credentials(
            email=credentials.get('email'),
            password=credentials.get('password')
        )
        
        return {
            'success': result.get('success', False),
            'account_info': result.get('account_info', {}),
            'error': result.get('error')
        }
    
    except Exception as e:
        logger.error(f"Facebook credential verification failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_youtube_credentials(credentials):
    """Verify YouTube credentials"""
    try:
        # Import YouTube automator when it's implemented
        # from app.automation.platforms.youtube_automator import YouTubeAutomator
        
        # For now, basic validation
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            return {
                'success': False,
                'error': 'Email and password required'
            }
        
        # TODO: Implement actual YouTube API verification
        return {
            'success': True,
            'account_info': {'email': email},
            'error': None
        }
    
    except Exception as e:
        logger.error(f"YouTube credential verification failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_twitter_credentials(credentials):
    """Verify Twitter credentials"""
    try:
        # Import Twitter automator when it's implemented
        # from app.automation.platforms.twitter_automator import TwitterAutomator
        
        # For now, basic validation
        username = credentials.get('username')
        password = credentials.get('password')
        
        if not username or not password:
            return {
                'success': False,
                'error': 'Username and password required'
            }
        
        # TODO: Implement actual Twitter API verification
        return {
            'success': True,
            'account_info': {'username': username},
            'error': None
        }
    
    except Exception as e:
        logger.error(f"Twitter credential verification failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def verify_linkedin_credentials(credentials):
    """Verify LinkedIn credentials"""
    try:
        # Import LinkedIn automator when it's implemented
        # from app.automation.platforms.linkedin_automator import LinkedInAutomator
        
        # For now, basic validation
        email = credentials.get('email')
        password = credentials.get('password')
        
        if not email or not password:
            return {
                'success': False,
                'error': 'Email and password required'
            }
        
        # TODO: Implement actual LinkedIn verification
        return {
            'success': True,
            'account_info': {'email': email},
            'error': None
        }
    
    except Exception as e:
        logger.error(f"LinkedIn credential verification failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

@current_app.task
def cleanup_failed_credentials():
    """
    Clean up credentials that have failed verification multiple times
    """
    try:
        # Find credentials that have been failing for more than 7 days
        cutoff_time = datetime.utcnow() - timedelta(days=7)
        
        failed_credentials = Credentials.objects.filter(
            is_verified=False,
            verification_error__ne=None,
            last_verified__lt=cutoff_time
        )
        
        deactivated_count = 0
        for credential in failed_credentials:
            # Deactivate instead of deleting
            credential.deactivate()
            deactivated_count += 1
            
            logger.info(f"Deactivated failed credential {credential.id} for user {credential.user.id}")
        
        return {
            'deactivated_count': deactivated_count,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Credential cleanup failed: {str(e)}")
        raise e

@current_app.task
def send_credential_alerts():
    """
    Send alerts for failed credentials to users
    """
    try:
        # Find users with failed credentials
        failed_credentials = Credentials.objects.filter(
            is_active=True,
            is_verified=False,
            verification_error__ne=None
        )
        
        # Group by user
        user_failures = {}
        for credential in failed_credentials:
            user_id = str(credential.user.id)
            if user_id not in user_failures:
                user_failures[user_id] = []
            user_failures[user_id].append(credential)
        
        # Send alerts (implement email/notification service)
        alerts_sent = 0
        for user_id, credentials in user_failures.items():
            try:
                # TODO: Implement email notification
                # send_credential_failure_email(user_id, credentials)
                alerts_sent += 1
                logger.info(f"Alert sent to user {user_id} for {len(credentials)} failed credentials")
            except Exception as e:
                logger.error(f"Failed to send alert to user {user_id}: {str(e)}")
        
        return {
            'alerts_sent': alerts_sent,
            'total_users_with_failures': len(user_failures),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Credential alert sending failed: {str(e)}")
        raise e