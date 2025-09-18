"""
WhatsApp Cloud API Automation Module - Complete WhatsApp Business Automation
Multi-user support with message templates, media sending, and campaign management
"""

import os
import asyncio
import logging
import json
import base64
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
import httpx
import requests
import aiofiles
import tempfile
from urllib.parse import quote

logger = logging.getLogger(__name__)

@dataclass
class WhatsAppConfig:
    """Configuration for WhatsApp automation"""
    user_id: str
    business_name: str = ""
    phone_number_id: str = ""
    access_token: str = ""
    webhook_verify_token: str = ""
    message_templates: List[str] = field(default_factory=list)
    auto_reply_enabled: bool = False
    campaign_enabled: bool = False
    broadcast_lists: List[str] = field(default_factory=list)
    business_hours: Dict[str, str] = field(default_factory=lambda: {"start": "09:00", "end": "18:00"})
    timezone: str = "UTC"

class WhatsAppCloudAPI:
    """WhatsApp Cloud API connector"""
    
    def __init__(self, access_token: str, phone_number_id: str, api_version: str = "v18.0"):
        self.access_token = access_token
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
    async def send_text_message(self, to: str, message: str) -> Dict[str, Any]:
        """Send text message via WhatsApp Cloud API"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get("messages", [{}])[0].get("id")
                    
                    logger.info(f"WhatsApp message sent successfully: {message_id}")
                    
                    return {
                        "success": True,
                        "message_id": message_id,
                        "to": to,
                        "message": message,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    error_data = response.json() if response.content else {}
                    logger.error(f"WhatsApp message failed: {response.status_code} - {error_data}")
                    
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp message send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_media_message(
        self, 
        to: str, 
        media_type: str, 
        media_url: str, 
        caption: str = None
    ) -> Dict[str, Any]:
        """Send media message (image, video, document) via WhatsApp"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            media_payload = {
                "link": media_url
            }
            
            if caption:
                media_payload["caption"] = caption
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": media_type,
                media_type: media_payload
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get("messages", [{}])[0].get("id")
                    
                    return {
                        "success": True,
                        "message_id": message_id,
                        "media_type": media_type,
                        "media_url": media_url,
                        "caption": caption
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp media send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_template_message(
        self,
        to: str,
        template_name: str,
        language_code: str = "en_US",
        parameters: List[str] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp template message"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            template_payload = {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
            
            if parameters:
                template_payload["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                }]
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": template_payload
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get("messages", [{}])[0].get("id")
                    
                    return {
                        "success": True,
                        "message_id": message_id,
                        "template_name": template_name,
                        "parameters": parameters
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp template send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_business_profile(self) -> Dict[str, Any]:
        """Get WhatsApp Business profile information"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "profile": result
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"WhatsApp profile fetch failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def mark_message_read(self, message_id: str) -> Dict[str, Any]:
        """Mark incoming message as read"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=self.headers,
                    json=payload,
                    timeout=30
                )
                
                return {
                    "success": response.status_code == 200,
                    "message_id": message_id
                }
                
        except Exception as e:
            logger.error(f"WhatsApp mark read failed: {e}")
            return {"success": False, "error": str(e)}

class WhatsAppWebhookHandler:
    """Handle WhatsApp webhook events"""
    
    def __init__(self, verify_token: str, app_secret: str = None):
        self.verify_token = verify_token
        self.app_secret = app_secret
        
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify webhook subscription"""
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        
        logger.warning("WhatsApp webhook verification failed")
        return None
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature"""
        if not self.app_secret:
            return True  # Skip verification if no secret configured
        
        try:
            expected_signature = hmac.new(
                self.app_secret.encode('utf-8'),
                payload,
                hashlib.sha256
            ).hexdigest()
            
            received_signature = signature.replace('sha256=', '')
            
            return hmac.compare_digest(expected_signature, received_signature)
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    def parse_webhook_event(self, webhook_data: Dict) -> List[Dict[str, Any]]:
        """Parse incoming webhook events"""
        try:
            events = []
            
            for entry in webhook_data.get("entry", []):
                for change in entry.get("changes", []):
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        
                        # Parse incoming messages
                        for message in value.get("messages", []):
                            events.append({
                                "type": "message",
                                "message_id": message.get("id"),
                                "from": message.get("from"),
                                "timestamp": message.get("timestamp"),
                                "text": message.get("text", {}).get("body", ""),
                                "message_type": message.get("type"),
                                "phone_number_id": value.get("metadata", {}).get("phone_number_id")
                            })
                        
                        # Parse message status updates
                        for status in value.get("statuses", []):
                            events.append({
                                "type": "status",
                                "message_id": status.get("id"),
                                "recipient_id": status.get("recipient_id"),
                                "status": status.get("status"),
                                "timestamp": status.get("timestamp"),
                                "phone_number_id": value.get("metadata", {}).get("phone_number_id")
                            })
            
            return events
            
        except Exception as e:
            logger.error(f"Webhook parsing failed: {e}")
            return []

class WhatsAppAutomationScheduler:
    """WhatsApp automation and campaign scheduler"""
    
    def __init__(self, ai_service, database_manager):
        self.ai_service = ai_service
        self.database = database_manager
        self.active_configs = {}
        self.whatsapp_apis = {}  # user_id -> WhatsAppCloudAPI instance
        self.is_running = False
        
        logger.info("WhatsApp Automation Scheduler initialized")
    
    async def setup_whatsapp_automation(
        self,
        user_id: str,
        phone_number_id: str,
        access_token: str,
        config: WhatsAppConfig
    ) -> Dict[str, Any]:
        """Setup WhatsApp automation for user"""
        try:
            # Create WhatsApp API instance for user
            whatsapp_api = WhatsAppCloudAPI(access_token, phone_number_id)
            
            # Test connection
            profile_result = await whatsapp_api.get_business_profile()
            if not profile_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to connect to WhatsApp API",
                    "details": profile_result.get("error")
                }
            
            # Store API instance and config
            self.whatsapp_apis[user_id] = whatsapp_api
            config.phone_number_id = phone_number_id
            config.access_token = access_token
            
            self.active_configs[user_id] = {
                "whatsapp_automation": {
                    "config": config,
                    "enabled": True,
                    "created_at": datetime.now(),
                    "total_messages": 0,
                    "successful_messages": 0,
                    "failed_messages": 0,
                    "last_activity": None
                }
            }
            
            # Save to database
            if hasattr(self.database, 'store_automation_config'):
                config_dict = config.__dict__.copy()
                # Don't store sensitive tokens in config
                config_dict.pop('access_token', None)
                
                await self.database.store_automation_config(
                    user_id=user_id,
                    config_type='whatsapp_automation',
                    config_data=config_dict
                )
            
            logger.info(f"WhatsApp automation setup successful for user {user_id}")
            
            return {
                "success": True,
                "message": "WhatsApp automation enabled successfully!",
                "config": {
                    "business_name": config.business_name,
                    "phone_number_id": phone_number_id,
                    "auto_reply_enabled": config.auto_reply_enabled,
                    "campaign_enabled": config.campaign_enabled,
                    "business_hours": config.business_hours
                },
                "business_profile": profile_result.get("profile", {}),
                "scheduler_status": "Active"
            }
            
        except Exception as e:
            logger.error(f"WhatsApp automation setup failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_message(
        self,
        user_id: str,
        to: str,
        message: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send message via user's WhatsApp API"""
        try:
            if user_id not in self.whatsapp_apis:
                return {
                    "success": False,
                    "error": "WhatsApp not configured for user"
                }
            
            whatsapp_api = self.whatsapp_apis[user_id]
            
            if message_type == "text":
                result = await whatsapp_api.send_text_message(to, message)
            else:
                return {
                    "success": False,
                    "error": f"Message type '{message_type}' not supported yet"
                }
            
            # Update statistics
            if user_id in self.active_configs:
                config = self.active_configs[user_id].get("whatsapp_automation", {})
                if result.get("success"):
                    config["successful_messages"] = config.get("successful_messages", 0) + 1
                else:
                    config["failed_messages"] = config.get("failed_messages", 0) + 1
                config["total_messages"] = config.get("total_messages", 0) + 1
                config["last_activity"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp message send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_media_message(
        self,
        user_id: str,
        to: str,
        media_url: str,
        media_type: str = "image",
        caption: str = None
    ) -> Dict[str, Any]:
        """Send media message via user's WhatsApp API"""
        try:
            if user_id not in self.whatsapp_apis:
                return {
                    "success": False,
                    "error": "WhatsApp not configured for user"
                }
            
            whatsapp_api = self.whatsapp_apis[user_id]
            result = await whatsapp_api.send_media_message(to, media_type, media_url, caption)
            
            # Update statistics
            if user_id in self.active_configs and result.get("success"):
                config = self.active_configs[user_id].get("whatsapp_automation", {})
                config["successful_messages"] = config.get("successful_messages", 0) + 1
                config["total_messages"] = config.get("total_messages", 0) + 1
                config["last_activity"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp media send failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def handle_incoming_message(
        self,
        user_id: str,
        message_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming message and auto-reply if configured"""
        try:
            config = self.active_configs.get(user_id, {}).get("whatsapp_automation", {}).get("config")
            
            if not config or not config.auto_reply_enabled:
                return {
                    "success": True,
                    "action": "no_auto_reply",
                    "message": "Auto-reply not enabled"
                }
            
            # Check business hours
            if not self._is_business_hours(config):
                # Send out-of-hours message
                auto_reply = "Thank you for your message! We're currently outside business hours and will respond soon."
            else:
                # Generate AI response
                ai_response = await self._generate_auto_reply(
                    user_id,
                    message_data.get("text", ""),
                    config
                )
                auto_reply = ai_response.get("reply", "Thank you for your message! We'll get back to you soon.")
            
            # Send auto-reply
            from_number = message_data.get("from")
            if from_number:
                reply_result = await self.send_message(user_id, from_number, auto_reply)
                
                return {
                    "success": True,
                    "action": "auto_reply_sent",
                    "reply": auto_reply,
                    "reply_result": reply_result
                }
            
            return {
                "success": False,
                "error": "No sender number found"
            }
            
        except Exception as e:
            logger.error(f"WhatsApp incoming message handling failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_broadcast(
        self,
        user_id: str,
        recipient_list: List[str],
        message: str,
        media_url: str = None,
        media_type: str = None
    ) -> Dict[str, Any]:
        """Send broadcast message to multiple recipients"""
        try:
            if user_id not in self.whatsapp_apis:
                return {
                    "success": False,
                    "error": "WhatsApp not configured for user"
                }
            
            results = []
            successful_count = 0
            failed_count = 0
            
            for recipient in recipient_list:
                try:
                    if media_url and media_type:
                        result = await self.send_media_message(
                            user_id, recipient, media_url, media_type, message
                        )
                    else:
                        result = await self.send_message(user_id, recipient, message)
                    
                    if result.get("success"):
                        successful_count += 1
                    else:
                        failed_count += 1
                    
                    results.append({
                        "recipient": recipient,
                        "success": result.get("success", False),
                        "message_id": result.get("message_id"),
                        "error": result.get("error")
                    })
                    
                    # Small delay between messages to avoid rate limiting
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    failed_count += 1
                    results.append({
                        "recipient": recipient,
                        "success": False,
                        "error": str(e)
                    })
            
            return {
                "success": True,
                "broadcast_results": {
                    "total_recipients": len(recipient_list),
                    "successful": successful_count,
                    "failed": failed_count,
                    "results": results
                }
            }
            
        except Exception as e:
            logger.error(f"WhatsApp broadcast failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_auto_reply(
        self,
        user_id: str,
        incoming_message: str,
        config: WhatsAppConfig
    ) -> Dict[str, Any]:
        """Generate AI-powered auto-reply"""
        try:
            if hasattr(self.ai_service, 'generate_whatsapp_reply'):
                return await self.ai_service.generate_whatsapp_reply(
                    incoming_message=incoming_message,
                    business_context={
                        "business_name": config.business_name,
                        "business_type": "customer_service"
                    }
                )
            elif hasattr(self.ai_service, 'generate_reddit_domain_content'):
                # Fallback using existing AI service
                content_result = await self.ai_service.generate_reddit_domain_content(
                    domain="business",
                    business_type=config.business_name or "Customer Service",
                    target_audience="customers",
                    content_style="helpful"
                )
                
                if content_result.get("success"):
                    return {
                        "success": True,
                        "reply": f"Thank you for reaching out! {content_result.get('content', '')[:100]}..."
                    }
            
            # Default reply
            return {
                "success": True,
                "reply": f"Thank you for contacting {config.business_name or 'us'}! We'll get back to you soon."
            }
            
        except Exception as e:
            logger.error(f"Auto-reply generation failed: {e}")
            return {
                "success": True,
                "reply": "Thank you for your message! We'll get back to you soon."
            }
    
    def _is_business_hours(self, config: WhatsAppConfig) -> bool:
        """Check if current time is within business hours"""
        try:
            current_time = datetime.now().time()
            
            start_time = datetime.strptime(
                config.business_hours.get("start", "09:00"), "%H:%M"
            ).time()
            
            end_time = datetime.strptime(
                config.business_hours.get("end", "18:00"), "%H:%M"
            ).time()
            
            return start_time <= current_time <= end_time
            
        except Exception:
            return True  # Default to always in business hours if parsing fails
    
    async def get_automation_status(self, user_id: str) -> Dict[str, Any]:
        """Get WhatsApp automation status for user"""
        try:
            user_config = self.active_configs.get(user_id, {})
            whatsapp_config = user_config.get("whatsapp_automation", {})
            config_obj = whatsapp_config.get("config")
            
            if config_obj and hasattr(config_obj, '__dict__'):
                config_data = config_obj.__dict__.copy()
                # Remove sensitive data
                config_data.pop('access_token', None)
            elif isinstance(config_obj, dict):
                config_data = config_obj.copy()
                config_data.pop('access_token', None)
            else:
                config_data = None
            
            return {
                "success": True,
                "user_id": user_id,
                "whatsapp_connected": user_id in self.whatsapp_apis,
                "whatsapp_automation": {
                    "enabled": "whatsapp_automation" in user_config,
                    "config": config_data,
                    "stats": {
                        "total_messages": whatsapp_config.get("total_messages", 0),
                        "successful_messages": whatsapp_config.get("successful_messages", 0),
                        "failed_messages": whatsapp_config.get("failed_messages", 0),
                        "last_activity": whatsapp_config.get("last_activity")
                    }
                },
                "scheduler_running": self.is_running,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"WhatsApp status check failed: {e}")
            return {"success": False, "error": str(e)}