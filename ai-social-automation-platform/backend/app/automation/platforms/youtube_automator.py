"""
YouTube Automation Module
Handles YouTube video uploads and channel management
"""
import os
import time
import logging
from typing import Dict, Any, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from app.utils.logger import setup_logger, log_automation_event
from app.utils.error_handlers import AutomationError

logger = setup_logger('youtube_automation')

class YouTubeAutomator:
    """Automate YouTube video uploads and management"""
    
    def __init__(self, headless: bool = True):
        """Initialize YouTube automator"""
        self.headless = headless
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.channel_info = {}
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with YouTube-specific options"""
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # YouTube-specific options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Disable notifications and location requests
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "profile.default_content_setting_values.geolocation": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("YouTube WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup YouTube WebDriver: {str(e)}")
            raise AutomationError('youtube', 'driver_setup', f"WebDriver setup failed: {str(e)}")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login to YouTube
        
        Args:
            email: YouTube/Google account email
            password: Account password
        
        Returns:
            Dict with login result
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Attempting YouTube login for {email}")
            
            # Navigate to YouTube
            self.driver.get('https://www.youtube.com')
            time.sleep(3)
            
            # Click Sign In button
            sign_in_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[@aria-label='Sign in']"))
            )
            sign_in_button.click()
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "identifierId"))
            )
            email_input.send_keys(email)
            
            # Click Next
            next_button = self.driver.find_element(By.ID, "identifierNext")
            next_button.click()
            
            time.sleep(3)
            
            # Enter password
            password_input = self.wait.until(
                EC.element_to_be_clickable((By.NAME, "password"))
            )
            password_input.send_keys(password)
            
            # Click Next
            password_next = self.driver.find_element(By.ID, "passwordNext")
            password_next.click()
            
            time.sleep(5)
            
            # Check if login was successful
            try:
                # Look for avatar or channel button
                self.wait.until(
                    EC.presence_of_element_located((By.ID, "avatar-btn"))
                )
                
                self.is_logged_in = True
                
                # Get channel info
                self.channel_info = self._get_channel_info()
                
                logger.info(f"YouTube login successful for {email}")
                
                return {
                    'success': True,
                    'message': 'Login successful',
                    'channel_info': self.channel_info
                }
                
            except TimeoutException:
                # Check for 2FA or verification required
                if "verification" in self.driver.current_url.lower():
                    return {
                        'success': False,
                        'error': 'Two-factor authentication required',
                        'requires_2fa': True
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Login failed - invalid credentials or account issue'
                    }
        
        except Exception as e:
            error_msg = f"YouTube login failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _get_channel_info(self) -> Dict[str, Any]:
        """Get current channel information"""
        try:
            # Click on avatar to get channel info
            avatar_btn = self.driver.find_element(By.ID, "avatar-btn")
            avatar_btn.click()
            
            time.sleep(2)
            
            # Get channel name
            try:
                channel_name = self.driver.find_element(
                    By.XPATH, "//yt-formatted-string[@id='text' and @slot='title']"
                ).text
            except:
                channel_name = "Unknown Channel"
            
            # Get subscriber count (if available)
            try:
                subscriber_count = self.driver.find_element(
                    By.XPATH, "//yt-formatted-string[contains(@class, 'subscriber-count')]"
                ).text
            except:
                subscriber_count = "Unknown"
            
            # Close dropdown
            self.driver.find_element(By.TAG_NAME, "body").click()
            
            return {
                'channel_name': channel_name,
                'subscriber_count': subscriber_count,
                'url': self.driver.current_url
            }
        
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return {}
    
    def upload_video(self, video_path: str, title: str, description: str = "", 
                    tags: List[str] = None, thumbnail_path: str = None,
                    privacy: str = 'public', schedule_time: str = None) -> Dict[str, Any]:
        """
        Upload video to YouTube
        
        Args:
            video_path: Path to video file
            title: Video title
            description: Video description
            tags: List of tags
            thumbnail_path: Path to thumbnail image
            privacy: Privacy setting (public, unlisted, private)
            schedule_time: Schedule publish time (ISO format)
        
        Returns:
            Dict with upload result
        """
        try:
            if not self.is_logged_in:
                raise AutomationError('youtube', 'upload', 'Not logged in')
            
            if not os.path.exists(video_path):
                raise AutomationError('youtube', 'upload', f'Video file not found: {video_path}')
            
            logger.info(f"Starting YouTube video upload: {title}")
            
            # Navigate to YouTube Studio
            self.driver.get('https://studio.youtube.com')
            time.sleep(5)
            
            # Click Create button
            create_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "create-icon"))
            )
            create_button.click()
            
            # Click Upload videos
            upload_option = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//tp-yt-paper-item[@test-id='upload-beta']"))
            )
            upload_option.click()
            
            time.sleep(3)
            
            # Upload video file
            file_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(video_path)
            
            time.sleep(5)
            
            # Wait for upload to start
            self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//ytcp-video-upload-progress"))
            )
            
            # Fill in video details
            # Title
            title_input = self.wait.until(
                EC.element_to_be_clickable((By.ID, "textbox"))
            )
            title_input.clear()
            title_input.send_keys(title)
            
            # Description
            if description:
                description_input = self.driver.find_element(
                    By.XPATH, "//div[@id='textbox' and @aria-label='Tell viewers about your video']"
                )
                description_input.clear()
                description_input.send_keys(description)
            
            # Thumbnail upload
            if thumbnail_path and os.path.exists(thumbnail_path):
                try:
                    thumbnail_input = self.driver.find_element(
                        By.XPATH, "//input[@accept='image/jpeg,image/png']"
                    )
                    thumbnail_input.send_keys(thumbnail_path)
                    time.sleep(3)
                except Exception as e:
                    logger.warning(f"Failed to upload thumbnail: {str(e)}")
            
            # Click "No, it's not made for kids" (assuming not kids content)
            try:
                not_for_kids = self.wait.until(
                    EC.element_to_be_clickable((By.NAME, "VIDEO_MADE_FOR_KIDS_NOT_MFK"))
                )
                not_for_kids.click()
            except:
                pass
            
            # Click Next
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "next-button"))
            )
            next_button.click()
            
            time.sleep(3)
            
            # Skip video elements page
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "next-button"))
            )
            next_button.click()
            
            time.sleep(3)
            
            # Skip checks page
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "next-button"))
            )
            next_button.click()
            
            time.sleep(3)
            
            # Set privacy
            privacy_options = {
                'private': 'PRIVATE',
                'unlisted': 'UNLISTED',
                'public': 'PUBLIC'
            }
            
            privacy_setting = privacy_options.get(privacy.lower(), 'PUBLIC')
            
            privacy_button = self.wait.until(
                EC.element_to_be_clickable((By.NAME, privacy_setting))
            )
            privacy_button.click()
            
            # Schedule if needed
            if schedule_time:
                try:
                    schedule_radio = self.driver.find_element(By.NAME, "SCHEDULE")
                    schedule_radio.click()
                    
                    # Set schedule time (implementation depends on date picker)
                    # This is complex and would require more detailed implementation
                    logger.info(f"Scheduling feature requested but not fully implemented")
                except Exception as e:
                    logger.warning(f"Failed to schedule video: {str(e)}")
            
            # Publish
            publish_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "done-button"))
            )
            publish_button.click()
            
            # Wait for upload completion
            time.sleep(10)
            
            # Try to get video URL
            video_url = None
            try:
                video_link = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/watch?v=')]"))
                )
                video_url = video_link.get_attribute('href')
            except:
                logger.warning("Could not retrieve video URL")
            
            result = {
                'success': True,
                'message': 'Video uploaded successfully',
                'video_url': video_url,
                'title': title,
                'privacy': privacy,
                'upload_time': time.time()
            }
            
            logger.info(f"YouTube video upload completed: {title}")
            
            return result
        
        except Exception as e:
            error_msg = f"YouTube video upload failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_channel_analytics(self) -> Dict[str, Any]:
        """Get basic channel analytics"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to YouTube Studio Analytics
            self.driver.get('https://studio.youtube.com/channel/UC/analytics')
            time.sleep(5)
            
            analytics_data = {}
            
            # Try to get subscriber count
            try:
                subscribers = self.driver.find_element(
                    By.XPATH, "//div[contains(@class, 'metric')]//span[contains(text(), 'subscribers')]/..//span[@class='metric-value']"
                ).text
                analytics_data['subscribers'] = subscribers
            except:
                pass
            
            # Try to get view count
            try:
                views = self.driver.find_element(
                    By.XPATH, "//div[contains(@class, 'metric')]//span[contains(text(), 'views')]/..//span[@class='metric-value']"
                ).text
                analytics_data['views'] = views
            except:
                pass
            
            # Try to get watch time
            try:
                watch_time = self.driver.find_element(
                    By.XPATH, "//div[contains(@class, 'metric')]//span[contains(text(), 'watch time')]/..//span[@class='metric-value']"
                ).text
                analytics_data['watch_time'] = watch_time
            except:
                pass
            
            return {
                'success': True,
                'analytics': analytics_data,
                'retrieved_at': time.time()
            }
        
        except Exception as e:
            error_msg = f"Failed to get YouTube analytics: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_video_list(self, limit: int = 10) -> Dict[str, Any]:
        """Get list of recent videos"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to YouTube Studio Content page
            self.driver.get('https://studio.youtube.com/channel/UC/videos')
            time.sleep(5)
            
            videos = []
            
            # Get video rows
            video_rows = self.driver.find_elements(
                By.XPATH, "//div[@id='video-list']//ytcp-video-row"
            )
            
            for i, row in enumerate(video_rows[:limit]):
                try:
                    # Get video title
                    title_element = row.find_element(
                        By.XPATH, ".//a[@id='video-title']"
                    )
                    title = title_element.text
                    url = title_element.get_attribute('href')
                    
                    # Get video status
                    try:
                        status = row.find_element(
                            By.XPATH, ".//span[contains(@class, 'visibility')]"
                        ).text
                    except:
                        status = 'Unknown'
                    
                    # Get view count
                    try:
                        views = row.find_element(
                            By.XPATH, ".//span[contains(@class, 'views')]"
                        ).text
                    except:
                        views = '0'
                    
                    videos.append({
                        'title': title,
                        'url': url,
                        'status': status,
                        'views': views
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse video row {i}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'videos': videos,
                'total_found': len(videos)
            }
        
        except Exception as e:
            error_msg = f"Failed to get YouTube video list: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def test_credentials(self, email: str, password: str) -> Dict[str, Any]:
        """Test YouTube credentials without full login"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Attempt login
            login_result = self.login(email, password)
            
            if login_result['success']:
                # Get additional account info
                account_info = {
                    'email': email,
                    'channel_info': login_result.get('channel_info', {}),
                    'verified_at': time.time()
                }
                
                return {
                    'success': True,
                    'account_info': account_info
                }
            else:
                return login_result
        
        except Exception as e:
            error_msg = f"YouTube credential test failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def logout(self):
        """Logout from YouTube"""
        try:
            if self.is_logged_in:
                # Click avatar
                avatar_btn = self.driver.find_element(By.ID, "avatar-btn")
                avatar_btn.click()
                
                time.sleep(2)
                
                # Click Sign out
                signout_btn = self.driver.find_element(
                    By.XPATH, "//yt-formatted-string[text()='Sign out']"
                )
                signout_btn.click()
                
                time.sleep(3)
                
                self.is_logged_in = False
                logger.info("YouTube logout successful")
        
        except Exception as e:
            logger.error(f"YouTube logout failed: {str(e)}")
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("YouTube WebDriver closed")
        except Exception as e:
            logger.error(f"Failed to close YouTube WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()
        self.close()

# Utility functions for YouTube automation
def upload_video_with_retry(email: str, password: str, video_path: str, 
                          title: str, description: str = "", 
                          max_retries: int = 3) -> Dict[str, Any]:
    """Upload video with retry mechanism"""
    
    for attempt in range(max_retries):
        try:
            with YouTubeAutomator() as automator:
                # Login
                login_result = automator.login(email, password)
                if not login_result['success']:
                    return login_result
                
                # Upload video
                upload_result = automator.upload_video(
                    video_path=video_path,
                    title=title,
                    description=description
                )
                
                if upload_result['success']:
                    return upload_result
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Upload attempt {attempt + 1} failed, retrying...")
                        time.sleep(30)  # Wait before retry
                        continue
                    else:
                        return upload_result
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Upload attempt {attempt + 1} failed with exception: {str(e)}")
                time.sleep(30)
                continue
            else:
                return {
                    'success': False,
                    'error': f"All {max_retries} upload attempts failed: {str(e)}"
                }
    
    return {
        'success': False,
        'error': f"Upload failed after {max_retries} attempts"
    }