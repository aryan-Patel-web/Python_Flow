"""
YouTube Automation Module - Complete YouTube Shorts & Video Automation
Multi-user support with OAuth, content generation, and scheduling
"""

import os
import asyncio
import logging
import json
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import httpx
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import io
import tempfile
import aiofiles

logger = logging.getLogger(__name__)

@dataclass
class YouTubeConfig:
    """Configuration for YouTube automation"""
    user_id: str
    channel_name: str = ""
    content_type: str = "shorts"  # shorts, videos, both
    upload_schedule: List[str] = field(default_factory=list)
    content_categories: List[str] = field(default_factory=list)
    auto_generate_titles: bool = True
    auto_generate_descriptions: bool = True
    auto_add_tags: bool = True
    privacy_status: str = "public"  # private, unlisted, public
    shorts_per_day: int = 3
    videos_per_week: int = 2

class YouTubeOAuthConnector:
    """YouTube OAuth and API connector"""
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube.force-ssl',
            'https://www.googleapis.com/auth/youtube.readonly'
        ]
        
    def generate_oauth_url(self, state: str = None) -> Dict[str, str]:
        """Generate OAuth URL for YouTube authorization"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes,
                state=state
            )
            flow.redirect_uri = self.redirect_uri
            
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            return {
                "success": True,
                "authorization_url": authorization_url,
                "state": state
            }
            
        except Exception as e:
            logger.error(f"YouTube OAuth URL generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes
            )
            flow.redirect_uri = self.redirect_uri
            
            # Exchange code for token
            flow.fetch_token(code=code)
            
            # Get user info
            credentials = flow.credentials
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Get channel information
            channels_response = youtube.channels().list(
                part='snippet,statistics',
                mine=True
            ).execute()
            
            if not channels_response.get('items'):
                return {
                    "success": False,
                    "error": "No YouTube channel found for this account"
                }
            
            channel_info = channels_response['items'][0]
            
            return {
                "success": True,
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "expires_in": 3600,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "channel_info": {
                    "channel_id": channel_info['id'],
                    "channel_name": channel_info['snippet']['title'],
                    "subscriber_count": channel_info['statistics'].get('subscriberCount', '0'),
                    "video_count": channel_info['statistics'].get('videoCount', '0'),
                    "view_count": channel_info['statistics'].get('viewCount', '0')
                }
            }
            
        except Exception as e:
            logger.error(f"YouTube token exchange failed: {e}")
            return {"success": False, "error": str(e)}
    
    def refresh_access_token(self, refresh_token: str, token_uri: str, client_id: str, client_secret: str) -> Dict[str, Any]:
        """Refresh YouTube access token"""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=refresh_token,
                token_uri=token_uri,
                client_id=client_id,
                client_secret=client_secret
            )
            
            credentials.refresh(Request())
            
            return {
                "success": True,
                "access_token": credentials.token,
                "expires_in": 3600
            }
            
        except Exception as e:
            logger.error(f"YouTube token refresh failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def upload_video(
        self,
        credentials_data: Dict,
        video_file_path: str,
        title: str,
        description: str,
        tags: List[str] = None,
        category_id: str = "22",  # People & Blogs
        privacy_status: str = "public"
    ) -> Dict[str, Any]:
        """Upload video to YouTube"""
        try:
            # Reconstruct credentials
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            # Refresh if needed
            if credentials.expired:
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags or [],
                    'categoryId': category_id
                },
                'status': {
                    'privacyStatus': privacy_status,
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Check if it's a YouTube Short (< 60 seconds)
            if self._is_youtube_short(video_file_path):
                body['snippet']['title'] = f"{title} #Shorts"
                logger.info("Detected YouTube Short format")
            
            # Upload video
            media = MediaFileUpload(
                video_file_path,
                chunksize=-1,
                resumable=True
            )
            
            insert_request = youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=media
            )
            
            response = None
            error = None
            retry = 0
            
            while response is None:
                try:
                    status, response = insert_request.next_chunk()
                    if response is not None:
                        if 'id' in response:
                            video_id = response['id']
                            video_url = f"https://www.youtube.com/watch?v={video_id}"
                            
                            logger.info(f"YouTube upload successful: {video_url}")
                            
                            return {
                                "success": True,
                                "video_id": video_id,
                                "video_url": video_url,
                                "title": title,
                                "privacy_status": privacy_status
                            }
                        else:
                            return {
                                "success": False,
                                "error": f"Upload failed: {response}"
                            }
                
                except HttpError as e:
                    if e.resp.status in [500, 502, 503, 504]:
                        retry += 1
                        if retry > 5:
                            return {
                                "success": False,
                                "error": f"Upload failed after retries: {e}"
                            }
                        await asyncio.sleep(2 ** retry)
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP error: {e}"
                        }
            
        except Exception as e:
            logger.error(f"YouTube upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_youtube_short(self, video_file_path: str) -> bool:
        """Check if video is eligible for YouTube Shorts (< 60 seconds)"""
        try:
            # This is a placeholder - in production, use ffprobe or similar
            # to get actual video duration
            import subprocess
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-print_format', 'json',
                '-show_format', video_file_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                duration = float(data['format']['duration'])
                return duration <= 60
                
        except Exception:
            pass
        
        # Fallback: assume it's a short if file size is small
        try:
            file_size = os.path.getsize(video_file_path)
            return file_size < 50 * 1024 * 1024  # Less than 50MB
        except:
            return False
    
    async def get_channel_analytics(self, credentials_data: Dict, days: int = 30) -> Dict[str, Any]:
        """Get YouTube channel analytics"""
        try:
            credentials = Credentials(
                token=credentials_data.get('access_token'),
                refresh_token=credentials_data.get('refresh_token'),
                token_uri=credentials_data.get('token_uri'),
                client_id=credentials_data.get('client_id'),
                client_secret=credentials_data.get('client_secret'),
                scopes=credentials_data.get('scopes')
            )
            
            if credentials.expired:
                credentials.refresh(Request())
            
            youtube = build('youtube', 'v3', credentials=credentials)
            
            # Get recent videos
            videos_response = youtube.search().list(
                part='snippet',
                forMine=True,
                type='video',
                order='date',
                maxResults=10
            ).execute()
            
            videos = []
            for item in videos_response.get('items', []):
                video_id = item['id']['videoId']
                
                # Get video statistics
                stats_response = youtube.videos().list(
                    part='statistics',
                    id=video_id
                ).execute()
                
                stats = stats_response['items'][0]['statistics'] if stats_response.get('items') else {}
                
                videos.append({
                    'video_id': video_id,
                    'title': item['snippet']['title'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': stats.get('viewCount', '0'),
                    'like_count': stats.get('likeCount', '0'),
                    'comment_count': stats.get('commentCount', '0')
                })
            
            # Get channel statistics
            channels_response = youtube.channels().list(
                part='statistics',
                mine=True
            ).execute()
            
            channel_stats = {}
            if channels_response.get('items'):
                channel_stats = channels_response['items'][0]['statistics']
            
            return {
                "success": True,
                "channel_statistics": channel_stats,
                "recent_videos": videos,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"YouTube analytics failed: {e}")
            return {"success": False, "error": str(e)}

class YouTubeAutomationScheduler:
    """YouTube content automation scheduler"""
    
    def __init__(self, youtube_connector, ai_service, database_manager, user_tokens):
        self.youtube_connector = youtube_connector
        self.ai_service = ai_service
        self.database = database_manager
        self.user_tokens = user_tokens
        self.active_configs = {}
        self.is_running = False
        self.upload_queue = {}
        
        logger.info("YouTube Automation Scheduler initialized")
    
    async def setup_youtube_automation(self, config: YouTubeConfig) -> Dict[str, Any]:
        """Setup YouTube automation for user"""
        try:
            user_id = config.user_id
            
            # Validate user has YouTube tokens
            if user_id not in self.user_tokens:
                return {
                    "success": False,
                    "error": "YouTube not connected",
                    "message": "Please connect your YouTube account first"
                }
            
            # Store configuration
            self.active_configs[user_id] = {
                "youtube_automation": {
                    "config": config,
                    "enabled": True,
                    "created_at": datetime.now(),
                    "total_uploads": 0,
                    "successful_uploads": 0,
                    "failed_uploads": 0
                }
            }
            
            # Save to database
            if hasattr(self.database, 'store_automation_config'):
                await self.database.store_automation_config(
                    user_id=user_id,
                    config_type='youtube_automation',
                    config_data=config.__dict__
                )
            
            logger.info(f"YouTube automation setup successful for user {user_id}")
            
            return {
                "success": True,
                "message": "YouTube automation enabled successfully!",
                "config": config.__dict__,
                "next_upload_time": self._get_next_upload_time(config.upload_schedule),
                "content_type": config.content_type,
                "scheduler_status": "Active"
            }
            
        except Exception as e:
            logger.error(f"YouTube automation setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_and_upload_content(
        self,
        user_id: str,
        content_type: str = "shorts",
        title: str = None,
        description: str = None,
        video_url: str = None
    ) -> Dict[str, Any]:
        """Generate and upload YouTube content"""
        try:
            if user_id not in self.user_tokens:
                return {
                    "success": False,
                    "error": "YouTube not connected"
                }
            
            credentials_data = self.user_tokens[user_id]
            
            # Generate content using AI if not provided
            if not title or not description:
                ai_content = await self._generate_video_content(user_id, content_type)
                if not ai_content.get("success"):
                    return ai_content
                
                title = title or ai_content.get("title")
                description = description or ai_content.get("description")
                tags = ai_content.get("tags", [])
            else:
                tags = []
            
            # For now, we'll handle video upload if video_url is provided
            if video_url:
                # Download video temporarily
                temp_video_path = await self._download_video_temporarily(video_url)
                
                if not temp_video_path:
                    return {
                        "success": False,
                        "error": "Failed to download video"
                    }
                
                # Upload to YouTube
                upload_result = await self.youtube_connector.upload_video(
                    credentials_data=credentials_data,
                    video_file_path=temp_video_path,
                    title=title,
                    description=description,
                    tags=tags,
                    privacy_status="public"
                )
                
                # Clean up temp file
                try:
                    os.unlink(temp_video_path)
                except:
                    pass
                
                # Update statistics
                if user_id in self.active_configs:
                    config = self.active_configs[user_id].get("youtube_automation", {})
                    if upload_result.get("success"):
                        config["successful_uploads"] = config.get("successful_uploads", 0) + 1
                    else:
                        config["failed_uploads"] = config.get("failed_uploads", 0) + 1
                    config["total_uploads"] = config.get("total_uploads", 0) + 1
                
                return upload_result
            else:
                return {
                    "success": False,
                    "error": "Video URL required for upload",
                    "message": "Please provide a video URL or file to upload"
                }
                
        except Exception as e:
            logger.error(f"YouTube content generation/upload failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_video_content(self, user_id: str, content_type: str) -> Dict[str, Any]:
        """Generate video title, description, and tags using AI"""
        try:
            if not hasattr(self.ai_service, 'generate_youtube_content'):
                # Fallback content generation
                if hasattr(self.ai_service, 'generate_reddit_domain_content'):
                    content_result = await self.ai_service.generate_reddit_domain_content(
                        domain="general",
                        business_type="YouTube Content",
                        target_audience="youtube_viewers",
                        content_style="engaging"
                    )
                    
                    if content_result.get("success"):
                        return {
                            "success": True,
                            "title": content_result.get("title", "AI Generated Video"),
                            "description": content_result.get("content", "AI generated description"),
                            "tags": ["AI", "generated", "content", content_type]
                        }
            
            # Use dedicated YouTube content generation if available
            content_result = await self.ai_service.generate_youtube_content(
                content_type=content_type,
                user_preferences=self._get_user_preferences(user_id)
            )
            
            return content_result
            
        except Exception as e:
            logger.error(f"AI content generation failed: {e}")
            return {
                "success": False,
                "error": f"AI content generation failed: {str(e)}"
            }
    
    async def _download_video_temporarily(self, video_url: str) -> Optional[str]:
        """Download video to temporary file for uploading"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(video_url)
                
                if response.status_code == 200:
                    # Create temporary file
                    temp_file = tempfile.NamedTemporaryFile(
                        delete=False,
                        suffix='.mp4'
                    )
                    
                    temp_file.write(response.content)
                    temp_file.close()
                    
                    return temp_file.name
                    
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            
        return None
    
    def _get_user_preferences(self, user_id: str) -> Dict:
        """Get user preferences for content generation"""
        config = self.active_configs.get(user_id, {}).get("youtube_automation", {}).get("config")
        if config:
            return {
                "content_categories": getattr(config, 'content_categories', []),
                "content_type": getattr(config, 'content_type', 'shorts')
            }
        return {}
    
    def _get_next_upload_time(self, upload_schedule: List[str]) -> str:
        """Get next scheduled upload time"""
        if not upload_schedule:
            return "No schedule set"
        
        try:
            current_time = datetime.now().time()
            
            for time_str in sorted(upload_schedule):
                upload_time = datetime.strptime(time_str, "%H:%M").time()
                if upload_time > current_time:
                    return f"Today at {time_str}"
            
            return f"Tomorrow at {sorted(upload_schedule)[0]}"
            
        except Exception:
            return "Schedule error"
    
    async def get_automation_status(self, user_id: str) -> Dict[str, Any]:
        """Get YouTube automation status for user"""
        try:
            user_config = self.active_configs.get(user_id, {})
            
            youtube_config = user_config.get("youtube_automation", {})
            config_obj = youtube_config.get("config")
            
            if config_obj and hasattr(config_obj, '__dict__'):
                config_data = config_obj.__dict__
            elif isinstance(config_obj, dict):
                config_data = config_obj
            else:
                config_data = None
            
            return {
                "success": True,
                "user_id": user_id,
                "youtube_connected": user_id in self.user_tokens,
                "youtube_automation": {
                    "enabled": "youtube_automation" in user_config,
                    "config": config_data,
                    "stats": {
                        "total_uploads": youtube_config.get("total_uploads", 0),
                        "successful_uploads": youtube_config.get("successful_uploads", 0),
                        "failed_uploads": youtube_config.get("failed_uploads", 0)
                    }
                },
                "scheduler_running": self.is_running,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"YouTube status check failed: {e}")
            return {"success": False, "error": str(e)}