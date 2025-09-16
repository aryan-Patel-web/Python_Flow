"""
Streamlined AI Service - Real Mistral/Groq Integration
Compatible with main.py - Enhanced with asyncio and better error handling
Uses direct HTTP API calls instead of mistralai library to avoid pyarrow dependency
Generates unique, human-like content for Reddit automation
"""

import asyncio
import logging
import os
import json
import random
import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class AIService:
    """Streamlined AI Service for Reddit content generation using HTTP APIs"""
    
    def __init__(self):
        """Initialize with HTTP clients for APIs"""
        
        # Load API keys from environment
        self.mistral_key = os.getenv("MISTRAL_API_KEY", "").strip()
        self.groq_key = os.getenv("GROQ_API_KEY", "").strip()
        
        # Debug key loading
        print(f"Mistral Key Found: {bool(self.mistral_key and len(self.mistral_key) > 20)}")
        print(f"Groq Key Found: {bool(self.groq_key and len(self.groq_key) > 20)}")
        
        # API endpoints
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # HTTP headers
        self.mistral_headers = {
            "Authorization": f"Bearer {self.mistral_key}",
            "Content-Type": "application/json",
            "User-Agent": "Reddit-AI-Service/1.0"
        } if self.mistral_key else {}
        
        self.groq_headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json", 
            "User-Agent": "Reddit-AI-Service/1.0"
        } if self.groq_key else {}
        
        # Initialize status
        self.mistral_available = bool(self.mistral_key and len(self.mistral_key) > 20)
        self.groq_available = bool(self.groq_key and len(self.groq_key) > 20)
        
        # Rate limiting and request management
        self.mistral_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent Mistral requests
        self.groq_semaphore = asyncio.Semaphore(2)     # Max 2 concurrent Groq requests
        self.mistral_last_request = 0
        self.groq_last_request = 0
        self.min_request_interval = 3.0  # Minimum 3 seconds between requests
        
        # Enhanced model configurations with multiple fallbacks
        self.mistral_models = [
            "mistral-small-latest",    # Primary - most reliable
            "mistral-medium-latest",   # Fallback 1
            "open-mistral-7b"          # Fallback 2 - fastest
        ]
        
        self.groq_models = [
            "llama-3.1-8b-instant",    # Primary - fast and reliable
            "llama3-70b-8192",         # Fallback 1 - higher quality  
            "mixtral-8x7b-32768"       # Fallback 2 - good performance
        ]
        
        if self.mistral_available:
            print("✅ Mistral AI HTTP client ready")
            logger.info("Mistral AI HTTP client initialized")
        
        if self.groq_available:
            print("✅ Groq AI HTTP client ready")
            logger.info("Groq AI HTTP client initialized")
        
        if not (self.mistral_available or self.groq_available):
            print("❌ No AI services configured - check API keys")
            logger.warning("No AI services available")
        
        # Content variety templates
        self.content_styles = {
            "question": ["Have you ever wondered...", "What's your experience with...", "How do you handle..."],
            "tip": ["Here's a practical tip:", "Something that helped me:", "A technique worth trying:"],
            "story": ["I recently discovered...", "Here's what I learned...", "My experience with..."],
            "discussion": ["Let's talk about...", "What are your thoughts on...", "I'm curious about..."],
            "advice": ["If you're struggling with...", "Here's what works for...", "Consider this approach:"]
        }
        
        self.domain_contexts = {
            "education": {
                "topics": ["study techniques", "exam strategies", "time management", "motivation", "career planning"],
                "audiences": ["JEE aspirants", "NEET students", "college students", "working professionals"],
                "pain_points": ["exam stress", "time management", "concentration issues", "career confusion"]
            },
            "tech": {
                "topics": ["programming tips", "career advice", "tool recommendations", "learning paths", "project ideas"],
                "audiences": ["new developers", "experienced programmers", "career switchers", "students"],
                "pain_points": ["learning curve", "imposter syndrome", "staying updated", "work-life balance"]
            },
            "health": {
                "topics": ["fitness routines", "nutrition tips", "mental wellness", "healthy habits", "workout motivation"],
                "audiences": ["fitness beginners", "health enthusiasts", "busy professionals", "students"],
                "pain_points": ["lack of time", "motivation issues", "diet confusion", "stress management"]
            },
            "business": {
                "topics": ["startup advice", "business strategies", "marketing tips", "financial planning", "productivity"],
                "audiences": ["entrepreneurs", "small business owners", "freelancers", "corporate professionals"],
                "pain_points": ["funding challenges", "market competition", "work-life balance", "scaling issues"]
            }
        }
    
    async def _wait_for_rate_limit(self, service: str) -> None:
        """Implement intelligent rate limiting"""
        current_time = time.time()
        
        if service == "mistral":
            time_since_last = current_time - self.mistral_last_request
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                logger.info(f"Rate limiting Mistral: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            self.mistral_last_request = time.time()
        
        elif service == "groq":
            time_since_last = current_time - self.groq_last_request
            if time_since_last < self.min_request_interval:
                wait_time = self.min_request_interval - time_since_last
                logger.info(f"Rate limiting Groq: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            self.groq_last_request = time.time()
    
    async def _call_mistral_api(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Enhanced Mistral API call with concurrent handling and model fallbacks"""
        if not self.mistral_available:
            return None
        
        async with self.mistral_semaphore:  # Limit concurrent requests
            await self._wait_for_rate_limit("mistral")
            
            # Try multiple Mistral models
            for model_idx, model in enumerate(self.mistral_models):
                try:
                    payload = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 600),
                        "temperature": kwargs.get("temperature", 0.9),
                        "top_p": kwargs.get("top_p", 0.95),
                        "stream": False
                    }
                    
                    timeout_duration = 45.0 + (model_idx * 15.0)  # Increase timeout for fallback models
                    
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(timeout_duration, connect=10.0),
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
                    ) as client:
                        logger.info(f"Trying Mistral model: {model}")
                        response = await client.post(
                            self.mistral_url,
                            headers=self.mistral_headers,
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            content = data["choices"][0]["message"]["content"].strip()
                            logger.info(f"✅ Mistral API success with model: {model}")
                            return content
                        
                        elif response.status_code == 429:
                            logger.warning(f"⚠️ Mistral rate limit hit with {model}")
                            if model_idx < len(self.mistral_models) - 1:
                                await asyncio.sleep(5.0)  # Wait before trying next model
                                continue
                            else:
                                logger.error("All Mistral models hit rate limit")
                                return None
                        
                        else:
                            logger.error(f"❌ Mistral API error with {model}: {response.status_code}")
                            if model_idx < len(self.mistral_models) - 1:
                                continue
                            else:
                                return None
                            
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Mistral API timeout with {model}")
                    if model_idx < len(self.mistral_models) - 1:
                        continue
                    else:
                        return None
                except Exception as e:
                    logger.error(f"💥 Mistral API call failed with {model}: {e}")
                    if model_idx < len(self.mistral_models) - 1:
                        continue
                    else:
                        return None
            
            logger.error("🚫 All Mistral models failed")
            return None
    
    async def _call_groq_api(self, messages: List[Dict], **kwargs) -> Optional[str]:
        """Enhanced Groq API call with concurrent handling and model fallbacks"""
        if not self.groq_available:
            return None
        
        async with self.groq_semaphore:  # Limit concurrent requests
            await self._wait_for_rate_limit("groq")
            
            # Try multiple Groq models
            for model_idx, model in enumerate(self.groq_models):
                try:
                    payload = {
                        "model": model,
                        "messages": messages,
                        "max_tokens": kwargs.get("max_tokens", 600),
                        "temperature": kwargs.get("temperature", 0.9),
                        "top_p": kwargs.get("top_p", 0.95),
                        "stream": False
                    }
                    
                    timeout_duration = 45.0 + (model_idx * 15.0)  # Increase timeout for fallback models
                    
                    async with httpx.AsyncClient(
                        timeout=httpx.Timeout(timeout_duration, connect=10.0),
                        limits=httpx.Limits(max_connections=5, max_keepalive_connections=2)
                    ) as client:
                        logger.info(f"Trying Groq model: {model}")
                        response = await client.post(
                            self.groq_url,
                            headers=self.groq_headers,
                            json=payload
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            content = data["choices"][0]["message"]["content"].strip()
                            logger.info(f"✅ Groq API success with model: {model}")
                            return content
                        
                        elif response.status_code == 429:
                            logger.warning(f"⚠️ Groq rate limit hit with {model}")
                            # Extract wait time from error message if available
                            try:
                                error_data = response.json()
                                error_msg = error_data.get("error", {}).get("message", "")
                                if "Please try again in" in error_msg:
                                    # Extract milliseconds and convert to seconds
                                    import re
                                    match = re.search(r'(\d+(?:\.\d+)?)ms', error_msg)
                                    if match:
                                        wait_ms = float(match.group(1))
                                        wait_time = (wait_ms / 1000.0) + 2.0  # Add 2 seconds buffer
                                        logger.info(f"Groq suggested wait: {wait_time:.1f}s")
                                        await asyncio.sleep(min(wait_time, 10.0))  # Cap at 10 seconds
                                    else:
                                        await asyncio.sleep(8.0)
                                else:
                                    await asyncio.sleep(6.0)
                            except:
                                await asyncio.sleep(6.0)
                            
                            if model_idx < len(self.groq_models) - 1:
                                continue
                            else:
                                logger.error("All Groq models hit rate limit")
                                return None
                        
                        else:
                            logger.error(f"❌ Groq API error with {model}: {response.status_code}")
                            if model_idx < len(self.groq_models) - 1:
                                continue
                            else:
                                return None
                            
                except asyncio.TimeoutError:
                    logger.error(f"⏰ Groq API timeout with {model}")
                    if model_idx < len(self.groq_models) - 1:
                        continue
                    else:
                        return None
                except Exception as e:
                    logger.error(f"💥 Groq API call failed with {model}: {e}")
                    if model_idx < len(self.groq_models) - 1:
                        continue
                    else:
                        return None
            
            logger.error("🚫 All Groq models failed")
            return None
    
    async def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI service connections - SEQUENTIAL to avoid rate limits"""
        try:
            services = {}
            primary = None
            
            # Test Mistral first (SEQUENTIAL, not concurrent)
            if self.mistral_available:
                try:
                    messages = [{"role": "user", "content": "Hi"}]
                    response = await self._call_mistral_api(messages, max_tokens=5)
                    
                    if response:
                        services["mistral"] = "connected"
                        primary = "mistral"
                        logger.info("✅ Mistral HTTP test successful")
                    else:
                        services["mistral"] = "failed to get response"
                except Exception as e:
                    services["mistral"] = f"failed: {str(e)[:50]}"
                    logger.error(f"❌ Mistral test failed: {e}")
            else:
                services["mistral"] = "not configured"
            
            # Wait between tests to avoid rate limits
            await asyncio.sleep(2.0)
            
            # Test Groq second (SEQUENTIAL)
            if self.groq_available:
                try:
                    messages = [{"role": "user", "content": "Hi"}]
                    response = await self._call_groq_api(messages, max_tokens=5)
                    
                    if response:
                        services["groq"] = "connected"
                        if not primary:
                            primary = "groq"
                        logger.info("✅ Groq HTTP test successful")
                    else:
                        services["groq"] = "failed to get response"
                except Exception as e:
                    services["groq"] = f"failed: {str(e)[:50]}"
                    logger.error(f"❌ Groq test failed: {e}")
            else:
                services["groq"] = "not configured"
            
            success = primary is not None
            
            return {
                "success": success,
                "primary_service": primary,
                "services": services,
                "message": f"Primary: {primary}" if primary else "No AI services available"
            }
            
        except Exception as e:
            logger.error(f"AI test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "primary_service": None,
                "services": {}
            }
    
    async def generate_reddit_domain_content(
        self,
        domain: str,
        business_type: str,
        business_description: str = "",
        target_audience: str = "indian_users",
        language: str = "en",
        content_style: str = "engaging",
        test_mode: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate unique, human-like Reddit content using HTTP APIs - SEQUENTIAL FALLBACK"""
        
        try:
            logger.info(f"🚀 Generating content for {domain} domain using AI HTTP APIs")
            
            # Create unique prompt
            prompt = self._create_human_like_prompt(
                domain, business_type, business_description, 
                target_audience, content_style
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            # Try Mistral first (primary) - SEQUENTIAL not concurrent
            if self.mistral_available:
                try:
                    logger.info("🎯 Using Mistral AI HTTP API for content generation")
                    
                    content = await self._call_mistral_api(
                        messages,
                        max_tokens=600,
                        temperature=0.9,
                        top_p=0.95
                    )
                    
                    if content:
                        parsed = self._parse_content(content, domain, business_type)
                        
                        if parsed.get("title") and parsed.get("content"):
                            parsed["ai_service"] = "mistral"
                            parsed["success"] = True
                            logger.info(f"✅ Mistral generated {len(parsed['content'])} chars")
                            return parsed
                    
                except Exception as e:
                    logger.error(f"❌ Mistral generation failed: {e}")
            
            # Wait before trying Groq fallback
            await asyncio.sleep(2.0)
            
            # Fallback to Groq - SEQUENTIAL
            if self.groq_available:
                try:
                    logger.info("🔄 Using Groq AI HTTP API for content generation (fallback)")
                    
                    content = await self._call_groq_api(
                        messages,
                        max_tokens=600,
                        temperature=0.9,
                        top_p=0.95
                    )
                    
                    if content:
                        parsed = self._parse_content(content, domain, business_type)
                        
                        if parsed.get("title") and parsed.get("content"):
                            parsed["ai_service"] = "groq"
                            parsed["success"] = True
                            logger.info(f"✅ Groq generated {len(parsed['content'])} chars")
                            return parsed
                    
                except Exception as e:
                    logger.error(f"❌ Groq generation failed: {e}")
            
            # No AI services available
            logger.error("🚫 No AI services available for content generation")
            return {
                "success": False,
                "error": "No AI services configured",
                "title": "AI Configuration Error",
                "content": "AI services not properly configured. Check API keys.",
                "ai_service": "none"
            }
            
        except Exception as e:
            logger.error(f"💥 Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": "Generation Error",
                "content": f"Content generation failed: {str(e)}",
                "ai_service": "error"
            }
    
    def _create_human_like_prompt(
        self, 
        domain: str, 
        business_type: str, 
        business_description: str,
        target_audience: str,
        content_style: str
    ) -> str:
        """Create prompts that generate rule-compliant, human-like content"""
        
        # Get domain context
        context = self.domain_contexts.get(domain, {
            "topics": ["general advice", "tips", "experiences"],
            "audiences": ["users", "people interested"],
            "pain_points": ["common challenges", "daily issues"]
        })
        
        # Random elements for variety
        topic = random.choice(context["topics"])
        audience = random.choice(context["audiences"])
        pain_point = random.choice(context["pain_points"])
        style_opener = random.choice(self.content_styles[random.choice(list(self.content_styles.keys()))])
        
        # Subreddit-specific rules and guidelines
        subreddit_rules = {
            "education": """
            Educational subreddit rules:
            - NO direct promotion or advertising
            - Share genuine study experiences and tips
            - Focus on helping students, not selling services
            - Use clear, helpful language
            - Include practical advice that anyone can use
            - No "my coaching institute" mentions
            """,
            "tech": """
            Tech subreddit rules:
            - NO self-promotion without value
            - Share genuine technical insights
            - Focus on helping developers
            - Include code examples or practical tips
            - No company/service promotion
            - Ask technical questions that spark discussion
            """,
            "health": """
            Health subreddit rules:
            - NO medical advice or claims
            - Share personal fitness experiences only
            - Focus on lifestyle and motivation
            - No supplement or service promotion
            - Use disclaimers like "this worked for me"
            - Encourage consulting professionals
            """,
            "business": """
            Business subreddit rules:
            - NO direct business promotion
            - Share genuine business experiences
            - Focus on lessons learned, not success stories
            - Ask for community input and advice
            - No service selling or client hunting
            - Be humble and authentic
            """,
            "general": """
            General Reddit rules:
            - NO spam or self-promotion
            - Provide value first, always
            - Be authentic and conversational
            - Follow reddiquette guidelines
            """
        }
        
        rules = subreddit_rules.get(domain, subreddit_rules["general"])
        
        # Create rule-compliant prompt
        prompt = f"""Write a Reddit post that strictly follows subreddit rules and sounds genuinely human.

{rules}

Context:
- You're someone with experience in {domain}
- Topic focus: {topic}
- Audience: {audience}
- Common challenge: {pain_point}

CRITICAL REQUIREMENTS:
- NO business promotion whatsoever
- NO mentions of services, products, or companies
- Write as a regular person sharing experience
- Focus 100% on helping others
- Use casual, conversational tone
- Include personal struggles or learning moments
- Ask genuine questions to the community
- Be humble and relatable
- Length: 150-300 words
- Indian context is fine but subtle

Format your response as:
TITLE: [Helpful, non-promotional title - max 100 characters]

CONTENT: [Genuine, rule-compliant content that provides real value]

Examples of what NOT to do:
- "My coaching institute helps..."
- "Our service provides..."
- "Contact me for..."
- "Check out my..."

Examples of what TO do:
- "I struggled with... here's what helped"
- "Has anyone else noticed..."
- "What's your experience with..."
- "Here's something I learned..."

Write like you're genuinely helping the Reddit community, not promoting anything.
Current context: {datetime.now().strftime('%B %Y')}"""
        
        return prompt
    
    def _parse_content(self, ai_response: str, domain: str, business_type: str) -> Dict[str, Any]:
        """Parse AI response into structured content"""
        try:
            title = ""
            content = ""
            
            # Extract title and content
            lines = ai_response.strip().split('\n')
            
            for i, line in enumerate(lines):
                if line.upper().startswith('TITLE:'):
                    title = line[6:].strip().replace('"', '').replace("'", "")
                    break
            
            # Extract content after CONTENT: marker
            content_started = False
            content_lines = []
            
            for line in lines:
                if line.upper().startswith('CONTENT:'):
                    content_started = True
                    content_part = line[8:].strip()
                    if content_part:
                        content_lines.append(content_part)
                elif content_started and line.strip():
                    content_lines.append(line.strip())
            
            content = '\n\n'.join(content_lines) if content_lines else ""
            
            # Fallback parsing
            if not title or not content:
                paragraphs = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
                if paragraphs:
                    # Use first line/paragraph as title
                    potential_title = paragraphs[0].split('\n')[0]
                    title = potential_title[:100] if len(potential_title) > 10 else f"{business_type} Tips for {domain.title()}"
                    
                    # Use rest as content
                    if len(paragraphs) > 1:
                        content = '\n\n'.join(paragraphs[1:])
                    else:
                        content = paragraphs[0]
            
            # Ensure content quality
            if len(content.strip()) < 100:
                content += f"\n\nWhat's your experience with {domain}? Share your thoughts below!"
            
            # Clean up title
            if len(title) > 150:
                title = title[:147] + "..."
            
            return {
                "title": title,
                "content": content,
                "body": content,
                "word_count": len(content.split()),
                "character_count": len(content),
                "parsed_successfully": bool(title and content)
            }
            
        except Exception as e:
            logger.error(f"Content parsing failed: {e}")
            # Return the raw content if parsing fails
            return {
                "title": f"{business_type} - {domain.title()} Insights",
                "content": ai_response[:400] if ai_response else "Content generation failed",
                "body": ai_response[:400] if ai_response else "Content generation failed",
                "word_count": len(ai_response.split()) if ai_response else 0,
                "character_count": len(ai_response) if ai_response else 0,
                "parsed_successfully": False
            }
    
    async def generate_qa_answer(
        self,
        platform: str,
        question: str,
        domain: str = None,
        expertise_level: str = "intermediate",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate Q&A answers for auto-replies - SEQUENTIAL FALLBACK"""
        
        prompt = f"""Answer this {platform} question naturally and helpfully:

Question: {question}

Requirements:
- Write like a knowledgeable person, not a bot
- Provide practical, actionable advice
- Keep it 100-250 words
- Be conversational and friendly
- Include personal touch if relevant
- Don't be promotional
{f"- Focus on {domain} expertise" if domain else ""}

Write a helpful, human-like response that adds real value."""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            # Try Mistral first - SEQUENTIAL
            if self.mistral_available:
                answer = await self._call_mistral_api(
                    messages,
                    max_tokens=400,
                    temperature=0.8
                )
                
                if answer:
                    return {
                        "success": True,
                        "answer": answer,
                        "ai_service": "mistral",
                        "word_count": len(answer.split())
                    }
            
            # Wait before trying Groq
            await asyncio.sleep(2.0)
            
            # Fallback to Groq - SEQUENTIAL
            if self.groq_available:
                answer = await self._call_groq_api(
                    messages,
                    max_tokens=400,
                    temperature=0.8
                )
                
                if answer:
                    return {
                        "success": True,
                        "answer": answer,
                        "ai_service": "groq",
                        "word_count": len(answer.split())
                    }
            
            return {
                "success": False,
                "error": "No AI service available",
                "answer": "Unable to generate response - AI service not configured"
            }
            
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Error generating response"
            }