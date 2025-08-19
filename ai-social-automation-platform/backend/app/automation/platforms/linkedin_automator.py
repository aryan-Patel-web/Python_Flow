"""
LinkedIn Automation Module
Handles LinkedIn posting and networking
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

logger = setup_logger('linkedin_automation')

class LinkedInAutomator:
    """Automate LinkedIn posting and networking"""
    
    def __init__(self, headless: bool = True):
        """Initialize LinkedIn automator"""
        self.headless = headless
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.user_info = {}
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with LinkedIn-specific options"""
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # LinkedIn-specific options
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            # Disable notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2
            }
            options.add_experimental_option("prefs", prefs)
            
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, 30)
            
            logger.info("LinkedIn WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup LinkedIn WebDriver: {str(e)}")
            raise AutomationError('linkedin', 'driver_setup', f"WebDriver setup failed: {str(e)}")
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login to LinkedIn
        
        Args:
            email: LinkedIn account email
            password: Account password
        
        Returns:
            Dict with login result
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Attempting LinkedIn login for {email}")
            
            # Navigate to LinkedIn login
            self.driver.get('https://www.linkedin.com/login')
            time.sleep(3)
            
            # Enter email
            email_input = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_input.send_keys(email)
            
            # Enter password
            password_input = self.driver.find_element(By.ID, "password")
            password_input.send_keys(password)
            
            # Click Sign in
            sign_in_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )
            sign_in_button.click()
            
            time.sleep(5)
            
            # Check if login was successful
            try:
                # Look for feed or profile elements
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CLASS_NAME, "global-nav")),
                        EC.presence_of_element_located((By.ID, "global-nav"))
                    )
                )
                
                self.is_logged_in = True
                
                # Get user info
                self.user_info = self._get_user_info()
                
                logger.info(f"LinkedIn login successful for {email}")
                
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user_info': self.user_info
                }
                
            except TimeoutException:
                # Check for verification or security challenge
                current_url = self.driver.current_url
                if "challenge" in current_url or "verification" in current_url:
                    return {
                        'success': False,
                        'error': 'Account verification required',
                        'requires_verification': True
                    }
                elif "checkpoint" in current_url:
                    return {
                        'success': False,
                        'error': 'Security checkpoint required'
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Login failed - invalid credentials or account issue'
                    }
        
        except Exception as e:
            error_msg = f"LinkedIn login failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            # Navigate to profile to get user info
            self.driver.get('https://www.linkedin.com/me/')
            time.sleep(5)
            
            user_data = {}
            
            try:
                # Get name
                name_element = self.driver.find_element(
                    By.XPATH, "//h1[contains(@class, 'text-heading-xlarge')]"
                )
                user_data['name'] = name_element.text
            except:
                user_data['name'] = "Unknown User"
            
            try:
                # Get headline
                headline_element = self.driver.find_element(
                    By.XPATH, "//div[contains(@class, 'text-body-medium')]"
                )
                user_data['headline'] = headline_element.text
            except:
                user_data['headline'] = ""
            
            try:
                # Get connection count
                connections_element = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'connection')]"
                )
                user_data['connections'] = connections_element.text
            except:
                user_data['connections'] = "0"
            
            # Get profile URL
            user_data['profile_url'] = self.driver.current_url
            
            return user_data
        
        except Exception as e:
            logger.error(f"Failed to get LinkedIn user info: {str(e)}")
            return {}
    
    def create_post(self, text: str, media_path: str = None, 
                   article_url: str = None) -> Dict[str, Any]:
        """
        Create a LinkedIn post
        
        Args:
            text: Post text content
            media_path: Path to image/video file
            article_url: URL to share (for link posts)
        
        Returns:
            Dict with posting result
        """
        try:
            if not self.is_logged_in:
                raise AutomationError('linkedin', 'post', 'Not logged in')
            
            if len(text) > 3000:
                raise AutomationError('linkedin', 'post', f'Post too long: {len(text)} characters (max 3000)')
            
            logger.info(f"Creating LinkedIn post: {text[:50]}...")
            
            # Navigate to home feed
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(3)
            
            # Click "Start a post" button
            start_post_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-box-feed-entry__trigger')]"))
            )
            start_post_button.click()
            
            time.sleep(3)
            
            # Find and click in the text area
            text_area = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
            )
            text_area.click()
            text_area.send_keys(text)
            
            # Upload media if provided
            if media_path and os.path.exists(media_path):
                try:
                    # Click media upload button
                    media_button = self.driver.find_element(
                        By.XPATH, "//input[@type='file']"
                    )
                    media_button.send_keys(media_path)
                    time.sleep(5)  # Wait for upload
                except Exception as e:
                    logger.warning(f"Failed to upload media {media_path}: {str(e)}")
            
            # Add article URL if provided
            if article_url:
                try:
                    # Paste URL and let LinkedIn auto-preview
                    text_area.send_keys(f"\n\n{article_url}")
                    time.sleep(5)  # Wait for URL preview
                except Exception as e:
                    logger.warning(f"Failed to add article URL: {str(e)}")
            
            time.sleep(2)
            
            # Click Post button
            post_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-actions__primary-action')]"))
            )
            post_button.click()
            
            time.sleep(5)
            
            # Verify post was created
            try:
                # Check if we're back to feed
                self.wait.until(
                    EC.url_contains('feed')
                )
                
                result = {
                    'success': True,
                    'message': 'LinkedIn post created successfully',
                    'text': text,
                    'has_media': bool(media_path),
                    'has_link': bool(article_url),
                    'posted_at': time.time()
                }
                
                logger.info("LinkedIn post successful")
                return result
                
            except TimeoutException:
                return {
                    'success': False,
                    'error': 'Post creation failed - timeout waiting for confirmation'
                }
        
        except Exception as e:
            error_msg = f"LinkedIn posting failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def send_connection_request(self, profile_url: str, message: str = None) -> Dict[str, Any]:
        """Send a connection request"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to profile
            self.driver.get(profile_url)
            time.sleep(5)
            
            # Click Connect button
            connect_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Connect')]"))
            )
            connect_button.click()
            
            time.sleep(2)
            
            # Add personal message if provided
            if message:
                try:
                    # Click "Add a note"
                    add_note_button = self.driver.find_element(
                        By.XPATH, "//button[contains(text(), 'Add a note')]"
                    )
                    add_note_button.click()
                    
                    time.sleep(2)
                    
                    # Enter message
                    message_input = self.driver.find_element(
                        By.XPATH, "//textarea"
                    )
                    message_input.send_keys(message)
                    
                except Exception as e:
                    logger.warning(f"Failed to add note to connection request: {str(e)}")
            
            # Send invitation
            send_button = self.driver.find_element(
                By.XPATH, "//button[contains(@aria-label, 'Send')]"
            )
            send_button.click()
            
            time.sleep(3)
            
            return {
                'success': True,
                'message': 'Connection request sent successfully',
                'profile_url': profile_url,
                'note': message
            }
        
        except Exception as e:
            error_msg = f"Failed to send connection request: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def search_people(self, keywords: str, location: str = None, 
                     company: str = None, limit: int = 10) -> Dict[str, Any]:
        """Search for people on LinkedIn"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Build search URL
            search_url = f"https://www.linkedin.com/search/results/people/?keywords={keywords}"
            
            if location:
                search_url += f"&origin=GLOBAL_SEARCH_HEADER&geoUrn=%5B%22{location}%22%5D"
            
            if company:
                search_url += f"&currentCompany=%5B%22{company}%22%5D"
            
            self.driver.get(search_url)
            time.sleep(5)
            
            people = []
            
            # Get search result items
            result_items = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'search-result__info')]"
            )
            
            for i, item in enumerate(result_items[:limit]):
                try:
                    # Get name
                    name_element = item.find_element(
                        By.XPATH, ".//span[@dir='ltr']//span[1]"
                    )
                    name = name_element.text
                    
                    # Get profile link
                    link_element = item.find_element(
                        By.XPATH, ".//a[contains(@href, '/in/')]"
                    )
                    profile_url = link_element.get_attribute('href')
                    
                    # Get headline
                    try:
                        headline_element = item.find_element(
                            By.XPATH, ".//p[contains(@class, 'subline-level-1')]"
                        )
                        headline = headline_element.text
                    except:
                        headline = ""
                    
                    # Get location
                    try:
                        location_element = item.find_element(
                            By.XPATH, ".//p[contains(@class, 'subline-level-2')]"
                        )
                        location = location_element.text
                    except:
                        location = ""
                    
                    people.append({
                        'name': name,
                        'headline': headline,
                        'location': location,
                        'profile_url': profile_url
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse search result {i}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'people': people,
                'search_query': keywords,
                'count': len(people)
            }
        
        except Exception as e:
            error_msg = f"Failed to search LinkedIn people: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_feed_posts(self, count: int = 10) -> Dict[str, Any]:
        """Get recent posts from LinkedIn feed"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to feed
            self.driver.get('https://www.linkedin.com/feed/')
            time.sleep(5)
            
            posts = []
            
            # Scroll to load more posts
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Get post elements
            post_elements = self.driver.find_elements(
                By.XPATH, "//div[contains(@class, 'feed-shared-update-v2')]"
            )
            
            for i, post_element in enumerate(post_elements[:count]):
                try:
                    # Get author name
                    try:
                        author_element = post_element.find_element(
                            By.XPATH, ".//span[contains(@class, 'feed-shared-actor__name')]"
                        )
                        author = author_element.text
                    except:
                        author = "Unknown"
                    
                    # Get post text
                    try:
                        text_element = post_element.find_element(
                            By.XPATH, ".//div[contains(@class, 'feed-shared-text')]"
                        )
                        text = text_element.text
                    except:
                        text = ""
                    
                    # Get engagement metrics
                    try:
                        likes_element = post_element.find_element(
                            By.XPATH, ".//button[contains(@aria-label, 'reaction')]"
                        )
                        likes = likes_element.get_attribute('aria-label')
                    except:
                        likes = "0"
                    
                    posts.append({
                        'author': author,
                        'text': text,
                        'likes': likes,
                        'comments': comments
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse LinkedIn post {i}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'posts': posts,
                'count': len(posts)
            }
        
        except Exception as e:
            error_msg = f"Failed to get LinkedIn feed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def like_post(self, post_url: str) -> Dict[str, Any]:
        """Like a LinkedIn post"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to post
            self.driver.get(post_url)
            time.sleep(3)
            
            # Click like button
            like_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'React Like')]"))
            )
            like_button.click()
            
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'Post liked successfully',
                'post_url': post_url
            }
        
        except Exception as e:
            error_msg = f"Failed to like LinkedIn post: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def comment_on_post(self, post_url: str, comment: str) -> Dict[str, Any]:
        """Comment on a LinkedIn post"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to post
            self.driver.get(post_url)
            time.sleep(3)
            
            # Click comment button to expand comment section
            comment_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Comment')]"))
            )
            comment_button.click()
            
            time.sleep(2)
            
            # Find comment input and enter text
            comment_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
            )
            comment_input.click()
            comment_input.send_keys(comment)
            
            # Submit comment
            submit_button = self.driver.find_element(
                By.XPATH, "//button[contains(@class, 'comments-comment-box__submit-button')]"
            )
            submit_button.click()
            
            time.sleep(3)
            
            return {
                'success': True,
                'message': 'Comment posted successfully',
                'post_url': post_url,
                'comment': comment
            }
        
        except Exception as e:
            error_msg = f"Failed to comment on LinkedIn post: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_profile_analytics(self) -> Dict[str, Any]:
        """Get basic profile analytics"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to profile
            self.driver.get('https://www.linkedin.com/me/')
            time.sleep(5)
            
            analytics_data = {}
            
            # Get connection count
            try:
                connections_element = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'connection')]"
                )
                analytics_data['connections'] = connections_element.text
            except:
                analytics_data['connections'] = "0"
            
            # Get profile views (if available)
            try:
                self.driver.get('https://www.linkedin.com/me/profile-views/')
                time.sleep(3)
                
                views_element = self.driver.find_element(
                    By.XPATH, "//strong[contains(@class, 'profile-views')]"
                )
                analytics_data['profile_views'] = views_element.text
            except:
                analytics_data['profile_views'] = "N/A"
            
            # Get post impressions (if available)
            try:
                impressions_element = self.driver.find_element(
                    By.XPATH, "//span[contains(text(), 'post impression')]"
                )
                analytics_data['post_impressions'] = impressions_element.text
            except:
                analytics_data['post_impressions'] = "N/A"
            
            return {
                'success': True,
                'analytics': analytics_data,
                'retrieved_at': time.time()
            }
        
        except Exception as e:
            error_msg = f"Failed to get LinkedIn analytics: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def test_credentials(self, email: str, password: str) -> Dict[str, Any]:
        """Test LinkedIn credentials without full login"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Attempt login
            login_result = self.login(email, password)
            
            if login_result['success']:
                # Get additional account info
                account_info = {
                    'email': email,
                    'user_info': login_result.get('user_info', {}),
                    'verified_at': time.time()
                }
                
                return {
                    'success': True,
                    'account_info': account_info
                }
            else:
                return login_result
        
        except Exception as e:
            error_msg = f"LinkedIn credential test failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def logout(self):
        """Logout from LinkedIn"""
        try:
            if self.is_logged_in:
                # Click on profile menu
                profile_menu = self.driver.find_element(
                    By.XPATH, "//button[contains(@class, 'global-nav__me')]"
                )
                profile_menu.click()
                
                time.sleep(2)
                
                # Click Sign out
                signout_btn = self.driver.find_element(
                    By.XPATH, "//a[contains(@href, '/logout')]"
                )
                signout_btn.click()
                
                time.sleep(3)
                
                self.is_logged_in = False
                logger.info("LinkedIn logout successful")
        
        except Exception as e:
            logger.error(f"LinkedIn logout failed: {str(e)}")
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("LinkedIn WebDriver closed")
        except Exception as e:
            logger.error(f"Failed to close LinkedIn WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()
        self.close()

# Utility functions for LinkedIn automation
def post_to_linkedin_with_retry(email: str, password: str, text: str, 
                               media_path: str = None, max_retries: int = 3) -> Dict[str, Any]:
    """Post to LinkedIn with retry mechanism"""
    
    for attempt in range(max_retries):
        try:
            with LinkedInAutomator() as automator:
                # Login
                login_result = automator.login(email, password)
                if not login_result['success']:
                    return login_result
                
                # Create post
                post_result = automator.create_post(
                    text=text,
                    media_path=media_path
                )
                
                if post_result['success']:
                    return post_result
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"LinkedIn post attempt {attempt + 1} failed, retrying...")
                        time.sleep(30)
                        continue
                    else:
                        return post_result
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"LinkedIn post attempt {attempt + 1} failed with exception: {str(e)}")
                time.sleep(30)
                continue
            else:
                return {
                    'success': False,
                    'error': f"All {max_retries} LinkedIn post attempts failed: {str(e)}"
                }
    
    return {
        'success': False,
        'error': f"LinkedIn post failed after {max_retries} attempts"
    }

def bulk_connect_linkedin(email: str, password: str, profile_urls: List[str], 
                         personal_message: str = None, delay_between_requests: int = 60) -> Dict[str, Any]:
    """Send connection requests to multiple profiles"""
    
    results = []
    
    try:
        with LinkedInAutomator() as automator:
            # Login
            login_result = automator.login(email, password)
            if not login_result['success']:
                return login_result
            
            for profile_url in profile_urls:
                try:
                    connect_result = automator.send_connection_request(
                        profile_url=profile_url,
                        message=personal_message
                    )
                    
                    results.append({
                        'profile_url': profile_url,
                        'success': connect_result['success'],
                        'message': connect_result.get('message', connect_result.get('error'))
                    })
                    
                    # Delay between requests to avoid rate limiting
                    if profile_url != profile_urls[-1]:
                        time.sleep(delay_between_requests)
                
                except Exception as e:
                    results.append({
                        'profile_url': profile_url,
                        'success': False,
                        'message': str(e)
                    })
            
            successful_requests = sum(1 for r in results if r['success'])
            
            return {
                'success': True,
                'total_profiles': len(profile_urls),
                'successful_requests': successful_requests,
                'results': results
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Bulk connect operation failed: {str(e)}",
            'partial_results': results
        }

def linkedin_content_engagement(email: str, password: str, target_posts: List[str], 
                              engagement_type: str = 'like') -> Dict[str, Any]:
    """Engage with multiple LinkedIn posts (like/comment)"""
    
    if engagement_type not in ['like', 'comment']:
        return {
            'success': False,
            'error': 'Invalid engagement type. Must be "like" or "comment"'
        }
    
    results = []
    
    try:
        with LinkedInAutomator() as automator:
            # Login
            login_result = automator.login(email, password)
            if not login_result['success']:
                return login_result
            
            for post_url in target_posts:
                try:
                    if engagement_type == 'like':
                        result = automator.like_post(post_url)
                    else:  # comment
                        # For comment engagement, you'd need to provide comment text
                        result = {'success': False, 'error': 'Comment text not provided'}
                    
                    results.append({
                        'post_url': post_url,
                        'engagement_type': engagement_type,
                        'success': result['success'],
                        'message': result.get('message', result.get('error'))
                    })
                    
                    # Small delay between engagements
                    time.sleep(10)
                
                except Exception as e:
                    results.append({
                        'post_url': post_url,
                        'engagement_type': engagement_type,
                        'success': False,
                        'message': str(e)
                    })
            
            successful_engagements = sum(1 for r in results if r['success'])
            
            return {
                'success': True,
                'total_posts': len(target_posts),
                'successful_engagements': successful_engagements,
                'engagement_type': engagement_type,
                'results': results
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"LinkedIn engagement operation failed: {str(e)}",
            'partial_results': results
        }