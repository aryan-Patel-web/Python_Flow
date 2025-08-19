"""
Twitter Automation Module
Handles Twitter posting and engagement
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

logger = setup_logger('twitter_automation')

class TwitterAutomator:
    """Automate Twitter posting and engagement"""
    
    def __init__(self, headless: bool = True):
        """Initialize Twitter automator"""
        self.headless = headless
        self.driver = None
        self.wait = None
        self.is_logged_in = False
        self.user_info = {}
    
    def _setup_driver(self):
        """Setup Chrome WebDriver with Twitter-specific options"""
        try:
            options = webdriver.ChromeOptions()
            
            if self.headless:
                options.add_argument('--headless')
            
            # Twitter-specific options
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
            
            logger.info("Twitter WebDriver setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup Twitter WebDriver: {str(e)}")
            raise AutomationError('twitter', 'driver_setup', f"WebDriver setup failed: {str(e)}")
    
    def login(self, username: str, password: str) -> Dict[str, Any]:
        """
        Login to Twitter
        
        Args:
            username: Twitter username or email
            password: Account password
        
        Returns:
            Dict with login result
        """
        try:
            if not self.driver:
                self._setup_driver()
            
            logger.info(f"Attempting Twitter login for {username}")
            
            # Navigate to Twitter login
            self.driver.get('https://twitter.com/i/flow/login')
            time.sleep(3)
            
            # Enter username/email
            username_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username']"))
            )
            username_input.send_keys(username)
            
            # Click Next
            next_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Next']"))
            )
            next_button.click()
            
            time.sleep(3)
            
            # Check if phone/username verification is required
            try:
                verification_input = self.driver.find_element(
                    By.XPATH, "//input[@data-testid='ocfEnterTextTextInput']"
                )
                # If verification required, enter username again
                verification_input.send_keys(username.split('@')[0] if '@' in username else username)
                
                verify_next = self.driver.find_element(
                    By.XPATH, "//span[text()='Next']"
                )
                verify_next.click()
                time.sleep(3)
            except:
                pass  # No verification required
            
            # Enter password
            password_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@name='password']"))
            )
            password_input.send_keys(password)
            
            # Click Log in
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
            )
            login_button.click()
            
            time.sleep(5)
            
            # Check if login was successful
            try:
                # Look for home timeline or profile
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//nav[@aria-label='Primary navigation']")),
                        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='primaryColumn']"))
                    )
                )
                
                self.is_logged_in = True
                
                # Get user info
                self.user_info = self._get_user_info()
                
                logger.info(f"Twitter login successful for {username}")
                
                return {
                    'success': True,
                    'message': 'Login successful',
                    'user_info': self.user_info
                }
                
            except TimeoutException:
                # Check for 2FA or suspended account
                current_url = self.driver.current_url
                if "account_access" in current_url or "suspended" in current_url:
                    return {
                        'success': False,
                        'error': 'Account suspended or restricted'
                    }
                elif "challenge" in current_url:
                    return {
                        'success': False,
                        'error': 'Account verification required',
                        'requires_verification': True
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Login failed - invalid credentials'
                    }
        
        except Exception as e:
            error_msg = f"Twitter login failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def _get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        try:
            # Navigate to profile to get user info
            profile_links = self.driver.find_elements(
                By.XPATH, "//a[contains(@href, '/') and @role='link']"
            )
            
            username = "unknown"
            display_name = "Unknown User"
            
            try:
                # Try to get username from URL or profile link
                for link in profile_links:
                    href = link.get_attribute('href')
                    if href and href.count('/') == 3 and href.endswith(tuple('abcdefghijklmnopqrstuvwxyz')):
                        username = href.split('/')[-1]
                        break
            except:
                pass
            
            try:
                # Try to get display name
                display_name_element = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='UserName']//span"
                )
                display_name = display_name_element.text
            except:
                pass
            
            return {
                'username': username,
                'display_name': display_name,
                'url': f"https://twitter.com/{username}"
            }
        
        except Exception as e:
            logger.error(f"Failed to get Twitter user info: {str(e)}")
            return {}
    
    def post_tweet(self, text: str, media_paths: List[str] = None, 
                   reply_to: str = None) -> Dict[str, Any]:
        """
        Post a tweet
        
        Args:
            text: Tweet text (max 280 characters)
            media_paths: List of image/video file paths
            reply_to: Tweet ID to reply to
        
        Returns:
            Dict with posting result
        """
        try:
            if not self.is_logged_in:
                raise AutomationError('twitter', 'post', 'Not logged in')
            
            if len(text) > 280:
                raise AutomationError('twitter', 'post', f'Tweet too long: {len(text)} characters (max 280)')
            
            logger.info(f"Posting tweet: {text[:50]}...")
            
            # Navigate to home if not already there
            if 'home' not in self.driver.current_url:
                self.driver.get('https://twitter.com/home')
                time.sleep(3)
            
            # If replying to a tweet
            if reply_to:
                # Navigate to the tweet to reply to
                tweet_url = f"https://twitter.com/i/web/status/{reply_to}"
                self.driver.get(tweet_url)
                time.sleep(3)
                
                # Click reply button
                reply_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='reply']"))
                )
                reply_button.click()
                time.sleep(2)
            
            # Find tweet compose box
            compose_tweet = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
            )
            compose_tweet.click()
            
            # Clear any existing text and type new tweet
            compose_tweet.clear()
            compose_tweet.send_keys(text)
            
            # Upload media if provided
            if media_paths:
                for media_path in media_paths[:4]:  # Twitter allows max 4 images
                    if os.path.exists(media_path):
                        try:
                            # Click media upload button
                            media_button = self.driver.find_element(
                                By.XPATH, "//input[@data-testid='fileInput']"
                            )
                            media_button.send_keys(media_path)
                            time.sleep(3)  # Wait for upload
                        except Exception as e:
                            logger.warning(f"Failed to upload media {media_path}: {str(e)}")
            
            time.sleep(2)
            
            # Click Tweet button
            tweet_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButtonInline']"))
            )
            tweet_button.click()
            
            time.sleep(5)
            
            # Verify tweet was posted (look for success indication)
            try:
                # Check if we're back to timeline or if tweet appears
                self.wait.until(
                    EC.any_of(
                        EC.url_contains('home'),
                        EC.presence_of_element_located((By.XPATH, "//div[@data-testid='toast']"))
                    )
                )
                
                result = {
                    'success': True,
                    'message': 'Tweet posted successfully',
                    'text': text,
                    'media_count': len(media_paths) if media_paths else 0,
                    'posted_at': time.time()
                }
                
                logger.info("Twitter post successful")
                return result
                
            except TimeoutException:
                return {
                    'success': False,
                    'error': 'Tweet posting failed - timeout waiting for confirmation'
                }
        
        except Exception as e:
            error_msg = f"Twitter posting failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_timeline_tweets(self, count: int = 10) -> Dict[str, Any]:
        """Get recent tweets from timeline"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to home timeline
            self.driver.get('https://twitter.com/home')
            time.sleep(5)
            
            tweets = []
            tweet_elements = self.driver.find_elements(
                By.XPATH, "//article[@data-testid='tweet']"
            )
            
            for i, tweet_element in enumerate(tweet_elements[:count]):
                try:
                    # Get tweet text
                    text_element = tweet_element.find_element(
                        By.XPATH, ".//div[@data-testid='tweetText']"
                    )
                    text = text_element.text
                    
                    # Get user info
                    try:
                        user_element = tweet_element.find_element(
                            By.XPATH, ".//div[@data-testid='User-Name']"
                        )
                        user_name = user_element.text
                    except:
                        user_name = "Unknown"
                    
                    # Get engagement metrics
                    try:
                        reply_count = tweet_element.find_element(
                            By.XPATH, ".//div[@data-testid='reply']//span"
                        ).text or "0"
                        
                        retweet_count = tweet_element.find_element(
                            By.XPATH, ".//div[@data-testid='retweet']//span"
                        ).text or "0"
                        
                        like_count = tweet_element.find_element(
                            By.XPATH, ".//div[@data-testid='like']//span"
                        ).text or "0"
                    except:
                        reply_count = retweet_count = like_count = "0"
                    
                    tweets.append({
                        'text': text,
                        'user': user_name,
                        'replies': reply_count,
                        'retweets': retweet_count,
                        'likes': like_count
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse tweet {i}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'tweets': tweets,
                'count': len(tweets)
            }
        
        except Exception as e:
            error_msg = f"Failed to get Twitter timeline: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def search_tweets(self, query: str, count: int = 10) -> Dict[str, Any]:
        """Search for tweets"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to search
            search_url = f"https://twitter.com/search?q={query}&src=typed_query"
            self.driver.get(search_url)
            time.sleep(5)
            
            tweets = []
            tweet_elements = self.driver.find_elements(
                By.XPATH, "//article[@data-testid='tweet']"
            )
            
            for i, tweet_element in enumerate(tweet_elements[:count]):
                try:
                    # Get tweet text
                    text_element = tweet_element.find_element(
                        By.XPATH, ".//div[@data-testid='tweetText']"
                    )
                    text = text_element.text
                    
                    # Get user info
                    try:
                        user_element = tweet_element.find_element(
                            By.XPATH, ".//div[@data-testid='User-Name']//span"
                        )
                        user_name = user_element.text
                    except:
                        user_name = "Unknown"
                    
                    tweets.append({
                        'text': text,
                        'user': user_name,
                        'query': query
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to parse search result {i}: {str(e)}")
                    continue
            
            return {
                'success': True,
                'tweets': tweets,
                'query': query,
                'count': len(tweets)
            }
        
        except Exception as e:
            error_msg = f"Failed to search Twitter: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def like_tweet(self, tweet_url: str) -> Dict[str, Any]:
        """Like a tweet"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to tweet
            self.driver.get(tweet_url)
            time.sleep(3)
            
            # Click like button
            like_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='like']"))
            )
            like_button.click()
            
            time.sleep(2)
            
            return {
                'success': True,
                'message': 'Tweet liked successfully',
                'tweet_url': tweet_url
            }
        
        except Exception as e:
            error_msg = f"Failed to like tweet: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def retweet(self, tweet_url: str, comment: str = None) -> Dict[str, Any]:
        """Retweet a tweet with optional comment"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to tweet
            self.driver.get(tweet_url)
            time.sleep(3)
            
            # Click retweet button
            retweet_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='retweet']"))
            )
            retweet_button.click()
            
            time.sleep(2)
            
            if comment:
                # Quote tweet with comment
                quote_tweet_option = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Quote Tweet']"))
                )
                quote_tweet_option.click()
                
                time.sleep(2)
                
                # Add comment
                comment_input = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetTextarea_0']"))
                )
                comment_input.send_keys(comment)
                
                # Click Tweet button
                tweet_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='tweetButton']"))
                )
                tweet_button.click()
            else:
                # Simple retweet
                retweet_confirm = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//span[text()='Retweet']"))
                )
                retweet_confirm.click()
            
            time.sleep(3)
            
            return {
                'success': True,
                'message': 'Tweet retweeted successfully',
                'tweet_url': tweet_url,
                'comment': comment
            }
        
        except Exception as e:
            error_msg = f"Failed to retweet: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def follow_user(self, username: str) -> Dict[str, Any]:
        """Follow a user"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to user profile
            profile_url = f"https://twitter.com/{username}"
            self.driver.get(profile_url)
            time.sleep(3)
            
            # Click follow button
            follow_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@data-testid='follow' or @data-testid='unfollow']"))
            )
            
            button_text = follow_button.text.lower()
            if 'follow' in button_text and 'following' not in button_text:
                follow_button.click()
                time.sleep(2)
                
                return {
                    'success': True,
                    'message': f'Successfully followed @{username}',
                    'username': username
                }
            else:
                return {
                    'success': False,
                    'error': f'Already following @{username} or user not found'
                }
        
        except Exception as e:
            error_msg = f"Failed to follow user {username}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Get user profile information"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to user profile
            profile_url = f"https://twitter.com/{username}"
            self.driver.get(profile_url)
            time.sleep(5)
            
            profile_data = {}
            
            try:
                # Get display name
                display_name = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='UserName']//span"
                ).text
                profile_data['display_name'] = display_name
            except:
                profile_data['display_name'] = username
            
            try:
                # Get bio
                bio = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='UserDescription']"
                ).text
                profile_data['bio'] = bio
            except:
                profile_data['bio'] = ""
            
            try:
                # Get follower count
                followers = self.driver.find_element(
                    By.XPATH, "//a[contains(@href, '/followers')]//span"
                ).text
                profile_data['followers'] = followers
            except:
                profile_data['followers'] = "0"
            
            try:
                # Get following count
                following = self.driver.find_element(
                    By.XPATH, "//a[contains(@href, '/following')]//span"
                ).text
                profile_data['following'] = following
            except:
                profile_data['following'] = "0"
            
            try:
                # Get tweet count
                tweet_count = self.driver.find_element(
                    By.XPATH, "//div[contains(text(), 'Tweets')]//span"
                ).text
                profile_data['tweets'] = tweet_count
            except:
                profile_data['tweets'] = "0"
            
            profile_data['username'] = username
            profile_data['url'] = profile_url
            
            return {
                'success': True,
                'profile': profile_data
            }
        
        except Exception as e:
            error_msg = f"Failed to get profile for {username}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def test_credentials(self, username: str, password: str) -> Dict[str, Any]:
        """Test Twitter credentials without full login"""
        try:
            if not self.driver:
                self._setup_driver()
            
            # Attempt login
            login_result = self.login(username, password)
            
            if login_result['success']:
                # Get additional account info
                account_info = {
                    'username': username,
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
            error_msg = f"Twitter credential test failed: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'error': error_msg
            }
    
    def logout(self):
        """Logout from Twitter"""
        try:
            if self.is_logged_in:
                # Click on profile menu
                profile_menu = self.driver.find_element(
                    By.XPATH, "//div[@data-testid='SideNav_AccountSwitcher_Button']"
                )
                profile_menu.click()
                
                time.sleep(2)
                
                # Click logout
                logout_btn = self.driver.find_element(
                    By.XPATH, "//span[text()='Log out @']"
                )
                logout_btn.click()
                
                time.sleep(2)
                
                # Confirm logout
                confirm_logout = self.driver.find_element(
                    By.XPATH, "//span[text()='Log out']"
                )
                confirm_logout.click()
                
                time.sleep(3)
                
                self.is_logged_in = False
                logger.info("Twitter logout successful")
        
        except Exception as e:
            logger.error(f"Twitter logout failed: {str(e)}")
    
    def close(self):
        """Close the browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Twitter WebDriver closed")
        except Exception as e:
            logger.error(f"Failed to close Twitter WebDriver: {str(e)}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.logout()
        self.close()

# Utility functions for Twitter automation
def post_tweet_with_retry(username: str, password: str, text: str, 
                         media_paths: List[str] = None, max_retries: int = 3) -> Dict[str, Any]:
    """Post tweet with retry mechanism"""
    
    for attempt in range(max_retries):
        try:
            with TwitterAutomator() as automator:
                # Login
                login_result = automator.login(username, password)
                if not login_result['success']:
                    return login_result
                
                # Post tweet
                post_result = automator.post_tweet(
                    text=text,
                    media_paths=media_paths
                )
                
                if post_result['success']:
                    return post_result
                else:
                    if attempt < max_retries - 1:
                        logger.warning(f"Tweet attempt {attempt + 1} failed, retrying...")
                        time.sleep(30)  # Wait before retry
                        continue
                    else:
                        return post_result
        
        except Exception as e:
            if attempt < max_retries - 1:
                logger.warning(f"Tweet attempt {attempt + 1} failed with exception: {str(e)}")
                time.sleep(30)
                continue
            else:
                return {
                    'success': False,
                    'error': f"All {max_retries} tweet attempts failed: {str(e)}"
                }
    
    return {
        'success': False,
        'error': f"Tweet failed after {max_retries} attempts"
    }

def batch_follow_users(username: str, password: str, users_to_follow: List[str], 
                      delay_between_follows: int = 30) -> Dict[str, Any]:
    """Follow multiple users with delays to avoid rate limiting"""
    
    results = []
    
    try:
        with TwitterAutomator() as automator:
            # Login
            login_result = automator.login(username, password)
            if not login_result['success']:
                return login_result
            
            for user in users_to_follow:
                try:
                    follow_result = automator.follow_user(user)
                    results.append({
                        'username': user,
                        'success': follow_result['success'],
                        'message': follow_result.get('message', follow_result.get('error'))
                    })
                    
                    # Delay between follows
                    if user != users_to_follow[-1]:  # Don't delay after last user
                        time.sleep(delay_between_follows)
                
                except Exception as e:
                    results.append({
                        'username': user,
                        'success': False,
                        'message': str(e)
                    })
            
            successful_follows = sum(1 for r in results if r['success'])
            
            return {
                'success': True,
                'total_users': len(users_to_follow),
                'successful_follows': successful_follows,
                'results': results
            }
    
    except Exception as e:
        return {
            'success': False,
            'error': f"Batch follow operation failed: {str(e)}",
            'partial_results': results
        }

def schedule_tweets(username: str, password: str, tweets: List[Dict[str, Any]], 
                   interval_minutes: int = 60) -> Dict[str, Any]:
    """Schedule multiple tweets with intervals"""
    import threading
    import schedule
    
    results = []
    
    def post_scheduled_tweet(tweet_data):
        try:
            with TwitterAutomator() as automator:
                login_result = automator.login(username, password)
                if login_result['success']:
                    post_result = automator.post_tweet(
                        text=tweet_data['text'],
                        media_paths=tweet_data.get('media_paths')
                    )
                    results.append({
                        'text': tweet_data['text'][:50] + '...',
                        'success': post_result['success'],
                        'message': post_result.get('message', post_result.get('error')),
                        'posted_at': time.time()
                    })
        except Exception as e:
            results.append({
                'text': tweet_data['text'][:50] + '...',
                'success': False,
                'message': str(e),
                'posted_at': time.time()
            })
    
    # Schedule tweets
    for i, tweet in enumerate(tweets):
        schedule_time = time.time() + (i * interval_minutes * 60)
        threading.Timer(
            i * interval_minutes * 60,
            post_scheduled_tweet,
            args=[tweet]
        ).start()
    
    return {
        'success': True,
        'message': f'Scheduled {len(tweets)} tweets',
        'total_tweets': len(tweets),
        'interval_minutes': interval_minutes,
        'estimated_completion': time.time() + (len(tweets) * interval_minutes * 60)
    }