"""
Enhanced AI Service Module for Multi-Platform Content Generation
Real Mistral AI integration with Groq fallback for Reddit automation
NO DEMO DATA - Uses actual API calls for content generation
"""

import asyncio
import base64
import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
import random

# Import AI service clients
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    print("⚠️ Mistral AI client not available. Install: pip install mistralai")

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("⚠️ Groq client not available. Install: pip install groq")

logger = logging.getLogger(__name__)

class AIService:
    """Enhanced AI Service with real Mistral integration for Reddit automation"""
    
    def __init__(self):
        """Initialize AI service with real API clients"""
        
        # Get API keys from environment or config
        self.mistral_api_key = os.getenv("MISTRAL_API_KEY") or "your_mistral_api_key_here"
        self.groq_api_key = os.getenv("GROQ_API_KEY") or "your_groq_api_key_here"
        print(f"Mistral Key: {self.mistral_api_key[:4]}..., Groq Key: {self.groq_api_key[:4]}...")
        
        # Initialize clients
        self.mistral_client = None
        self.groq_client = None
        
        # Initialize Mistral client
        if MISTRAL_AVAILABLE and self.mistral_api_key and self.mistral_api_key != "your_mistral_api_key_here":
            try:
                self.mistral_client = MistralClient(api_key=self.mistral_api_key)
                logger.info("✅ Mistral AI client initialized")
            except Exception as e:
                logger.error(f"❌ Mistral AI initialization failed: {e}")
        
        # Initialize Groq client as fallback
        if GROQ_AVAILABLE and self.groq_api_key and self.groq_api_key != "your_groq_api_key_here":
            try:
                self.groq_client = Groq(api_key=self.groq_api_key)
                logger.info("✅ Groq AI client initialized")
            except Exception as e:
                logger.error(f"❌ Groq AI initialization failed: {e}")
        
        # Domain-specific subreddit mappings
        self.domain_subreddits = {
            "education": ["JEE", "NEET", "IndianStudents", "india", "StudyTips", "GetStudying"],
            "restaurant": ["IndianFood", "food", "FoodPorn", "recipes", "bangalore", "mumbai"],
            "technology": ["developersIndia", "programming", "coding", "tech", "india"],
            "health": ["fitness", "HealthyFood", "nutrition", "india", "HealthyEating"],
            "business": ["entrepreneur", "IndiaInvestments", "business", "startup", "india"]
        }
        
        # Content style templates
        self.style_prompts = {
            "engaging": "Write in a conversational, engaging tone that encourages discussion",
            "informative": "Write in a clear, educational tone with practical information",
            "promotional": "Write in a subtle promotional tone that provides value first",
            "helpful": "Write in a supportive, helpful tone like giving advice to a friend"
        }
    
    async def test_ai_connection(self) -> Dict[str, Any]:
        """Test AI service connections"""
        try:
            services = {}
            primary_service = None
            
            # Test Mistral
            if self.mistral_client:
                try:
                    # Test with a simple message
                    response = self.mistral_client.chat(
                        model="mistral-large-latest",
                        messages=[ChatMessage(role="user", content="Hello, test connection.")],
                        max_tokens=10
                    )
                    services["mistral"] = {"status": "connected", "response_length": len(response.choices[0].message.content)}
                    primary_service = "mistral"
                    logger.info("✅ Mistral AI test successful")
                except Exception as e:
                    services["mistral"] = {"status": "failed", "error": str(e)}
                    logger.error(f"❌ Mistral AI test failed: {e}")
            else:
                services["mistral"] = {"status": "not_configured", "error": "API key not set"}
            
            # Test Groq
            if self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": "Hello, test connection."}],
                        model="llama3-8b-8192",
                        max_tokens=10
                    )
                    services["groq"] = {"status": "connected", "response_length": len(response.choices[0].message.content)}
                    if not primary_service:
                        primary_service = "groq"
                    logger.info("✅ Groq AI test successful")
                except Exception as e:
                    services["groq"] = {"status": "failed", "error": str(e)}
                    logger.error(f"❌ Groq AI test failed: {e}")
            else:
                services["groq"] = {"status": "not_configured", "error": "API key not set"}
            
            success = any(service.get("status") == "connected" for service in services.values())
            
            return {
                "success": success,
                "primary_service": primary_service,
                "services": services,
                "message": f"Primary service: {primary_service}" if primary_service else "No AI services available"
            }
            
        except Exception as e:
            logger.error(f"AI connection test failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "services": {},
                "primary_service": None
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
        """Generate domain-specific Reddit content using real AI"""
        
        try:
            # Create comprehensive prompt for the domain
            prompt = self._create_reddit_content_prompt(
                domain=domain,
                business_type=business_type,
                business_description=business_description,
                target_audience=target_audience,
                language=language,
                content_style=content_style,
                test_mode=test_mode
            )
            
            # Try Mistral first
            if self.mistral_client:
                try:
                    logger.info("🔄 Generating content using Mistral AI...")
                    
                    response = self.mistral_client.chat(
                        model="mistral-large-latest",
                        messages=[ChatMessage(role="user", content=prompt)],
                        max_tokens=800,
                        temperature=0.8
                    )
                    
                    content = response.choices[0].message.content.strip()
                    parsed_content = self._parse_reddit_content(content)
                    
                    if parsed_content.get("title") and parsed_content.get("content"):
                        parsed_content["ai_service"] = "mistral"
                        parsed_content["success"] = True
                        logger.info(f"✅ Mistral generated {len(parsed_content['content'])} characters")
                        return parsed_content
                    
                except Exception as e:
                    logger.error(f"❌ Mistral generation failed: {e}")
            
            # Fallback to Groq
            if self.groq_client:
                try:
                    logger.info("🔄 Falling back to Groq AI...")
                    
                    response = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-70b-8192",
                        max_tokens=800,
                        temperature=0.8
                    )
                    
                    content = response.choices[0].message.content.strip()
                    parsed_content = self._parse_reddit_content(content)
                    
                    if parsed_content.get("title") and parsed_content.get("content"):
                        parsed_content["ai_service"] = "groq"
                        parsed_content["success"] = True
                        logger.info(f"✅ Groq generated {len(parsed_content['content'])} characters")
                        return parsed_content
                    
                except Exception as e:
                    logger.error(f"❌ Groq generation failed: {e}")
            
            # If all AI services fail
            return {
                "success": False,
                "error": "All AI services failed or not configured",
                "title": "AI Service Unavailable",
                "content": "Please configure your Mistral or Groq API keys to generate content.",
                "ai_service": "none"
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "title": "Content Generation Error",
                "content": f"Error occurred: {str(e)}",
                "ai_service": "error"
            }
    
    def _create_reddit_content_prompt(
        self,
        domain: str,
        business_type: str,
        business_description: str,
        target_audience: str,
        language: str,
        content_style: str,
        test_mode: bool = False
    ) -> str:
        """Create comprehensive prompts for Reddit content generation"""
        
        # Base context
        audience_context = {
            "indian_students": "Indian students preparing for competitive exams like JEE, NEET, and other entrance exams",
            "indian_users": "Indian users interested in practical solutions and local insights",
            "tech_professionals": "Technology professionals and developers in India",
            "food_lovers": "Food enthusiasts and people interested in Indian cuisine",
            "health_conscious": "Health-conscious individuals looking for fitness and nutrition advice"
        }.get(target_audience, "General Indian audience")
        
        style_instruction = self.style_prompts.get(content_style, "Write in an engaging, conversational tone")
        
        # Domain-specific content requirements
        domain_instructions = {
            "education": f"""
            Create educational content about {business_type}. Focus on:
            - Study tips and strategies
            - Exam preparation advice
            - Career guidance
            - Success stories or motivation
            - Practical learning techniques
            Target subreddits like r/JEE, r/NEET, r/IndianStudents
            """,
            "restaurant": f"""
            Create food and restaurant content about {business_type}. Focus on:
            - Food recommendations and reviews
            - Cooking tips and recipes
            - Restaurant experiences
            - Food culture and traditions
            - Health and nutrition aspects
            Target subreddits like r/IndianFood, r/food, r/recipes
            """,
            "technology": f"""
            Create technology content about {business_type}. Focus on:
            - Technical tips and tutorials
            - Career advice in tech
            - Tool recommendations
            - Industry insights
            - Programming and development
            Target subreddits like r/developersIndia, r/programming
            """,
            "health": f"""
            Create health and fitness content about {business_type}. Focus on:
            - Fitness tips and workout routines
            - Nutrition advice
            - Health awareness
            - Wellness strategies
            - Lifestyle improvements
            Target subreddits like r/fitness, r/HealthyFood
            """,
            "business": f"""
            Create business content about {business_type}. Focus on:
            - Business advice and strategies
            - Entrepreneurship tips
            - Investment insights
            - Success stories
            - Market analysis
            Target subreddits like r/entrepreneur, r/IndiaInvestments
            """
        }.get(domain, f"Create engaging content about {business_type}")
        
        test_indicator = "[TEST MODE] " if test_mode else ""
        
        prompt = f"""
        {test_indicator}Create a Reddit post for {audience_context}.

        Business: {business_type}
        {f"Description: {business_description}" if business_description else ""}
        Domain: {domain}
        Style: {style_instruction}

        {domain_instructions}

        Requirements:
        1. Write for Indian context and audience
        2. Make it authentic and valuable, not promotional
        3. Use a natural, conversational tone
        4. Include practical tips or insights
        5. Make it engaging to encourage comments
        6. Keep title under 150 characters
        7. Keep content between 150-400 words
        
        Format your response exactly as:
        
        TITLE: [Your engaging title here]
        
        CONTENT: [Your detailed post content here]
        
        Make sure the content provides real value and doesn't sound like an advertisement.
        """
        
        return prompt
    
    def _parse_reddit_content(self, ai_response: str) -> Dict[str, Any]:
        """Parse AI response into title and content"""
        try:
            lines = ai_response.strip().split('\n')
            title = ""
            content = ""
            
            # Find title
            for line in lines:
                if line.upper().startswith('TITLE:'):
                    title = line[6:].strip()
                    break
            
            # Find content
            content_started = False
            content_lines = []
            
            for line in lines:
                if line.upper().startswith('CONTENT:'):
                    content_started = True
                    content_line = line[8:].strip()
                    if content_line:
                        content_lines.append(content_line)
                elif content_started and line.strip():
                    content_lines.append(line.strip())
            
            content = '\n\n'.join(content_lines)
            
            # Fallback parsing if structured format not found
            if not title or not content:
                paragraphs = [p.strip() for p in ai_response.split('\n\n') if p.strip()]
                if len(paragraphs) >= 2:
                    title = paragraphs[0][:150]  # First paragraph as title
                    content = '\n\n'.join(paragraphs[1:])  # Rest as content
                elif len(paragraphs) == 1:
                    # Single paragraph - create title and content
                    full_text = paragraphs[0]
                    if len(full_text) > 100:
                        title = full_text[:80] + "..."
                        content = full_text
                    else:
                        title = full_text
                        content = full_text
            
            # Clean up title (remove quotes, extra formatting)
            title = title.replace('"', '').replace("'", "").strip()
            
            # Ensure minimum content length
            if len(content.strip()) < 50:
                content += f"\n\nWhat are your thoughts on this? Have you had similar experiences?\n\nFeel free to share your insights in the comments!"
            
            return {
                "title": title,
                "content": content,
                "body": content,  # For backward compatibility
                "word_count": len(content.split()),
                "character_count": len(content),
                "parsed_successfully": bool(title and content)
            }
            
        except Exception as e:
            logger.error(f"Content parsing failed: {e}")
            return {
                "title": "AI Generated Content",
                "content": ai_response[:500] if ai_response else "Content generation failed",
                "body": ai_response[:500] if ai_response else "Content generation failed",
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
        language: str = "en",
        context: Dict[str, Any] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate Q&A answers for auto-replies"""
        
        try:
            context = context or {}
            
            # Create Q&A prompt
            prompt = f"""
            Answer this {platform} question with expertise level: {expertise_level}
            
            Question: {question}
            
            Requirements:
            1. Provide a helpful, accurate answer
            2. Use a friendly, knowledgeable tone
            3. Include practical tips if relevant
            4. Keep response between 100-300 words
            5. Make it valuable to the person asking
            6. Don't be promotional or salesy
            {f"7. Focus on {domain} domain knowledge" if domain else ""}
            
            Context: {json.dumps(context) if context else "None"}
            
            Write a natural, helpful response that adds value to the discussion.
            """
            
            # Try Mistral first
            if self.mistral_client:
                try:
                    response = self.mistral_client.chat(
                        model="mistral-large-latest",
                        messages=[ChatMessage(role="user", content=prompt)],
                        max_tokens=400,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    return {
                        "success": True,
                        "answer": answer,
                        "ai_service": "mistral",
                        "word_count": len(answer.split()),
                        "character_count": len(answer)
                    }
                    
                except Exception as e:
                    logger.error(f"Mistral Q&A generation failed: {e}")
            
            # Fallback to Groq
            if self.groq_client:
                try:
                    response = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama3-70b-8192",
                        max_tokens=400,
                        temperature=0.7
                    )
                    
                    answer = response.choices[0].message.content.strip()
                    
                    return {
                        "success": True,
                        "answer": answer,
                        "ai_service": "groq",
                        "word_count": len(answer.split()),
                        "character_count": len(answer)
                    }
                    
                except Exception as e:
                    logger.error(f"Groq Q&A generation failed: {e}")
            
            return {
                "success": False,
                "error": "No AI service available for Q&A generation",
                "answer": "I'd be happy to help, but I'm unable to generate a response right now."
            }
            
        except Exception as e:
            logger.error(f"Q&A generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "answer": "Sorry, I encountered an error while generating the response."
            }
    
    async def analyze_content_performance(self, content: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze content performance for optimization"""
        # This would be implemented for analytics features
        return {"success": True, "analysis": "Performance analysis not implemented yet"}
    
    def get_recommended_subreddits(self, domain: str) -> List[str]:
        """Get recommended subreddits for a domain"""
        return self.domain_subreddits.get(domain, ["india", "AskReddit"])
    
    def get_content_suggestions(self, domain: str, recent_posts: List[Dict]) -> List[str]:
        """Get content suggestions based on domain and recent posts"""
        # This would analyze recent posts and suggest new content ideas
        base_suggestions = {
            "education": [
                "Study tips for competitive exams",
                "Time management strategies",
                "Motivation and success stories",
                "Career guidance posts",
                "Learning technique tutorials"
            ],
            "restaurant": [
                "Recipe sharing and cooking tips",
                "Restaurant reviews and recommendations", 
                "Food culture discussions",
                "Healthy eating advice",
                "Local cuisine spotlights"
            ],
            "technology": [
                "Programming tutorials and tips",
                "Career advice for developers",
                "Tool and technology reviews",
                "Industry trend discussions",
                "Project showcases"
            ],
            "health": [
                "Fitness routines and exercises",
                "Nutrition advice and meal planning",
                "Mental health and wellness",
                "Health myth busting",
                "Lifestyle improvement tips"
            ],
            "business": [
                "Entrepreneurship advice",
                "Business strategy discussions",
                "Investment insights",
                "Success story sharing",
                "Market analysis posts"
            ]
        }
        
        return base_suggestions.get(domain, ["General tips and advice", "Ask Me Anything posts", "Discussion starters"])