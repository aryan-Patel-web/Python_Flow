"""
Human-like AI Service - Natural Reddit Content Generation
Generates authentic, conversational content that passes human detection
No formatting, lists, or obvious AI patterns
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
    """Human-like AI Service for authentic Reddit content"""
    
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
        self.mistral_semaphore = asyncio.Semaphore(3)
        self.groq_semaphore = asyncio.Semaphore(2)
        self.mistral_last_request = 0
        self.groq_last_request = 0
        self.min_request_interval = 3.0
        
        # Enhanced model configurations
        self.mistral_models = [
            "mistral-small-latest",
            "mistral-medium-latest",
            "open-mistral-7b"
        ]
        
        self.groq_models = [
            "llama-3.1-8b-instant",
            "llama3-70b-8192",
            "mixtral-8x7b-32768"
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
        
        # Natural conversation starters and patterns
        self.natural_starters = [
            "So I've been thinking about",
            "Anyone else notice that",
            "This might sound weird but",
            "Not sure if this is just me but",
            "Been dealing with this lately and",
            "Quick question for everyone here",
            "Maybe I'm overthinking this but",
            "Had this experience recently and",
            "Probably a dumb question but",
            "Just realized something about"
        ]
        
        self.casual_connectors = [
            "but honestly", "like", "idk", "tbh", "basically", "anyway", 
            "so yeah", "also", "btw", "i mean", "right?", "you know"
        ]
        
        self.human_quirks = [
            "edit: typo", "sorry for rambling", "hope this makes sense",
            "correct me if im wrong", "not an expert but", "just my 2 cents",
            "might be completely off here", "take this with a grain of salt"
        ]
        
        # Common typos and casual writing patterns
        self.casual_replacements = {
            "you": ["u", "you"],
            "are": ["r", "are"], 
            "because": ["bc", "cuz", "because"],
            "probably": ["prob", "probably"],
            "definitely": ["def", "definitely"],
            "really": ["rly", "really"],
            "something": ["smth", "something"],
            "someone": ["someone", "sb"],
            "though": ["tho", "though"],
            "through": ["thru", "through"]
        }
        
        # Domain-specific authentic experiences
        self.domain_contexts = {
            "education": {
                "real_struggles": [
                    "cant concentrate for more than 20 mins",
                    "feeling behind compared to classmates", 
                    "parents keep asking about marks",
                    "coaching classes are so expensive",
                    "online vs offline classes confusion"
                ],
                "casual_mentions": [
                    "my friend told me", "saw this on youtube", "teacher mentioned",
                    "read somewhere that", "cousin who's in college said"
                ]
            },
            "tech": {
                "real_struggles": [
                    "impostor syndrome is real", 
                    "tutorial hell is a thing",
                    "stack overflow copy paste guilt",
                    "job market feels impossible",
                    "everyone seems smarter than me"
                ],
                "casual_mentions": [
                    "saw on twitter", "colleague mentioned", "read on medium",
                    "some guy on youtube said", "friend who works at"
                ]
            },
            "health": {
                "real_struggles": [
                    "motivation dies after 2 weeks",
                    "healthy food is so expensive", 
                    "gym feels intimidating",
                    "work schedule kills workout plans",
                    "family doesnt understand diet changes"
                ],
                "casual_mentions": [
                    "doctor said", "friend who's into fitness", "saw on instagram",
                    "my sister tries", "colleague at work"
                ]
            },
            "business": {
                "real_struggles": [
                    "clients always want discounts",
                    "cash flow is unpredictable",
                    "competition is everywhere",
                    "marketing feels like throwing money away",
                    "work life balance doesnt exist"
                ],
                "casual_mentions": [
                    "mentor told me", "read in some blog", "customer feedback",
                    "business partner thinks", "accountant suggested"
                ]
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
        
        async with self.mistral_semaphore:
            await self._wait_for_rate_limit("mistral")
            
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
                    
                    timeout_duration = 45.0 + (model_idx * 15.0)
                    
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
                                await asyncio.sleep(5.0)
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
        
        async with self.groq_semaphore:
            await self._wait_for_rate_limit("groq")
            
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
                    
                    timeout_duration = 45.0 + (model_idx * 15.0)
                    
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
                            try:
                                error_data = response.json()
                                error_msg = error_data.get("error", {}).get("message", "")
                                if "Please try again in" in error_msg:
                                    import re
                                    match = re.search(r'(\d+(?:\.\d+)?)ms', error_msg)
                                    if match:
                                        wait_ms = float(match.group(1))
                                        wait_time = (wait_ms / 1000.0) + 2.0
                                        logger.info(f"Groq suggested wait: {wait_time:.1f}s")
                                        await asyncio.sleep(min(wait_time, 10.0))
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
        """Test AI service connections"""
        try:
            services = {}
            primary = None
            
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
            
            await asyncio.sleep(2.0)
            
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
    
    def _create_human_like_prompt(
        self, 
        domain: str, 
        business_type: str, 
        business_description: str,
        target_audience: str,
        content_style: str
    ) -> str:
        """Create prompts for authentic, human-like Reddit content"""
        
        context = self.domain_contexts.get(domain, {
            "real_struggles": ["daily challenges", "common issues"],
            "casual_mentions": ["friend said", "read somewhere"]
        })
        
        struggle = random.choice(context["real_struggles"])
        mention = random.choice(context["casual_mentions"])
        starter = random.choice(self.natural_starters)
        
        prompt = f"""Write a completely natural Reddit post that sounds like a real person sharing their genuine experience. This is for r/{domain} community.

CRITICAL: This must pass human detection and subreddit rules. 

Writing style requirements:
- Write like you're typing on your phone casually
- Use lowercase sometimes, normal capitalization other times  
- Include natural typos (but not too many)
- Use casual words like "tbh", "idk", "bc", "u", "rly"
- NO bullet points, numbered lists, or formatting
- NO bold text, asterisks, or markdown
- Sound conversational, not formal
- Include natural pauses with "..." sometimes
- Use "edit:" if you want to add something
- Make small grammar mistakes occasionally 

Content requirements:
- Share a real personal struggle: {struggle}
- Mention learning from: {mention}
- NO promotion, business mentions, or services
- Ask genuine questions to the community
- Include vulnerable moments or confusion
- Sound relatable and human
- Length: 150-300 words total
- Context: {domain} community

Subreddit rules to follow:
- No self-promotion whatsoever
- Provide value through sharing experience
- Be authentic and conversational  
- Ask for community input
- Follow reddiquette

Format should be:
A natural title (not "TITLE:" - just write the title)
[blank line]
The post content in conversational paragraphs

Examples of natural writing:
"idk if this is just me but i've been struggling with..."
"anyone else feel like..."
"prob a dumb question but..."
"edit: spelling"
"this might sound weird but..."

Make it sound like someone genuinely asking for help or sharing experience, not like marketing content or AI writing.

Current context: Regular person sharing on Reddit in {datetime.now().strftime('%B %Y')}"""
        
        return prompt
    
    def _make_content_natural(self, content: str) -> str:
        """Make content more human-like with casual language and minor imperfections"""
        
        # Apply casual replacements randomly
        words = content.split()
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?')
            if word_lower in self.casual_replacements and random.random() < 0.3:
                replacement_options = self.casual_replacements[word_lower]
                words[i] = word.replace(word_lower, random.choice(replacement_options))
        
        content = ' '.join(words)
        
        # Add casual connectors randomly
        if random.random() < 0.4:
            connector = random.choice(self.casual_connectors)
            sentences = content.split('. ')
            if len(sentences) > 1:
                insert_pos = random.randint(1, len(sentences) - 1)
                sentences[insert_pos] = connector + ' ' + sentences[insert_pos]
                content = '. '.join(sentences)
        
        # Occasionally add human quirks
        if random.random() < 0.3:
            quirk = random.choice(self.human_quirks)
            content += f"\n\n{quirk}"
        
        # Random capitalization changes (but not too many)
        if random.random() < 0.2:
            content = content.replace('I ', 'i ')
        
        # Remove obvious AI formatting
        content = content.replace('**', '')
        content = content.replace('###', '')
        content = content.replace('####', '')
        content = content.replace('- ', '')
        content = content.replace('* ', '')
        
        # Replace numbered lists with natural flow
        import re
        content = re.sub(r'\d+\.\s*', '', content)
        
        return content
    
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
        """Generate authentic, human-like Reddit content"""
        
        try:
            logger.info(f"🚀 Generating natural content for {domain} domain")
            
            prompt = self._create_human_like_prompt(
                domain, business_type, business_description, 
                target_audience, content_style
            )
            
            messages = [{"role": "user", "content": prompt}]
            
            # Try Mistral first
            if self.mistral_available:
                try:
                    logger.info("🎯 Using Mistral AI for natural content generation")
                    
                    content = await self._call_mistral_api(
                        messages,
                        max_tokens=600,
                        temperature=1.1,  # Higher temperature for more natural variation
                        top_p=0.92
                    )
                    
                    if content:
                        parsed = self._parse_natural_content(content, domain, business_type)
                        
                        if parsed.get("title") and parsed.get("content"):
                            parsed["ai_service"] = "mistral"
                            parsed["success"] = True
                            logger.info(f"✅ Mistral generated natural content: {len(parsed['content'])} chars")
                            return parsed
                    
                except Exception as e:
                    logger.error(f"❌ Mistral generation failed: {e}")
            
            await asyncio.sleep(2.0)
            
            # Fallback to Groq
            if self.groq_available:
                try:
                    logger.info("🔄 Using Groq AI for natural content generation")
                    
                    content = await self._call_groq_api(
                        messages,
                        max_tokens=600,
                        temperature=1.1,
                        top_p=0.92
                    )
                    
                    if content:
                        parsed = self._parse_natural_content(content, domain, business_type)
                        
                        if parsed.get("title") and parsed.get("content"):
                            parsed["ai_service"] = "groq"
                            parsed["success"] = True
                            logger.info(f"✅ Groq generated natural content: {len(parsed['content'])} chars")
                            return parsed
                    
                except Exception as e:
                    logger.error(f"❌ Groq generation failed: {e}")
            
            logger.error("🚫 No AI services available for content generation")
            return {
                "success": False,
                "error": "No AI services configured",
                "title": "Need help with something",
                "content": "anyone else dealing with similar issues? would love to hear your thoughts",
                "ai_service": "none"
            }
            
        except Exception as e:
            logger.error(f"💥 Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": "having some issues here",
                "content": f"been struggling with this and wondering if anyone has similar experience",
                "ai_service": "error"
            }
    
    def _parse_natural_content(self, ai_response: str, domain: str, business_type: str) -> Dict[str, Any]:
        """Parse AI response but keep it natural and unformatted"""
        try:
            # Split into lines
            lines = [line.strip() for line in ai_response.strip().split('\n') if line.strip()]
            
            if not lines:
                return self._create_fallback_content(domain, business_type)
            
            # First line is usually the title
            title = lines[0]
            
            # Rest is content
            content_lines = lines[1:] if len(lines) > 1 else [title]
            content = '\n\n'.join(content_lines)
            
            # Clean up any remaining formatting
            title = self._clean_title(title)
            content = self._make_content_natural(content)
            
            # Ensure minimum length
            if len(content.strip()) < 80:
                extra = f"\n\nanyone else dealing with this? would love to hear your thoughts or experiences"
                content += extra
            
            return {
                "title": title,
                "content": content,
                "body": content,
                "word_count": len(content.split()),
                "character_count": len(content),
                "parsed_successfully": True
            }
            
        except Exception as e:
            logger.error(f"Natural content parsing failed: {e}")
            return self._create_fallback_content(domain, business_type)
    
    def _clean_title(self, title: str) -> str:
        """Clean title to make it natural"""
        # Remove obvious AI patterns
        title = title.replace('TITLE:', '').replace('Title:', '').strip()
        title = title.replace('**', '').replace('###', '').strip()
        title = title.replace('"', '').replace("'", "").strip()
        
        # Ensure reasonable length
        if len(title) > 200:
            title = title[:197] + "..."
        
        # Make slightly more casual
        if random.random() < 0.3:
            title = title.lower()
        
        return title
    
    def _create_fallback_content(self, domain: str, business_type: str) -> Dict[str, Any]:
        """Create fallback content when parsing fails"""
        starters = [
            f"been thinking about {domain} stuff lately",
            f"anyone else struggling with {domain} things?",
            f"quick question about {domain}",
            f"not sure if this is the right place but",
            f"maybe dumb question but"
        ]
        
        title = random.choice(starters)
        content = f"idk if this makes sense but i've been dealing with some {domain} related stuff and wondering if anyone has experience with this kind of thing\n\nwould appreciate any thoughts or advice"
        
        return {
            "title": title,
            "content": content,
            "body": content,
            "word_count": len(content.split()),
            "character_count": len(content),
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
        """Generate natural Q&A answers"""
        
        prompt = f"""Answer this {platform} question in a completely natural, human way:

Question: {question}

Write like a real person responding, not an AI:
- Use casual language and natural flow
- Include personal touches like "in my experience" or "i've found that"
- Make it conversational, not formal
- 100-200 words max
- Sound helpful but humble
- Use lowercase sometimes, normal grammar other times
- NO bullet points or formatting
{f"- Draw from {domain} knowledge but don't sound like a textbook" if domain else ""}

Write like you're genuinely trying to help someone, not like you're writing content."""
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            if self.mistral_available:
                answer = await self._call_mistral_api(
                    messages,
                    max_tokens=300,
                    temperature=1.0
                )
                
                if answer:
                    natural_answer = self._make_content_natural(answer)
                    return {
                        "success": True,
                        "answer": natural_answer,
                        "ai_service": "mistral",
                        "word_count": len(natural_answer.split())
                    }
            
            await asyncio.sleep(2.0)
            
            if self.groq_available:
                answer = await self._call_groq_api(
                    messages,
                    max_tokens=300,
                    temperature=1.0
                )
                
                if answer:
                    natural_answer = self._make_content_natural(answer)
                    return {
                        "success": True,
                        "answer": natural_answer,
                        "ai_service": "groq",
                        "word_count": len(natural_answer.split())
                    }
            
            return {
                "success": False,
                "error": "No AI service available",
                "answer": "sorry cant help with this right now"
            }
            
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "having some technical issues, sorry"
            }