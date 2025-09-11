"""
AI Service Module for Multi-Platform Content Generation
Handles Mistral AI, Groq fallback, voice processing, and platform-specific prompts
"""

import asyncio
import base64
import io
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import re

# AI Service imports
try:
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
except ImportError:
    MistralClient = None
    ChatMessage = None

try:
    from groq import Groq
except ImportError:
    Groq = None

# Voice processing imports
try:
    import speech_recognition as sr
    from gtts import gTTS
    import pyttsx3
    from pydub import AudioSegment
except ImportError:
    sr = None
    gTTS = None
    pyttsx3 = None
    AudioSegment = None

# Language detection
try:
    from langdetect import detect, LangDetectError
    from googletrans import Translator
except ImportError:
    detect = None
    LangDetectError = None
    Translator = None

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class AIService:
    """
    Production-ready AI service with Mistral primary, Groq fallback,
    platform-specific prompts, and voice processing capabilities
    """
    
    def __init__(self):
        """Initialize AI service with multiple providers"""
        self.mistral_client = None
        self.groq_client = None
        self.translator = None
        self.voice_engine = None
        
        # Initialize Mistral AI
        if settings.mistral_api_key and MistralClient:
            try:
                self.mistral_client = MistralClient(api_key=settings.mistral_api_key)
                logger.info("Mistral AI client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Mistral AI: {e}")
        
        # Initialize Groq as fallback
        if settings.groq_api_key and Groq:
            try:
                self.groq_client = Groq(api_key=settings.groq_api_key)
                logger.info("Groq client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
        
        # Initialize translator
        if Translator:
            try:
                self.translator = Translator()
                logger.info("Google Translator initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize translator: {e}")
        
        # Initialize voice engine
        if pyttsx3:
            try:
                self.voice_engine = pyttsx3.init()
                self.voice_engine.setProperty('rate', 150)  # Speed
                self.voice_engine.setProperty('volume', 0.9)  # Volume
                logger.info("Voice engine initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize voice engine: {e}")
        
        # Platform-specific prompts - FIXED: Added missing _get_reddit_answer_prompt
        self.platform_prompts = {
            "reddit": {
                "post": self._get_reddit_post_prompt,
                "comment": self._get_reddit_comment_prompt,
                "answer": self._get_reddit_answer_prompt  # This was missing - FIXED
            },
            "twitter": {
                "tweet": self._get_twitter_tweet_prompt,
                "thread": self._get_twitter_thread_prompt,
                "reply": self._get_twitter_reply_prompt
            },
            "stackoverflow": {
                "answer": self._get_stackoverflow_answer_prompt,
                "question": self._get_stackoverflow_question_prompt
            },
            "webmd": {
                "answer": self._get_webmd_answer_prompt,
                "advice": self._get_webmd_advice_prompt
            }
        }
        
        # Domain-specific content templates for Indian businesses
        self.domain_templates = {
            "education": {
                "reddit_subreddits": ["india", "JEE", "NEET", "IndianStudents", "StudyTips", "AskIndia"],
                "content_themes": ["exam_preparation", "study_tips", "career_guidance", "course_recommendations"],
                "keywords": ["JEE", "NEET", "board_exams", "competitive_exams", "study_abroad", "engineering", "medical"]
            },
            "restaurant": {
                "reddit_subreddits": ["india", "bangalore", "mumbai", "delhi", "food", "IndianFood", "pune"],
                "content_themes": ["food_reviews", "recipe_sharing", "restaurant_updates", "local_cuisine"],
                "keywords": ["indian_food", "street_food", "home_delivery", "restaurant", "recipe", "spices"]
            },
            "tech": {
                "reddit_subreddits": ["india", "bangalore", "developersIndia", "programming", "coding", "IndianStartups"],
                "content_themes": ["tech_tutorials", "job_market", "startup_news", "programming_tips"],
                "keywords": ["programming", "software", "development", "startup", "tech_jobs", "coding"]
            },
            "health": {
                "reddit_subreddits": ["india", "fitness", "HealthyFood", "mentalhealth", "AskDocs"],
                "content_themes": ["health_tips", "fitness_advice", "nutrition", "mental_wellness"],
                "keywords": ["health", "fitness", "yoga", "ayurveda", "nutrition", "wellness", "exercise"]
            },
            "business": {
                "reddit_subreddits": ["india", "entrepreneur", "IndiaInvestments", "business", "IndianStartups"],
                "content_themes": ["business_tips", "investment_advice", "startup_stories", "market_insights"],
                "keywords": ["business", "entrepreneur", "investment", "startup", "finance", "marketing"]
            }
        }
    
    async def generate_platform_content(
        self,
        platform: str,
        content_type: str,
        topic: str,
        tone: str = "professional",
        language: str = "en",
        target_audience: str = "general",
        additional_context: str = "",
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Generate platform-specific content using AI with domain expertise
        
        Args:
            platform: Target platform (reddit, twitter, stackoverflow, webmd)
            content_type: Type of content (post, comment, answer, etc.)
            topic: Content topic
            tone: Content tone (professional, casual, friendly, etc.)
            language: Target language
            target_audience: Target audience description
            additional_context: Additional context or requirements
            domain: Business domain (education, restaurant, tech, health, business)
            
        Returns:
            Dictionary containing generated content and metadata
        """
        try:
            # Get platform-specific prompt
            prompt_generator = self.platform_prompts.get(platform, {}).get(content_type)
            if not prompt_generator:
                raise ValueError(f"Unsupported platform/content_type: {platform}/{content_type}")
            
            # Generate prompt with domain context
            prompt = prompt_generator(
                topic=topic,
                tone=tone,
                language=language,
                target_audience=target_audience,
                additional_context=additional_context,
                domain=domain
            )
            
            # Generate content using AI
            content = await self._generate_with_fallback(prompt, platform, language)
            
            # Post-process content
            processed_content = self._post_process_content(content, platform, language, domain)
            
            return {
                "success": True,
                "content": processed_content,
                "platform": platform,
                "content_type": content_type,
                "language": language,
                "domain": domain,
                "word_count": len(processed_content.split()),
                "character_count": len(processed_content),
                "generated_at": datetime.now().isoformat(),
                "message": "Content generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate content"
            }
    
    async def generate_reddit_domain_content(
        self,
        domain: str,
        business_type: str,
        target_audience: str = "indian_users",
        language: str = "en",
        content_style: str = "engaging"
    ) -> Dict[str, Any]:
        """
        Generate domain-specific Reddit content for Indian businesses
        
        Args:
            domain: Business domain (education, restaurant, tech, health, business)
            business_type: Specific business type within domain
            target_audience: Target audience specification
            language: Content language
            content_style: Style of content (engaging, informative, promotional)
            
        Returns:
            Dictionary containing generated Reddit content
        """
        try:
            domain_config = self.domain_templates.get(domain, {})
            if not domain_config:
                raise ValueError(f"Unsupported domain: {domain}")
            
            # Create domain-specific prompt
            prompt = f"""
            Create engaging Reddit content for a {business_type} in the {domain} sector targeting {target_audience}.
            
            Domain Context: {domain}
            Business Type: {business_type}
            Target Audience: {target_audience}
            Language: {language}
            Content Style: {content_style}
            
            Requirements:
            - Create both a compelling title and body content
            - Make it relevant to Indian market and culture
            - Include appropriate keywords: {', '.join(domain_config.get('keywords', []))}
            - Suitable for subreddits: {', '.join(domain_config.get('reddit_subreddits', []))}
            - Tone should be helpful and authentic, not overly promotional
            - Include call-to-action that encourages discussion
            - Consider regional preferences and cultural nuances
            
            Content Themes to consider: {', '.join(domain_config.get('content_themes', []))}
            
            Format as:
            TITLE: [Engaging Reddit post title]
            BODY: [Main post content with appropriate formatting]
            SUGGESTED_SUBREDDITS: [Best subreddits for this content]
            """
            
            content = await self._generate_with_fallback(prompt, "reddit", language)
            
            # Parse the generated content
            parsed_content = self._parse_reddit_content(content)
            
            return {
                "success": True,
                "title": parsed_content.get("title", ""),
                "body": parsed_content.get("body", ""),
                "suggested_subreddits": parsed_content.get("subreddits", domain_config.get('reddit_subreddits', [])),
                "domain": domain,
                "business_type": business_type,
                "language": language,
                "keywords": domain_config.get('keywords', []),
                "generated_at": datetime.now().isoformat(),
                "message": "Domain-specific Reddit content generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Reddit domain content generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate Reddit domain content"
            }
    
    async def generate_qa_answer(
        self,
        platform: str,
        question: str,
        context: str = "",
        language: str = "en",
        expertise_level: str = "intermediate",
        domain: str = None
    ) -> Dict[str, Any]:
        """
        Generate Q&A answer for educational platforms with domain expertise
        
        Args:
            platform: Platform name (stackoverflow, webmd, reddit)
            question: Question text
            context: Additional context about the question
            language: Response language
            expertise_level: Level of technical detail (beginner, intermediate, advanced)
            domain: Business domain for specialized answers
            
        Returns:
            Dictionary containing generated answer
        """
        try:
            # Create specialized Q&A prompt with domain context
            prompt = self._get_qa_prompt(
                platform=platform,
                question=question,
                context=context,
                language=language,
                expertise_level=expertise_level,
                domain=domain
            )
            
            # Generate answer
            answer = await self._generate_with_fallback(prompt, platform, language)
            
            # Add platform-specific formatting and disclaimers
            formatted_answer = self._format_qa_answer(answer, platform, language, domain)
            
            return {
                "success": True,
                "answer": formatted_answer,
                "platform": platform,
                "language": language,
                "expertise_level": expertise_level,
                "domain": domain,
                "word_count": len(formatted_answer.split()),
                "generated_at": datetime.now().isoformat(),
                "message": "Answer generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Q&A answer generation failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate answer"
            }
    
    async def monitor_and_reply_questions(
        self,
        domain: str,
        subreddits: List[str],
        keywords: List[str],
        user_expertise: str,
        language: str = "en",
        max_replies: int = 5
    ) -> Dict[str, Any]:
        """
        Monitor Reddit questions and generate domain-specific replies
        
        Args:
            domain: User's domain expertise
            subreddits: Subreddits to monitor
            keywords: Keywords to filter questions
            user_expertise: User's expertise level in domain
            language: Reply language
            max_replies: Maximum number of replies to generate
            
        Returns:
            Dictionary containing generated replies
        """
        try:
            # This would integrate with your Reddit monitoring functionality
            # For now, providing the structure for generating replies
            
            generated_replies = []
            
            # Simulate finding relevant questions (integrate with actual Reddit monitoring)
            sample_questions = [
                {
                    "id": "sample_1",
                    "title": "Best way to prepare for JEE Main?",
                    "content": "I'm in 12th grade and need guidance on JEE preparation strategy.",
                    "subreddit": "JEE",
                    "score": 15,
                    "num_comments": 3
                }
            ]
            
            for question in sample_questions[:max_replies]:
                # Generate domain-specific reply
                reply_prompt = f"""
                As an expert in {domain}, provide a helpful answer to this question:
                
                Question: {question['title']}
                Context: {question['content']}
                Subreddit: r/{question['subreddit']}
                
                Your expertise level: {user_expertise}
                Target language: {language}
                
                Requirements:
                - Provide practical, actionable advice
                - Draw from {domain} domain expertise
                - Be helpful and encouraging
                - Include specific tips or resources
                - Keep it conversational and authentic
                - Consider Indian context and cultural nuances
                
                Format as a natural Reddit comment that adds genuine value.
                """
                
                reply_content = await self._generate_with_fallback(reply_prompt, "reddit", language)
                
                generated_replies.append({
                    "question_id": question["id"],
                    "question_title": question["title"],
                    "subreddit": question["subreddit"],
                    "generated_reply": reply_content,
                    "word_count": len(reply_content.split()),
                    "domain": domain
                })
            
            return {
                "success": True,
                "replies_generated": len(generated_replies),
                "replies": generated_replies,
                "domain": domain,
                "language": language,
                "message": f"Generated {len(generated_replies)} domain-specific replies"
            }
            
        except Exception as e:
            logger.error(f"Monitor and reply failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate replies"
            }
    
    async def speech_to_text(
        self,
        audio_base64: str,
        language: str = "auto"
    ) -> Dict[str, Any]:
        """
        Convert speech to text with language detection
        
        Args:
            audio_base64: Base64 encoded audio data
            language: Target language or 'auto' for detection
            
        Returns:
            Dictionary containing transcribed text
        """
        try:
            if not sr:
                raise ImportError("SpeechRecognition library not available")
            
            # Decode audio data
            audio_data = base64.b64decode(audio_base64)
            
            # Convert to audio file
            audio_file = io.BytesIO(audio_data)
            
            # Initialize recognizer
            recognizer = sr.Recognizer()
            
            # Process audio
            with sr.AudioFile(audio_file) as source:
                audio = recognizer.record(source)
            
            # Transcribe with language detection
            if language == "auto":
                # Try multiple languages for Indian users
                languages_to_try = ["en-US", "hi-IN", "ta-IN", "te-IN", "bn-IN"]
                
                for lang in languages_to_try:
                    try:
                        text = recognizer.recognize_google(audio, language=lang)
                        detected_language = lang.split("-")[0]
                        break
                    except sr.UnknownValueError:
                        continue
                else:
                    # Fallback to English
                    text = recognizer.recognize_google(audio, language="en-US")
                    detected_language = "en"
            else:
                text = recognizer.recognize_google(audio, language=f"{language}-IN")
                detected_language = language
            
            return {
                "success": True,
                "text": text,
                "detected_language": detected_language,
                "confidence": 0.95,  # Placeholder - Google API doesn't provide confidence
                "message": "Speech transcribed successfully"
            }
            
        except Exception as e:
            logger.error(f"Speech to text failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to transcribe speech"
            }
    
    async def text_to_speech(
        self,
        text: str,
        language: str = "en",
        voice: str = "default"
    ) -> Dict[str, Any]:
        """
        Convert text to speech with voice selection
        
        Args:
            text: Text to convert
            language: Speech language
            voice: Voice type (default, male, female)
            
        Returns:
            Dictionary containing audio data
        """
        try:
            if not gTTS:
                raise ImportError("gTTS library not available")
            
            # Language mapping for Indian languages
            language_mapping = {
                "hi": "hi",
                "ta": "ta",
                "te": "te",
                "bn": "bn",
                "mr": "mr",
                "gu": "gu",
                "kn": "kn",
                "ml": "ml",
                "pa": "pa",
                "en": "en"
            }
            
            tts_language = language_mapping.get(language, "en")
            
            # Generate speech
            tts = gTTS(text=text, lang=tts_language, slow=False)
            
            # Save to BytesIO
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Encode to base64
            audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "language": language,
                "voice": voice,
                "text_length": len(text),
                "message": "Text converted to speech successfully"
            }
            
        except Exception as e:
            logger.error(f"Text to speech failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to convert text to speech"
            }
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of input text
        
        Args:
            text: Input text
            
        Returns:
            Dictionary containing detected language
        """
        try:
            if not detect:
                raise ImportError("langdetect library not available")
            
            detected_lang = detect(text)
            
            # Language names mapping
            language_names = {
                "en": "English",
                "hi": "Hindi",
                "ta": "Tamil",
                "te": "Telugu",
                "bn": "Bengali",
                "mr": "Marathi",
                "gu": "Gujarati",
                "kn": "Kannada",
                "ml": "Malayalam",
                "pa": "Punjabi",
                "or": "Odia",
                "as": "Assamese"
            }
            
            return {
                "success": True,
                "detected_language": detected_lang,
                "language_name": language_names.get(detected_lang, "Unknown"),
                "confidence": 0.9,  # Placeholder
                "message": "Language detected successfully"
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "success": False,
                "detected_language": "en",
                "language_name": "English",
                "error": str(e),
                "message": "Language detection failed, defaulting to English"
            }
    
    async def translate_text(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """
        Translate text between languages
        
        Args:
            text: Text to translate
            source_language: Source language or 'auto'
            target_language: Target language
            
        Returns:
            Dictionary containing translated text
        """
        try:
            if not self.translator:
                raise ImportError("googletrans library not available")
            
            # Perform translation
            if source_language == "auto":
                result = self.translator.translate(text, dest=target_language)
                detected_source = result.src
            else:
                result = self.translator.translate(text, src=source_language, dest=target_language)
                detected_source = source_language
            
            return {
                "success": True,
                "translated_text": result.text,
                "source_language": detected_source,
                "target_language": target_language,
                "original_text": text,
                "message": "Text translated successfully"
            }
            
        except Exception as e:
            logger.error(f"Translation failed: {e}")
            return {
                "success": False,
                "translated_text": text,  # Return original on failure
                "error": str(e),
                "message": "Translation failed, returning original text"
            }
    
    async def _generate_with_fallback(
        self,
        prompt: str,
        platform: str,
        language: str
    ) -> str:
        """
        Generate content with Mistral primary, Groq fallback
        
        Args:
            prompt: Generation prompt
            platform: Target platform
            language: Content language
            
        Returns:
            Generated content string
        """
        # Try Mistral first
        if self.mistral_client:
            try:
                response = self.mistral_client.chat(
                    model="mistral-large-latest",
                    messages=[
                        ChatMessage(role="user", content=prompt)
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                logger.info("Content generated using Mistral AI")
                return content
                
            except Exception as e:
                logger.warning(f"Mistral AI failed: {e}, trying Groq fallback")
        
        # Fallback to Groq
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="mixtral-8x7b-32768",
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1000
                )
                content = response.choices[0].message.content
                logger.info("Content generated using Groq fallback")
                return content
                
            except Exception as e:
                logger.error(f"Groq fallback also failed: {e}")
        
        # Ultimate fallback - return template response
        logger.warning("Both AI services failed, using template response")
        return self._get_template_response(platform, language)
    
    def _get_reddit_post_prompt(self, **kwargs) -> str:
        """Generate Reddit post prompt"""
        domain_context = ""
        if kwargs.get('domain'):
            domain_config = self.domain_templates.get(kwargs['domain'], {})
            domain_context = f"""
            Domain: {kwargs['domain']}
            Relevant keywords: {', '.join(domain_config.get('keywords', []))}
            Target subreddits: {', '.join(domain_config.get('reddit_subreddits', []))}
            Content themes: {', '.join(domain_config.get('content_themes', []))}
            """
        
        return f"""
        Create a Reddit post about {kwargs['topic']} for r/india or related Indian subreddits.
        
        Requirements:
        - Tone: {kwargs['tone']}
        - Language: {kwargs['language']} (use Hindi words where culturally appropriate)
        - Target audience: {kwargs['target_audience']}
        - Length: 100-300 words
        - Make it engaging and discussion-worthy
        - Consider Indian cultural context and current trends
        - Include relevant hashtags sparingly
        
        {domain_context}
        
        Additional context: {kwargs.get('additional_context', '')}
        
        Format as a Reddit post with title and body.
        """
    
    def _get_reddit_comment_prompt(self, **kwargs) -> str:
        """Generate Reddit comment prompt"""
        return f"""
        Create a helpful Reddit comment about {kwargs['topic']}.
        
        Requirements:
        - Tone: {kwargs['tone']} but conversational
        - Language: {kwargs['language']}
        - Length: 50-150 words
        - Be helpful and add value to the discussion
        - Include personal insight or experience if relevant
        - Use appropriate Reddit culture and etiquette
        - Consider Indian context if applicable
        
        Make it sound natural and human-like.
        """
    
    def _get_reddit_answer_prompt(self, **kwargs) -> str:
        """Generate Reddit Q&A answer prompt - FIXED: This method was missing"""
        domain_context = ""
        if kwargs.get('domain'):
            domain_config = self.domain_templates.get(kwargs['domain'], {})
            domain_context = f"Drawing from {kwargs['domain']} domain expertise"
        
        return f"""
        Create a comprehensive Reddit answer about {kwargs['topic']}.
        
        Requirements:
        - Tone: {kwargs['tone']} but helpful and authoritative
        - Language: {kwargs['language']}
        - Length: 100-250 words
        - Provide practical, actionable advice
        - Include specific examples or steps where appropriate
        - Be encouraging and supportive
        - Consider Indian cultural context
        - Use Reddit formatting (bold, lists, etc.)
        
        {domain_context}
        
        Additional context: {kwargs.get('additional_context', '')}
        
        Format as a helpful Reddit answer that genuinely helps the questioner.
        """
    
    def _get_twitter_tweet_prompt(self, **kwargs) -> str:
        """Generate Twitter tweet prompt"""
        return f"""
        Create a Twitter/X tweet about {kwargs['topic']}.
        
        Requirements:
        - Tone: {kwargs['tone']}
        - Language: {kwargs['language']}
        - Length: Under 280 characters
        - Include relevant hashtags (2-3 max)
        - Make it engaging and shareable
        - Consider Indian context and current trends
        
        Additional context: {kwargs.get('additional_context', '')}
        """
    
    def _get_twitter_thread_prompt(self, **kwargs) -> str:
        """Generate Twitter thread prompt"""
        return f"""
        Create a Twitter thread about {kwargs['topic']}.
        
        Requirements:
        - Tone: {kwargs['tone']}
        - Language: {kwargs['language']}
        - 3-5 tweets in the thread
        - Each tweet under 280 characters
        - Progressive information flow
        - Include relevant hashtags
        - Consider Indian context
        
        Format as numbered tweets: 1/5, 2/5, etc.
        """
    
    def _get_twitter_reply_prompt(self, **kwargs) -> str:
        """Generate Twitter reply prompt"""
        return f"""
        Create a Twitter reply about {kwargs['topic']}.
        
        Requirements:
        - Tone: {kwargs['tone']} but conversational
        - Language: {kwargs['language']}
        - Length: Under 280 characters
        - Be engaging and add value
        - Consider context of original tweet
        """
    
    def _get_stackoverflow_answer_prompt(self, **kwargs) -> str:
        """Generate Stack Overflow answer prompt"""
        return f"""
        Create a comprehensive Stack Overflow answer about {kwargs['topic']}.
        
        Requirements:
        - Tone: Technical and professional
        - Language: English (programming terms)
        - Include code examples if applicable
        - Explain the solution step-by-step
        - Add references or documentation links
        - Consider different scenarios and edge cases
        - Format with proper markdown
        
        Make it detailed enough to be helpful for other developers.
        """
    
    def _get_stackoverflow_question_prompt(self, **kwargs) -> str:
        """Generate Stack Overflow question prompt"""
        return f"""
        Create a well-structured Stack Overflow question about {kwargs['topic']}.
        
        Requirements:
        - Clear, specific title
        - Detailed problem description
        - Include relevant code snippets
        - Specify expected vs actual behavior
        - Add relevant tags
        - Follow SO best practices
        """
    
    def _get_webmd_answer_prompt(self, **kwargs) -> str:
        """Generate WebMD health answer prompt"""
        return f"""
        Create a helpful health information response about {kwargs['topic']}.
        
        Requirements:
        - Tone: Professional, caring, and informative
        - Language: {kwargs['language']} (simple, non-technical terms)
        - Include important health disclaimers
        - Provide general information, not specific medical advice
        - Suggest when to consult healthcare professionals
        - Be culturally sensitive to Indian health practices
        
        IMPORTANT: Always emphasize consulting qualified medical professionals.
        """
    
    def _get_webmd_advice_prompt(self, **kwargs) -> str:
        """Generate WebMD health advice prompt"""
        return f"""
        Create general health advice about {kwargs['topic']}.
        
        Requirements:
        - Focus on prevention and wellness
        - Include lifestyle recommendations
        - Be culturally appropriate for Indian users
        - Add strong medical disclaimers
        - Suggest professional consultation
        """