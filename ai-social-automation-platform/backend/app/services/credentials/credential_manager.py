# app/services/credentials/credential_manager.py
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)

class CredentialManager:
    def __init__(self, db, encryption_key: str):
        self.db = db
        self.credentials_collection = db.credentials
        
        # Initialize encryption
        if len(encryption_key) == 32:
            # If 32 chars, encode to base64 for Fernet
            import base64
            key = base64.urlsafe_b64encode(encryption_key.encode()[:32])
        else:
            # Assume it's already a valid Fernet key
            key = encryption_key.encode()
        
        self.cipher = Fernet(key)
    
    def save_credentials(self, user_id: str, platform: str, username: str, password: str, additional_data: dict = None) -> dict:
        """Encrypt and save user's social media credentials"""
        try:
            # Encrypt password
            encrypted_password = self.cipher.encrypt(password.encode())
            
            credential_data = {
                'user_id': ObjectId(user_id),
                'platform': platform,
                'username': username,
                'encrypted_password': encrypted_password,
                'additional_data': additional_data or {},
                'status': 'active',
                'verified': False,
                'last_verified': None,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            # Upsert credentials
            result = self.credentials_collection.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {'$set': credential_data},
                upsert=True
            )
            
            logger.info(f"Credentials saved for user {user_id} on platform {platform}")
            
            return {
                'success': True,
                'message': f'{platform} credentials saved successfully',
                'credential_id': str(credential_data.get('_id'))
            }
            
        except Exception as e:
            logger.error(f"Error saving credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_credentials(self, user_id: str, platform: str) -> dict:
        """Get and decrypt user's credentials for a platform"""
        try:
            credential = self.credentials_collection.find_one({
                'user_id': ObjectId(user_id),
                'platform': platform,
                'status': 'active'
            })
            
            if not credential:
                return {
                    'success': False,
                    'error': f'No {platform} credentials found'
                }
            
            # Decrypt password
            decrypted_password = self.cipher.decrypt(credential['encrypted_password']).decode()
            
            return {
                'success': True,
                'username': credential['username'],
                'password': decrypted_password,
                'additional_data': credential.get('additional_data', {}),
                'verified': credential.get('verified', False),
                'last_verified': credential.get('last_verified')
            }
            
        except Exception as e:
            logger.error(f"Error retrieving credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_user_credentials(self, user_id: str) -> dict:
        """Get all platforms credentials for a user"""
        try:
            credentials = list(self.credentials_collection.find({
                'user_id': ObjectId(user_id),
                'status': 'active'
            }))
            
            result = {}
            for cred in credentials:
                try:
                    decrypted_password = self.cipher.decrypt(cred['encrypted_password']).decode()
                    result[cred['platform']] = {
                        'username': cred['username'],
                        'password': decrypted_password,
                        'verified': cred.get('verified', False),
                        'last_verified': cred.get('last_verified')
                    }
                except Exception as e:
                    logger.error(f"Error decrypting {cred['platform']} credentials: {str(e)}")
                    continue
            
            return {
                'success': True,
                'credentials': result
            }
            
        except Exception as e:
            logger.error(f"Error retrieving all credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_credentials(self, user_id: str, platform: str, success: bool = True) -> dict:
        """Update credential verification status"""
        try:
            update_data = {
                'verified': success,
                'last_verified': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            if not success:
                update_data['verification_error'] = 'Login failed'
            
            result = self.credentials_collection.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {'$set': update_data}
            )
            
            return {
                'success': True,
                'verified': success,
                'message': f'{platform} credentials {"verified" if success else "verification failed"}'
            }
            
        except Exception as e:
            logger.error(f"Error verifying credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_credentials(self, user_id: str, platform: str) -> dict:
        """Delete credentials for a platform"""
        try:
            result = self.credentials_collection.update_one(
                {'user_id': ObjectId(user_id), 'platform': platform},
                {
                    '$set': {
                        'status': 'deleted',
                        'deleted_at': datetime.utcnow()
                    }
                }
            )
            
            return {
                'success': True,
                'message': f'{platform} credentials deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting credentials: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# app/automation/platforms/instagram_automator.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import logging
import os

logger = logging.getLogger(__name__)

class InstagramAutomator:
    def __init__(self, chrome_options=None):
        self.driver = None
        self.chrome_options = chrome_options or []
        self.wait_time = 10
    
    def setup_driver(self):
        """Setup Chrome driver for Instagram automation"""
        try:
            options = Options()
            
            # Add chrome options
            for option in self.chrome_options:
                options.add_argument(option)
            
            # Additional Instagram-specific options
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            
            logger.info("Instagram Chrome driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {str(e)}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """Login to Instagram"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            # Navigate to Instagram
            self.driver.get("https://www.instagram.com/accounts/login/")
            
            # Wait for page to load
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Find and fill username
            username_input = wait.until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            username_input.clear()
            username_input.send_keys(username)
            
            # Find and fill password
            password_input = self.driver.find_element(By.NAME, "password")
            password_input.clear()
            password_input.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(
                By.XPATH, "//button[@type='submit']"
            )
            login_button.click()
            
            # Wait for login to complete
            time.sleep(5)
            
            # Check if login was successful
            if "accounts/login" not in self.driver.current_url:
                # Handle "Save Your Login Info" popup
                try:
                    not_now_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    not_now_button.click()
                except TimeoutException:
                    pass
                
                # Handle notification popup
                try:
                    not_now_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Not Now')]"))
                    )
                    not_now_button.click()
                except TimeoutException:
                    pass
                
                logger.info(f"Successfully logged in to Instagram as {username}")
                return True
            else:
                logger.error("Instagram login failed - still on login page")
                return False
                
        except Exception as e:
            logger.error(f"Error during Instagram login: {str(e)}")
            return False
    
    def post_image(self, image_path: str, caption: str = "") -> dict:
        """Post an image to Instagram"""
        try:
            if not self.driver:
                return {'success': False, 'error': 'Driver not initialized'}
            
            # Navigate to home page
            self.driver.get("https://www.instagram.com/")
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Click new post button
            new_post_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//span[contains(text(), 'Create')]"))
            )
            new_post_button.click()
            
            # Upload image
            file_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(image_path))
            
            # Click Next
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            
            # Click Next again (crop page)
            time.sleep(2)
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            
            # Add caption
            if caption:
                caption_textarea = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption...']"))
                )
                caption_textarea.clear()
                caption_textarea.send_keys(caption)
            
            # Click Share
            share_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')]"))
            )
            share_button.click()
            
            # Wait for post to complete
            time.sleep(5)
            
            logger.info("Instagram image posted successfully")
            return {
                'success': True,
                'message': 'Image posted to Instagram successfully',
                'platform': 'instagram',
                'post_type': 'image'
            }
            
        except Exception as e:
            logger.error(f"Error posting image to Instagram: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def post_reel(self, video_path: str, caption: str = "") -> dict:
        """Post a reel to Instagram"""
        try:
            if not self.driver:
                return {'success': False, 'error': 'Driver not initialized'}
            
            # Navigate to home page
            self.driver.get("https://www.instagram.com/")
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Click new post button
            new_post_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='menuitem']//span[contains(text(), 'Create')]"))
            )
            new_post_button.click()
            
            # Upload video
            file_input = wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            file_input.send_keys(os.path.abspath(video_path))
            
            # Select Reel option
            reel_option = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Reel')]"))
            )
            reel_option.click()
            
            # Click Next
            next_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Next')]"))
            )
            next_button.click()
            
            # Add caption
            if caption:
                caption_textarea = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Write a caption...']"))
                )
                caption_textarea.clear()
                caption_textarea.send_keys(caption)
            
            # Click Share
            share_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Share')]"))
            )
            share_button.click()
            
            # Wait for reel to upload
            time.sleep(10)
            
            logger.info("Instagram reel posted successfully")
            return {
                'success': True,
                'message': 'Reel posted to Instagram successfully',
                'platform': 'instagram',
                'post_type': 'reel'
            }
            
        except Exception as e:
            logger.error(f"Error posting reel to Instagram: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Instagram automator closed")

# app/automation/platforms/facebook_automator.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import logging
import os

logger = logging.getLogger(__name__)

class FacebookAutomator:
    def __init__(self, chrome_options=None):
        self.driver = None
        self.chrome_options = chrome_options or []
        self.wait_time = 10
    
    def setup_driver(self):
        """Setup Chrome driver for Facebook automation"""
        try:
            options = Options()
            
            for option in self.chrome_options:
                options.add_argument(option)
            
            options.add_argument('--disable-notifications')
            options.add_argument('--disable-popup-blocking')
            
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            
            logger.info("Facebook Chrome driver setup completed")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up Chrome driver: {str(e)}")
            return False
    
    def login(self, username: str, password: str) -> bool:
        """Login to Facebook"""
        try:
            if not self.driver:
                if not self.setup_driver():
                    return False
            
            self.driver.get("https://www.facebook.com/login")
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Find and fill email
            email_input = wait.until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            email_input.clear()
            email_input.send_keys(username)
            
            # Find and fill password
            password_input = self.driver.find_element(By.ID, "pass")
            password_input.clear()
            password_input.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.NAME, "login")
            login_button.click()
            
            time.sleep(5)
            
            # Check if login successful
            if "facebook.com/login" not in self.driver.current_url:
                logger.info(f"Successfully logged in to Facebook as {username}")
                return True
            else:
                logger.error("Facebook login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during Facebook login: {str(e)}")
            return False
    
    def post_text(self, text: str) -> dict:
        """Post text to Facebook"""
        try:
            self.driver.get("https://www.facebook.com/")
            wait = WebDriverWait(self.driver, self.wait_time)
            
            # Click on status update box
            status_box = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), \"What's on your mind\")]"))
            )
            status_box.click()
            
            # Type the post
            text_area = wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            text_area.click()
            text_area.send_keys(text)
            
            # Click Post button
            post_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Post']"))
            )
            post_button.click()
            
            time.sleep(3)
            
            logger.info("Facebook text posted successfully")
            return {
                'success': True,
                'message': 'Text posted to Facebook successfully',
                'platform': 'facebook',
                'post_type': 'text'
            }
            
        except Exception as e:
            logger.error(f"Error posting text to Facebook: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            logger.info("Facebook automator closed")