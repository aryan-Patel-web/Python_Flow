import logging
from app.automation.platforms.instagram_automator import InstagramAutomator
from app.automation.platforms.facebook_automator import FacebookAutomator
from app.automation.platforms.youtube_automator import YouTubeAutomator

logger = logging.getLogger(__name__)

class AutoPoster:
    def __init__(self, config):
        self.config = config
        self.chrome_options = config.get('CHROME_OPTIONS', [])
    
    def post_to_platform(self, platform, username, password, content, content_type='text', media_url=None):
        """Post content to specified platform"""
        try:
            if platform == 'instagram':
                return self._post_to_instagram(username, password, content, content_type, media_url)
            elif platform == 'facebook':
                return self._post_to_facebook(username, password, content, content_type, media_url)
            elif platform == 'youtube':
                return self._post_to_youtube(username, password, content, content_type, media_url)
            else:
                return {'success': False, 'error': f'Platform {platform} not supported'}
                
        except Exception as e:
            logger.error(f"Auto posting error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _post_to_instagram(self, username, password, content, content_type, media_url):
        """Post to Instagram"""
        automator = InstagramAutomator(self.chrome_options)
        
        try:
            if not automator.login(username, password):
                return {'success': False, 'error': 'Instagram login failed'}
            
            if content_type == 'image' and media_url:
                result = automator.post_image(media_url, content)
            elif content_type == 'reel' and media_url:
                result = automator.post_reel(media_url, content)
            else:
                result = {'success': False, 'error': 'Invalid content type for Instagram'}
            
            return result
            
        finally:
            automator.close()
    
    def _post_to_facebook(self, username, password, content, content_type, media_url):
        """Post to Facebook"""
        automator = FacebookAutomator(self.chrome_options)
        
        try:
            if not automator.login(username, password):
                return {'success': False, 'error': 'Facebook login failed'}
            
            if content_type == 'text':
                result = automator.post_text(content)
            elif content_type == 'image' and media_url:
                result = automator.post_image(media_url, content)
            elif content_type == 'video' and media_url:
                result = automator.post_video(media_url, content)
            else:
                result = {'success': False, 'error': 'Invalid content type for Facebook'}
            
            return result
            
        finally:
            automator.close()
    
    def _post_to_youtube(self, username, password, content, content_type, media_url):
        """Post to YouTube"""
        # YouTube requires API-based posting for videos
        if content_type == 'video' and media_url:
            # This would integrate with YouTube Data API
            return {'success': False, 'error': 'YouTube API integration required'}
        else:
            return {'success': False, 'error': 'Only video uploads supported for YouTube'}
