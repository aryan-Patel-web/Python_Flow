"""
YouTube Feature Extraction - Main Logic
Handles thumbnail generation workflow and API integration
"""

import logging
from typing import Dict
from YT_ai_services import YouTubeAIService

logger = logging.getLogger(__name__)

class YouTubeFeatureExtractor:
    """Main feature extractor for YouTube automation"""
    
    def __init__(self, ai_service: YouTubeAIService):
        self.ai_service = ai_service
        logger.info("YouTube Feature Extractor initialized")
    
    async def generate_thumbnails_for_video(
        self,
        video_url: str,
        video_title: str,
        style: str = "indian"
    ) -> Dict:
        """
        Public API: Generate thumbnails for video upload
        """
        try:
            result = await self.ai_service.generate_thumbnail_options(
                video_url=video_url,
                video_title=video_title,
                style=style
            )
            
            if result.get("success"):
                logger.info(f"Thumbnails generated successfully for: {video_title}")
            else:
                logger.error(f"Thumbnail generation failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {"success": False, "error": str(e)}