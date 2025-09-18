"""
AI Service Module for YouTube & WhatsApp Content Generation
Enhanced AI content generation with multi-platform support
"""

import os
import asyncio
import logging
import json
import httpx
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import random

logger = logging.getLogger(__name__)

class AIService2:
    """Enhanced AI service for YouTube and WhatsApp content generation"""
    
    def __init__(self):
        self.groq_api_key = os.getenv("GROQ_API_KEY")
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY")
        self.primary_service = None
        self.is_mock = False
        
        # Initialize available services
        self.services = {
            "groq": bool(self.groq_api_key),
            "mistral": bool(self.mistral_api_key)
        }
        
        # Set primary service
        if self.groq_api_key:
            self.primary_service = "groq"
        elif self.mistral_api_key:
            self.primary_service = "mistral"
        else:
            self.is_mock = True
            self.primary_service = "mock"
            logger.warning("No AI API keys found - using mock service")
        
        logger.info(f"AI Service initialized - Primary: {self.primary_service}")
    
    async def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI service connection"""
        try:
            if self.is_mock:
                return {
                    "success": False,
                    "primary_service": "mock",
                    "services": self.services,
                    "error": "No API keys configured"
                }
            
            # Test primary service
            test_result = await self._test_service(self.primary_service)
            
            return {
                "success": test_result,
                "primary_service": self.primary_service,
                "services": self.services,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "primary_service": self.primary_service
            }
    
    async def _test_service(self, service_name: str) -> bool:
        """Test specific AI service"""
        try:
            if service_name == "groq":
                return await self._test_groq()
            elif service_name == "mistral":
                return await self._test_mistral()
            return False
        except Exception as e:
            logger.error(f"Service test failed for {service_name}: {e}")
            return False
    
    async def _test_groq(self) -> bool:
        """Test Groq API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [{"role": "user", "content": "Test"}],
                        "model": "mixtral-8x7b-32768",
                        "max_tokens": 10
                    },
                    timeout=30
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def _test_mistral(self) -> bool:
        """Test Mistral API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-medium",
                        "messages": [{"role": "user", "content": "Test"}],
                        "max_tokens": 10
                    },
                    timeout=30
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def generate_youtube_content(
        self,
        content_type: str = "shorts",
        topic: str = "general",
        target_audience: str = "general",
        duration_seconds: int = 30,
        style: str = "engaging"
    ) -> Dict[str, Any]:
        """Generate YouTube content (title, description, script)"""
        try:
            if self.is_mock:
                return self._get_mock_youtube_content(content_type, topic)
            
            prompt = self._create_youtube_prompt(
                content_type, topic, target_audience, duration_seconds, style
            )
            
            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                parsed_content = self._parse_youtube_content(content, content_type)
                
                return {
                    "success": True,
                    "title": parsed_content.get("title"),
                    "description": parsed_content.get("description"),
                    "script": parsed_content.get("script"),
                    "tags": parsed_content.get("tags", []),
                    "content_type": content_type,
                    "ai_service": self.primary_service,
                    "word_count": len(content.split()),
                    "estimated_duration": duration_seconds
                }
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube content generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_whatsapp_content(
        self,
        message_type: str = "promotional",
        business_type: str = "general",
        target_audience: str = "customers",
        occasion: str = None,
        call_to_action: str = None
    ) -> Dict[str, Any]:
        """Generate WhatsApp message content"""
        try:
            if self.is_mock:
                return self._get_mock_whatsapp_content(message_type, business_type)
            
            prompt = self._create_whatsapp_prompt(
                message_type, business_type, target_audience, occasion, call_to_action
            )
            
            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                parsed_content = self._parse_whatsapp_content(content, message_type)
                
                return {
                    "success": True,
                    "message": parsed_content.get("message"),
                    "subject": parsed_content.get("subject"),
                    "call_to_action": parsed_content.get("call_to_action"),
                    "emojis": parsed_content.get("emojis", []),
                    "message_type": message_type,
                    "ai_service": self.primary_service,
                    "char_count": len(parsed_content.get("message", "")),
                    "estimated_read_time": len(parsed_content.get("message", "").split()) // 3
                }
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp content generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_whatsapp_reply(
        self,
        incoming_message: str,
        business_context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Generate WhatsApp auto-reply"""
        try:
            if self.is_mock:
                return {
                    "success": True,
                    "reply": "Thank you for your message! We'll get back to you soon.",
                    "ai_service": "mock"
                }
            
            business_name = business_context.get("business_name", "our business") if business_context else "our business"
            business_type = business_context.get("business_type", "customer service") if business_context else "customer service"
            
            prompt = f"""Generate a professional and helpful WhatsApp auto-reply for {business_name} ({business_type}).

Incoming message: "{incoming_message}"

Requirements:
- Professional but friendly tone
- Acknowledge their message
- Provide helpful response if possible
- Keep it concise (under 100 words)
- Include business name if appropriate
- Use appropriate emojis sparingly

Generate only the reply message, no extra text."""

            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                reply = result.get("content", "").strip()
                
                return {
                    "success": True,
                    "reply": reply,
                    "ai_service": self.primary_service,
                    "original_message": incoming_message
                }
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp reply generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_primary_service(self, prompt: str) -> Dict[str, Any]:
        """Generate content with primary AI service"""
        try:
            if self.primary_service == "groq":
                return await self._generate_with_groq(prompt)
            elif self.primary_service == "mistral":
                return await self._generate_with_mistral(prompt)
            else:
                return {"success": False, "error": "No AI service available"}
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_groq(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Groq API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.groq_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert content creator specializing in social media and digital marketing. Create engaging, authentic, and platform-optimized content."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "model": "mixtral-8x7b-32768",
                        "max_tokens": 2000,
                        "temperature": 0.8,
                        "top_p": 0.9
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "content": content.strip(),
                        "ai_service": "groq",
                        "model": "mixtral-8x7b-32768",
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"Groq API error: {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_with_mistral(self, prompt: str) -> Dict[str, Any]:
        """Generate content using Mistral API"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.mistral.ai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.mistral_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "mistral-medium",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are an expert content creator specializing in social media and digital marketing. Create engaging, authentic, and platform-optimized content."
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "max_tokens": 2000,
                        "temperature": 0.8,
                        "top_p": 0.9
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    return {
                        "success": True,
                        "content": content.strip(),
                        "ai_service": "mistral",
                        "model": "mistral-medium",
                        "tokens_used": data.get("usage", {}).get("total_tokens", 0)
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"Mistral API error: {response.status_code}",
                        "details": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            logger.error(f"Mistral generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_youtube_prompt(
        self,
        content_type: str,
        topic: str,
        target_audience: str,
        duration_seconds: int,
        style: str
    ) -> str:
        """Create optimized prompt for YouTube content generation"""
        duration_text = "under 60 seconds" if content_type == "shorts" else f"approximately {duration_seconds} seconds"
        
        return f"""Create engaging YouTube {content_type} content about {topic}.

Requirements:
- Target audience: {target_audience}
- Duration: {duration_text}
- Style: {style}
- Platform: YouTube {"Shorts" if content_type == "shorts" else ""}

Please provide:
1. TITLE: Catchy, SEO-optimized title (60 chars max)
2. DESCRIPTION: Detailed description with keywords (200-300 words)
3. SCRIPT: {"Short, punchy script for vertical video" if content_type == "shorts" else "Full video script with timestamps"}
4. TAGS: 10 relevant tags for SEO

Format your response as:
TITLE: [title here]
DESCRIPTION: [description here]
SCRIPT: [script here]
TAGS: [tag1, tag2, tag3, etc.]"""
    
    def _create_whatsapp_prompt(
        self,
        message_type: str,
        business_type: str,
        target_audience: str,
        occasion: str = None,
        call_to_action: str = None
    ) -> str:
        """Create optimized prompt for WhatsApp content generation"""
        occasion_text = f" for {occasion}" if occasion else ""
        cta_text = f"\n- Call to action: {call_to_action}" if call_to_action else ""
        
        return f"""Create a {message_type} WhatsApp message for a {business_type} business{occasion_text}.

Requirements:
- Target audience: {target_audience}
- Message type: {message_type}
- Keep under 160 characters for SMS compatibility
- Professional but friendly tone
- Use appropriate emojis (2-3 max)
- Clear and actionable{cta_text}

Format your response as:
SUBJECT: [subject line if needed]
MESSAGE: [main message content]
CTA: [call to action]
EMOJIS: [list of suggested emojis]"""
    
    def _parse_youtube_content(self, content: str, content_type: str) -> Dict[str, Any]:
        """Parse AI-generated YouTube content"""
        try:
            lines = content.strip().split('\n')
            result = {
                "title": "",
                "description": "",
                "script": "",
                "tags": []
            }
            
            current_section = None
            section_content = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('TITLE:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'title'
                    section_content = [line[6:].strip()]
                elif line.startswith('DESCRIPTION:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'description'
                    section_content = [line[12:].strip()]
                elif line.startswith('SCRIPT:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'script'
                    section_content = [line[7:].strip()]
                elif line.startswith('TAGS:'):
                    if current_section:
                        result[current_section] = '\n'.join(section_content).strip()
                    current_section = 'tags'
                    tags_text = line[5:].strip()
                    result['tags'] = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                elif current_section and line:
                    section_content.append(line)
            
            # Handle last section
            if current_section and current_section != 'tags':
                result[current_section] = '\n'.join(section_content).strip()
            
            # Fallback parsing if structured format not found
            if not result['title'] and content:
                lines = content.split('\n')
                result['title'] = lines[0][:60] if lines else "AI Generated Content"
                result['description'] = content[:300] if len(content) > 60 else content
                result['script'] = content
            
            return result
            
        except Exception as e:
            logger.error(f"YouTube content parsing failed: {e}")
            return {
                "title": "AI Generated Content",
                "description": content[:300] if content else "AI generated description",
                "script": content or "AI generated script",
                "tags": ["AI", "generated", "content"]
            }
    
    def _parse_whatsapp_content(self, content: str, message_type: str) -> Dict[str, Any]:
        """Parse AI-generated WhatsApp content"""
        try:
            lines = content.strip().split('\n')
            result = {
                "subject": "",
                "message": "",
                "call_to_action": "",
                "emojis": []
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith('SUBJECT:'):
                    result['subject'] = line[8:].strip()
                elif line.startswith('MESSAGE:'):
                    result['message'] = line[8:].strip()
                elif line.startswith('CTA:'):
                    result['call_to_action'] = line[4:].strip()
                elif line.startswith('EMOJIS:'):
                    emojis_text = line[7:].strip()
                    result['emojis'] = [emoji.strip() for emoji in emojis_text.split(',') if emoji.strip()]
            
            # Fallback if structured format not found
            if not result['message'] and content:
                result['message'] = content.strip()
            
            return result
            
        except Exception as e:
            logger.error(f"WhatsApp content parsing failed: {e}")
            return {
                "subject": "",
                "message": content.strip() if content else "AI generated message",
                "call_to_action": "",
                "emojis": []
            }
    
    def _get_mock_youtube_content(self, content_type: str, topic: str) -> Dict[str, Any]:
        """Generate mock YouTube content for testing"""
        mock_titles = [
            f"Amazing {topic} Tips You Need to Know!",
            f"The Ultimate {topic} Guide for Beginners",
            f"5 Mind-Blowing {topic} Facts That Will Surprise You"
        ]
        
        return {
            "success": True,
            "title": random.choice(mock_titles),
            "description": f"Mock description for {content_type} about {topic}. This is generated by the mock AI service for testing purposes.",
            "script": f"Mock script for {content_type}:\n1. Introduction about {topic}\n2. Main content points\n3. Call to action",
            "tags": ["mock", topic.lower(), content_type, "ai", "generated"],
            "content_type": content_type,
            "ai_service": "mock",
            "word_count": 25,
            "estimated_duration": 30 if content_type == "shorts" else 180
        }
    
    def _get_mock_whatsapp_content(self, message_type: str, business_type: str) -> Dict[str, Any]:
        """Generate mock WhatsApp content for testing"""
        mock_messages = {
            "promotional": f"🎉 Special offer from your favorite {business_type}! Limited time only. Contact us for details!",
            "customer_service": f"Thank you for contacting {business_type}! We'll get back to you within 24 hours.",
            "notification": f"📢 Important update from {business_type}. Check our latest news and updates."
        }
        
        message = mock_messages.get(message_type, f"Mock {message_type} message for {business_type}")
        
        return {
            "success": True,
            "message": message,
            "subject": f"Mock {message_type} subject",
            "call_to_action": "Contact us for more information",
            "emojis": ["🎉", "📢", "✨"],
            "message_type": message_type,
            "ai_service": "mock",
            "char_count": len(message),
            "estimated_read_time": 3
        }
    
    # Backward compatibility methods
    async def generate_reddit_domain_content(self, **kwargs) -> Dict[str, Any]:
        """Backward compatibility with existing Reddit AI service"""
        try:
            domain = kwargs.get('domain', 'general')
            business_type = kwargs.get('business_type', 'Business')
            content_style = kwargs.get('content_style', 'engaging')
            
            if self.is_mock:
                return {
                    "success": True,
                    "title": f"Mock {domain} content for {business_type}",
                    "content": f"Mock content generated for {business_type} in {domain} domain with {content_style} style.",
                    "ai_service": "mock",
                    "word_count": 15
                }
            
            prompt = f"""Create engaging {content_style} content for a {business_type} in the {domain} domain.
            
Requirements:
- Professional and informative
- Engaging for social media
- Include valuable insights
- Keep it concise but informative

Format:
TITLE: [engaging title]
CONTENT: [main content]"""

            result = await self._generate_with_primary_service(prompt)
            
            if result.get("success"):
                content = result.get("content", "")
                lines = content.split('\n')
                
                title = ""
                main_content = ""
                
                for line in lines:
                    if line.startswith('TITLE:'):
                        title = line[6:].strip()
                    elif line.startswith('CONTENT:'):
                        main_content = line[8:].strip()
                    elif not title and line.strip():
                        title = line.strip()
                    elif title and line.strip():
                        main_content += line + "\n"
                
                return {
                    "success": True,
                    "title": title or f"AI Generated {domain} Content",
                    "content": main_content.strip() or content,
                    "ai_service": self.primary_service,
                    "word_count": len(content.split())
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Backward compatibility content generation failed: {e}")
            return {"success": False, "error": str(e)}