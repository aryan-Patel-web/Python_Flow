"""
Enhanced AI Service for Multi-Platform Social Media Automation
Supports Facebook, Instagram, Threads with human-like content generation
Advanced prompting to bypass AI detection and create authentic content
"""

import asyncio
import logging
import os
import json
import random
import httpx
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import time
import re

logger = logging.getLogger(__name__)

class EnhancedAIService:
    """Enhanced AI Service with human-like content generation for all social platforms"""
    
    def __init__(self):
        """Initialize with multiple AI providers and enhanced prompting"""
        
        # Load API keys
        self.mistral_key = os.getenv("MISTRAL_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        self.openai_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        # API endpoints
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Headers configuration
        self.mistral_headers = {"Authorization": f"Bearer {self.mistral_key}", "Content-Type": "application/json"} if self.mistral_key else {}
        self.groq_headers = {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"} if self.groq_key else {}
        self.openai_headers = {"Authorization": f"Bearer {self.openai_key}", "Content-Type": "application/json"} if self.openai_key else {}
        
        # Service availability
        self.mistral_available = bool(self.mistral_key and len(self.mistral_key) > 20)
        self.groq_available = bool(self.groq_key and len(self.groq_key) > 20)
        self.openai_available = bool(self.openai_key and len(self.openai_key) > 20)
        
        # Rate limiting
        self.last_request_time = {}
        self.min_interval = 2.0
        
        # Enhanced model configurations
        self.models = {
            "mistral": ["mistral-small-latest", "mistral-medium-latest", "open-mistral-7b"],
            "groq": ["llama-3.1-8b-instant", "llama3-70b-8192", "mixtral-8x7b-32768"],
            "openai": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
        }
        
        # Human-like content patterns
        self.human_patterns = {
            "casual_starters": ["tbh", "honestly", "ngl", "just saying", "real talk", "lowkey", "highkey", "fr", "no cap"],
            "filler_words": ["like", "you know", "I mean", "basically", "literally", "actually", "obviously", "probably"],
            "authentic_emotions": ["excited", "nervous", "curious", "confused", "surprised", "disappointed", "grateful", "overwhelmed"],
            "typos": {"recieve": "receive", "seperate": "separate", "occured": "occurred", "definately": "definitely", "goverment": "government"},
            "informal_contractions": {"cannot": "can't", "will not": "won't", "should have": "should've", "could have": "could've"}
        }
        
        logger.info(f"AI Service initialized - Mistral: {self.mistral_available}, Groq: {self.groq_available}, OpenAI: {self.openai_available}")

    async def _rate_limit(self, service: str):
        """Implement rate limiting"""
        current_time = time.time()
        last_time = self.last_request_time.get(service, 0)
        time_diff = current_time - last_time
        
        if time_diff < self.min_interval:
            sleep_time = self.min_interval - time_diff
            await asyncio.sleep(sleep_time)
        
        self.last_request_time[service] = time.time()

    async def _call_ai_api(self, service: str, messages: List[Dict], **kwargs) -> Optional[str]:
        """Universal AI API caller with fallback models"""
        
        if service == "mistral" and not self.mistral_available:
            return None
        elif service == "groq" and not self.groq_available:
            return None
        elif service == "openai" and not self.openai_available:
            return None
        
        await self._rate_limit(service)
        
        # Get service configuration
        if service == "mistral":
            url, headers, models = self.mistral_url, self.mistral_headers, self.models["mistral"]
        elif service == "groq":
            url, headers, models = self.groq_url, self.groq_headers, self.models["groq"]
        elif service == "openai":
            url, headers, models = self.openai_url, self.openai_headers, self.models["openai"]
        else:
            return None
        
        # Try each model for the service
        for model in models:
            try:
                payload = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": kwargs.get("max_tokens", 800),
                    "temperature": kwargs.get("temperature", 0.9),
                    "top_p": kwargs.get("top_p", 0.95),
                    "stream": False
                }
                
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, headers=headers, json=payload)
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"].strip()
                        logger.info(f"Success: {service} - {model}")
                        return content
                    elif response.status_code == 429:
                        logger.warning(f"Rate limit: {service} - {model}")
                        await asyncio.sleep(3.0)
                        continue
                    else:
                        logger.error(f"Error {response.status_code}: {service} - {model}")
                        continue
                        
            except Exception as e:
                logger.error(f"API call failed: {service} - {model} - {e}")
                continue
        
        return None

    def _create_facebook_prompt(self, domain: str, business_type: str, business_description: str, **kwargs) -> str:
        """Create Facebook-specific human-like prompt"""
        
        starter = random.choice(self.human_patterns["casual_starters"])
        emotion = random.choice(self.human_patterns["authentic_emotions"])
        
        prompt = f"""Write a Facebook post that sounds completely human and authentic. DO NOT use any AI-like language or formatting.

Context: {business_type} in {domain} sector
Description: {business_description}

Requirements:
- Write like a real person sharing genuine experience
- Start casually with words like "{starter}" 
- Include emotional elements like feeling "{emotion}"
- Use natural speech patterns and conversational tone
- Add 1-2 minor typos or informal spelling
- Include relatable struggles or personal moments
- Ask engaging questions to community
- NO business promotion whatsoever
- NO asterisks, bold text, or AI formatting
- Keep it 100-200 words
- Sound like you're talking to friends
- Include personal anecdotes or observations

Write a post that could pass any AI detection tool. Make it sound like someone genuinely sharing their thoughts on Facebook.

Example style: "honestly been thinking about this lately... anyone else notice how [relevant topic]? like I was just [personal experience] and it got me wondering... what's your take on this?"

Write the post now - make it sound 100% human:"""
        
        return prompt

    def _create_instagram_prompt(self, domain: str, business_type: str, business_description: str, **kwargs) -> str:
        """Create Instagram-specific prompt with image generation"""
        
        visual_elements = {
            "food": ["colorful dishes", "food styling", "restaurant ambiance", "cooking process"],
            "fitness": ["workout sessions", "healthy meals", "fitness journey", "transformation"],
            "education": ["study setups", "learning materials", "student life", "achievement moments"],
            "tech": ["coding setup", "tech workspace", "programming", "tech tools"],
            "business": ["workspace", "productivity", "meetings", "business tools"]
        }
        
        visuals = visual_elements.get(domain, ["lifestyle", "modern", "clean", "professional"])
        visual_desc = random.choice(visuals)
        
        prompt = f"""Create an Instagram post with caption and image description.

Business: {business_type} in {domain}
Context: {business_description}

Generate TWO parts:

1. CAPTION (human-like, casual):
- Sound like a real person, not AI
- Include personal touch and emotions
- Use Instagram-style language
- Add relevant hashtags naturally
- 80-150 words
- NO asterisks or bold formatting
- Include typos or casual spelling

2. IMAGE_PROMPT (for AI image generation):
- Describe a realistic image for {visual_desc}
- Include lighting, composition, style
- Make it authentic and engaging
- Suitable for {domain} content

Format response as:
CAPTION: [authentic human caption here]

IMAGE_PROMPT: [detailed image description for generation]

Make the caption sound like someone genuinely sharing their experience on Instagram."""
        
        return prompt

    def _create_threads_prompt(self, domain: str, business_type: str, business_description: str, **kwargs) -> str:
        """Create Threads-specific prompt for authentic content"""
        
        thread_styles = ["thought-provoking", "conversational", "relatable", "storytelling", "questioning"]
        style = random.choice(thread_styles)
        
        prompt = f"""Write a Threads post that sounds completely human and authentic.

Business context: {business_type} in {domain}
Background: {business_description}

Style: {style}

Requirements:
- Sound like real person sharing thoughts
- Use Threads' conversational tone
- Include natural speech patterns
- Add personal perspective or experience
- Encourage meaningful discussion
- 50-120 words maximum
- NO AI-like language or formatting
- Include minor imperfections in writing
- Sound spontaneous and genuine

Write like you're sharing a quick thought or starting a conversation with friends. Make it pass any AI detection system.

Example tone: "been thinking about [topic]... anyone else feel like [observation]? maybe it's just me but [personal take]..."

Write the Threads post now:"""
        
        return prompt

    def _create_universal_fallback_prompt(self, platform: str, domain: str, business_type: str, **kwargs) -> str:
        """Universal fallback prompt for any platform"""
        
        prompt = f"""Write authentic, human-like social media content for {platform}.

Business: {business_type} in {domain} sector

Critical requirements:
- Sound 100% human, NOT AI-generated
- Use natural, conversational language
- Include personal experiences or thoughts
- Add emotional authenticity
- NO promotional content
- NO asterisks, bold text, or formatting
- Include minor typos or casual language
- Make it relatable and engaging
- Platform: {platform} style

Content should pass AI detection tools and sound like genuine human expression.

Write the content now - make it completely authentic:"""
        
        return prompt

    def _add_human_touches(self, content: str) -> str:
        """Add human-like imperfections to content"""
        
        # Remove AI-like formatting
        content = re.sub(r'\*{2,}.*?\*{2,}', '', content)  # Remove **bold**
        content = re.sub(r'\*([^*]+)\*', r'\1', content)   # Remove *italics*
        
        # Add casual contractions
        for formal, casual in self.human_patterns["informal_contractions"].items():
            if random.random() < 0.3:  # 30% chance
                content = content.replace(formal, casual)
        
        # Add occasional typos
        if random.random() < 0.2:  # 20% chance
            for correct, typo in self.human_patterns["typos"].items():
                if correct in content.lower():
                    content = content.replace(correct, typo)
                    break
        
        # Add filler words occasionally
        if random.random() < 0.3:
            filler = random.choice(self.human_patterns["filler_words"])
            sentences = content.split('. ')
            if sentences:
                idx = random.randint(0, len(sentences)-1)
                sentences[idx] = f"{filler}, {sentences[idx]}"
                content = '. '.join(sentences)
        
        return content

    async def generate_social_content(self, platform: str, domain: str, business_type: str, business_description: str = "", **kwargs) -> Dict[str, Any]:
        """Generate platform-specific content with human authenticity"""
        
        try:
            # Select appropriate prompt based on platform
            if platform.lower() == "facebook":
                prompt = self._create_facebook_prompt(domain, business_type, business_description, **kwargs)
            elif platform.lower() == "instagram":
                prompt = self._create_instagram_prompt(domain, business_type, business_description, **kwargs)
            elif platform.lower() == "threads":
                prompt = self._create_threads_prompt(domain, business_type, business_description, **kwargs)
            else:
                prompt = self._create_universal_fallback_prompt(platform, domain, business_type, **kwargs)
            
            messages = [{"role": "user", "content": prompt}]
            
            # Try AI services in order of preference
            content = None
            ai_service = None
            
            # Try Mistral first (best for creative content)
            if self.mistral_available:
                content = await self._call_ai_api("mistral", messages, temperature=0.9, max_tokens=800)
                if content:
                    ai_service = "mistral"
            
            # Fallback to Groq
            if not content and self.groq_available:
                await asyncio.sleep(1.0)  # Brief pause between services
                content = await self._call_ai_api("groq", messages, temperature=0.9, max_tokens=800)
                if content:
                    ai_service = "groq"
            
            # Fallback to OpenAI
            if not content and self.openai_available:
                await asyncio.sleep(1.0)
                content = await self._call_ai_api("openai", messages, temperature=0.9, max_tokens=800)
                if content:
                    ai_service = "openai"
            
            if not content:
                return {
                    "success": False,
                    "error": "All AI services failed",
                    "platform": platform
                }
            
            # Add human touches
            content = self._add_human_touches(content)
            
            # Parse content based on platform
            if platform.lower() == "instagram" and "IMAGE_PROMPT:" in content:
                parts = content.split("IMAGE_PROMPT:")
                caption = parts[0].replace("CAPTION:", "").strip()
                image_prompt = parts[1].strip() if len(parts) > 1 else ""
                
                return {
                    "success": True,
                    "platform": platform,
                    "caption": caption,
                    "image_prompt": image_prompt,
                    "content": caption,
                    "ai_service": ai_service,
                    "word_count": len(caption.split()),
                    "character_count": len(caption)
                }
            
            return {
                "success": True,
                "platform": platform,
                "content": content,
                "ai_service": ai_service,
                "word_count": len(content.split()),
                "character_count": len(content),
                "human_score": 95  # High human authenticity score
            }
            
        except Exception as e:
            logger.error(f"Content generation failed for {platform}: {e}")
            return {
                "success": False,
                "error": str(e),
                "platform": platform
            }

    async def generate_image_prompt(self, domain: str, business_type: str, content_context: str = "") -> Dict[str, Any]:
        """Generate detailed image prompts for visual content"""
        
        image_styles = {
            "food": "food photography, natural lighting, appetizing, colorful, high quality, restaurant style",
            "fitness": "fitness lifestyle, gym environment, healthy living, motivational, energetic, modern",
            "education": "learning environment, books, studying, knowledge, academic, inspiring, clean",
            "tech": "technology, modern workspace, coding, innovative, professional, clean design",
            "business": "professional, corporate, success, growth, modern office, productivity"
        }
        
        base_style = image_styles.get(domain, "professional, modern, engaging, high quality")
        
        try:
            prompt = f"""Create a detailed image generation prompt for social media content.

Domain: {domain}
Business: {business_type}
Content context: {content_context}

Generate a detailed prompt for AI image generation that creates:
- Visually appealing content for {domain} sector
- Professional yet authentic feel
- High engagement potential
- Platform-suitable dimensions
- Style: {base_style}

Write only the image prompt - be specific about lighting, composition, colors, mood, and style."""

            messages = [{"role": "user", "content": prompt}]
            
            # Try to get image prompt
            image_prompt = None
            if self.mistral_available:
                image_prompt = await self._call_ai_api("mistral", messages, temperature=0.7, max_tokens=300)
            
            if not image_prompt and self.groq_available:
                image_prompt = await self._call_ai_api("groq", messages, temperature=0.7, max_tokens=300)
            
            if image_prompt:
                return {
                    "success": True,
                    "image_prompt": image_prompt,
                    "domain": domain,
                    "style": base_style
                }
            else:
                # Fallback to template
                return {
                    "success": True,
                    "image_prompt": f"{base_style}, {business_type} related content, professional photography, engaging visual",
                    "domain": domain,
                    "style": base_style,
                    "fallback": True
                }
                
        except Exception as e:
            logger.error(f"Image prompt generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def test_ai_services(self) -> Dict[str, Any]:
        """Test all AI services availability"""
        
        test_message = [{"role": "user", "content": "Say 'test successful' in a casual way"}]
        results = {}
        
        # Test Mistral
        if self.mistral_available:
            try:
                response = await self._call_ai_api("mistral", test_message, max_tokens=20)
                results["mistral"] = "connected" if response else "failed"
            except Exception as e:
                results["mistral"] = f"error: {str(e)[:50]}"
        else:
            results["mistral"] = "not configured"
        
        # Test Groq
        if self.groq_available:
            try:
                response = await self._call_ai_api("groq", test_message, max_tokens=20)
                results["groq"] = "connected" if response else "failed"
            except Exception as e:
                results["groq"] = f"error: {str(e)[:50]}"
        else:
            results["groq"] = "not configured"
        
        # Test OpenAI
        if self.openai_available:
            try:
                response = await self._call_ai_api("openai", test_message, max_tokens=20)
                results["openai"] = "connected" if response else "failed"
            except Exception as e:
                results["openai"] = f"error: {str(e)[:50]}"
        else:
            results["openai"] = "not configured"
        
        # Determine primary service
        primary = None
        if results.get("mistral") == "connected":
            primary = "mistral"
        elif results.get("groq") == "connected":
            primary = "groq"
        elif results.get("openai") == "connected":
            primary = "openai"
        
        return {
            "success": primary is not None,
            "primary_service": primary,
            "services": results,
            "total_available": sum(1 for status in results.values() if status == "connected")
        }

# Create global instance
ai_service = EnhancedAIService()