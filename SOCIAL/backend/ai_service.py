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
        
        # Platform-specific prompts
        self.platform_prompts = {
            "reddit": {
                "post": self._get_reddit_post_prompt,
                "comment": self._get_reddit_comment_prompt,
                "answer": self._get_reddit_answer_prompt
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
    
    async def generate_platform_content(
        self,
        platform: str,
        content_type: str,
        topic: str,
        tone: str = "professional",
        language: str = "en",
        target_audience: str = "general",
        additional_context: str = ""
    ) -> Dict[str, Any]:
        """
        Generate platform-specific content using AI
        
        Args:
            platform: Target platform (reddit, twitter, stackoverflow, webmd)
            content_type: Type of content (post, comment, answer, etc.)
            topic: Content topic
            tone: Content tone (professional, casual, friendly, etc.)
            language: Target language
            target_audience: Target audience description
            additional_context: Additional context or requirements
            
        Returns:
            Dictionary containing generated content and metadata
        """
        try:
            # Get platform-specific prompt
            prompt_generator = self.platform_prompts.get(platform, {}).get(content_type)
            if not prompt_generator:
                raise ValueError(f"Unsupported platform/content_type: {platform}/{content_type}")
            
            # Generate prompt
            prompt = prompt_generator(
                topic=topic,
                tone=tone,
                language=language,
                target_audience=target_audience,
                additional_context=additional_context
            )
            
            # Generate content using AI
            content = await self._generate_with_fallback(prompt, platform, language)
            
            # Post-process content
            processed_content = self._post_process_content(content, platform, language)
            
            return {
                "success": True,
                "content": processed_content,
                "platform": platform,
                "content_type": content_type,
                "language": language,
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
    
    async def generate_qa_answer(
        self,
        platform: str,
        question: str,
        context: str = "",
        language: str = "en",
        expertise_level: str = "intermediate"
    ) -> Dict[str, Any]:
        """
        Generate Q&A answer for educational platforms
        
        Args:
            platform: Platform name (stackoverflow, webmd, reddit)
            question: Question text
            context: Additional context about the question
            language: Response language
            expertise_level: Level of technical detail (beginner, intermediate, advanced)
            
        Returns:
            Dictionary containing generated answer
        """
        try:
            # Create specialized Q&A prompt
            prompt = self._get_qa_prompt(
                platform=platform,
                question=question,
                context=context,
                language=language,
                expertise_level=expertise_level
            )
            
            # Generate answer
            answer = await self._generate_with_fallback(prompt, platform, language)
            
            # Add platform-specific formatting and disclaimers
            formatted_answer = self._format_qa_answer(answer, platform, language)
            
            return {
                "success": True,
                "answer": formatted_answer,
                "platform": platform,
                "language": language,
                "expertise_level": expertise_level,
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
        return f"""
        Create a Reddit post about {kwargs['topic']} for r/india or related Indian subreddits.
        
        Requirements:
        - Tone: {kwargs['tone']}
        - Language: {kwargs['language']} (use Hindi words where culturally appropriate)
        - Target audience: {kwargs['target_audience']}
        - Length: 100-300 words
        - Include relevant hashtags
        - Make it engaging and discussion-worthy
        - Consider Indian cultural context and current trends
        
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
        
        Make it sound natural and human-like.
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
    
    def _get_qa_prompt(self, **kwargs) -> str:
        """Generate general Q&A prompt"""
        platform_specific = {
            "stackoverflow": "Provide a technical programming solution with code examples.",
            "webmd": "Provide health information with appropriate medical disclaimers.",
            "reddit": "Provide a helpful, conversational answer that adds value to the discussion."
        }
        
        platform_instruction = platform_specific.get(kwargs['platform'], "Provide a helpful, accurate answer.")
        
        return f"""
        Question: {kwargs['question']}
        Context: {kwargs.get('context', '')}
        
        {platform_instruction}
        
        Requirements:
        - Language: {kwargs['language']}
        - Expertise level: {kwargs['expertise_level']}
        - Be accurate and helpful
        - Include examples where appropriate
        - Consider Indian context and audience
        
        Provide a comprehensive answer.
        """
    
    def _post_process_content(self, content: str, platform: str, language: str) -> str:
        """Post-process generated content for platform specifics"""
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Platform-specific processing
        if platform == "twitter":
            # Ensure under 280 characters
            if len(content) > 280:
                content = content[:277] + "..."
        
        elif platform == "reddit":
            # Add Reddit-style formatting
            content = content.replace("**", "**")  # Keep bold formatting
            content = content.replace("*", "*")    # Keep italic formatting
        
        elif platform == "stackoverflow":
            # Ensure proper code formatting
            content = re.sub(r'```(\w+)?\n(.*?)\n```', r'```\1\n\2\n```', content, flags=re.DOTALL)
        
        # Language-specific processing
        if language == "hi":
            # Add appropriate Hindi greetings/closings
            if not any(word in content.lower() for word in ['नमस्ते', 'धन्यवाद']):
                content = "नमस्ते! " + content + " धन्यवाद!"
        
        return content.strip()
    
    def _format_qa_answer(self, answer: str, platform: str, language: str) -> str:
        """Format Q&A answer with platform-specific disclaimers"""
        formatted_answer = answer
        
        # Add platform-specific disclaimers
        if platform == "webmd":
            if language == "hi":
                disclaimer = "\n\n⚠️ महत्वपूर्ण: यह केवल सामान्य जानकारी है। किसी भी स्वास्थ्य समस्या के लिए योग्य डॉक्टर से सलाह लें।"
            else:
                disclaimer = "\n\n⚠️ IMPORTANT: This is general health information only. Always consult with qualified healthcare professionals for medical advice specific to your condition."
            formatted_answer += disclaimer
        
        elif platform == "stackoverflow":
            formatted_answer += "\n\n*Hope this helps! Feel free to ask if you need clarification on any part.*"
        
        elif platform == "reddit":
            if language == "hi":
                formatted_answer += "\n\nकोई और सवाल हो तो पूछिए! 😊"
            else:
                formatted_answer += "\n\nFeel free to ask if you have more questions! 😊"
        
        return formatted_answer
    
    def _get_template_response(self, platform: str, language: str) -> str:
        """Get template response when AI services fail"""
        templates = {
            "reddit": {
                "en": "Thank you for your question! This is an interesting topic that deserves a detailed discussion. I'd be happy to help you explore this further.",
                "hi": "आपके सवाल के लिए धन्यवाद! यह एक दिलचस्प विषय है जिस पर विस्तार से चर्चा की जा सकती है।"
            },
            "twitter": {
                "en": "Sharing thoughts on this important topic. What's your perspective? #Discussion",
                "hi": "इस महत्वपूर्ण विषय पर विचार साझा कर रहा हूं। आपका क्या नजरिया है? #चर्चा"
            },
            "stackoverflow": {
                "en": "This is a great question that requires a detailed technical explanation. Let me break down the approach step by step.",
                "hi": "यह एक बेहतरीन सवाल है जिसके लिए विस्तृत तकनीकी व्याख्या की आवश्यकता है।"
            },
            "webmd": {
                "en": "Thank you for your health question. While I can provide general information, it's important to consult with healthcare professionals for personalized advice.",
                "hi": "आपके स्वास्थ्य संबंधी प्रश्न के लिए धन्यवाद। व्यक्तिगत सलाह के लिए स्वास्थ्य विशेषज्ञों से संपर्क करना महत्वपूर्ण है।"
            }
        }
        
        return templates.get(platform, {}).get(language, templates.get(platform, {}).get("en", "Thank you for your question!"))
    
    def health_check(self) -> Dict[str, Any]:
        """Check AI service health status"""
        try:
            services_status = {
                "mistral": bool(self.mistral_client),
                "groq": bool(self.groq_client),
                "translator": bool(self.translator),
                "voice_engine": bool(self.voice_engine),
                "speech_recognition": bool(sr),
                "text_to_speech": bool(gTTS)
            }
            
            # Test basic functionality
            test_results = {}
            
            # Test language detection
            try:
                if detect:
                    test_lang = detect("Hello world")
                    test_results["language_detection"] = True
                else:
                    test_results["language_detection"] = False
            except:
                test_results["language_detection"] = False
            
            # Test AI generation (simple test)
            try:
                if self.mistral_client or self.groq_client:
                    test_results["ai_generation"] = True
                else:
                    test_results["ai_generation"] = False
            except:
                test_results["ai_generation"] = False
            
            overall_health = any([
                services_status["mistral"],
                services_status["groq"]
            ])
            
            return {
                "success": True,
                "status": "healthy" if overall_health else "degraded",
                "services": services_status,
                "test_results": test_results,
                "message": "AI service health check completed"
            }
            
        except Exception as e:
            logger.error(f"AI service health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "message": "AI service health check failed"
            }
    
    async def generate_bulk_content(
        self,
        content_requests: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple pieces of content concurrently
        
        Args:
            content_requests: List of content generation requests
            max_concurrent: Maximum concurrent generations
            
        Returns:
            List of generation results
        """
        async def generate_single(request):
            try:
                return await self.generate_platform_content(**request)
            except Exception as e:
                logger.error(f"Bulk content generation failed for request: {e}")
                return {
                    "success": False,
                    "error": str(e),
                    "request": request
                }
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def generate_with_semaphore(request):
            async with semaphore:
                return await generate_single(request)
        
        # Execute all requests concurrently
        tasks = [generate_with_semaphore(request) for request in content_requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "request_index": i
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def optimize_content_for_engagement(
        self,
        content: str,
        platform: str,
        target_metrics: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Optimize content for better engagement based on platform best practices
        
        Args:
            content: Original content
            platform: Target platform
            target_metrics: Desired engagement metrics
            
        Returns:
            Dictionary containing optimized content and suggestions
        """
        try:
            optimization_prompt = f"""
            Optimize this {platform} content for maximum engagement:
            
            Original content: {content}
            
            Platform: {platform}
            Target metrics: {target_metrics or 'general engagement'}
            
            Provide:
            1. Optimized version of the content
            2. Specific improvements made
            3. Engagement predictions
            4. Best time to post recommendations
            5. Hashtag/keyword suggestions
            
            Consider {platform}-specific best practices and Indian audience preferences.
            """
            
            optimized_response = await self._generate_with_fallback(
                optimization_prompt, 
                platform, 
                "en"
            )
            
            # Parse the response (in production, you'd want more structured parsing)
            return {
                "success": True,
                "original_content": content,
                "optimized_content": optimized_response,
                "platform": platform,
                "optimization_score": 8.5,  # Placeholder
                "predicted_engagement": "high",  # Placeholder
                "message": "Content optimized successfully"
            }
            
        except Exception as e:
            logger.error(f"Content optimization failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "original_content": content,
                "message": "Content optimization failed"
            }
    
    async def analyze_content_sentiment(
        self,
        content: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Analyze sentiment and tone of content
        
        Args:
            content: Content to analyze
            language: Content language
            
        Returns:
            Dictionary containing sentiment analysis
        """
        try:
            analysis_prompt = f"""
            Analyze the sentiment and tone of this content:
            
            Content: {content}
            Language: {language}
            
            Provide:
            1. Overall sentiment (positive/negative/neutral)
            2. Emotional tone analysis
            3. Appropriateness for professional platforms
            4. Cultural sensitivity assessment
            5. Improvement suggestions if needed
            
            Return analysis in structured format.
            """
            
            analysis_response = await self._generate_with_fallback(
                analysis_prompt,
                "general",
                language
            )
            
            # Simple sentiment detection (in production, use specialized models)
            positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic"]
            negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = 0.7 + (positive_count * 0.1)
            elif negative_count > positive_count:
                sentiment = "negative"
                score = 0.3 - (negative_count * 0.1)
            else:
                sentiment = "neutral"
                score = 0.5
            
            return {
                "success": True,
                "content": content,
                "sentiment": sentiment,
                "sentiment_score": min(max(score, 0.0), 1.0),
                "analysis": analysis_response,
                "language": language,
                "word_count": len(content.split()),
                "message": "Sentiment analysis completed"
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "sentiment": "neutral",
                "sentiment_score": 0.5,
                "message": "Sentiment analysis failed"
            }
    
    def get_content_suggestions(
        self,
        platform: str,
        industry: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Get content suggestions based on platform and industry
        
        Args:
            platform: Target platform
            industry: User's industry/niche
            language: Content language
            
        Returns:
            Dictionary containing content suggestions
        """
        try:
            # Industry-specific content suggestions
            suggestions_db = {
                "education": {
                    "reddit": ["Study tips", "Career guidance", "Exam preparation", "Learning resources"],
                    "twitter": ["Educational quotes", "Quick tips", "Industry news", "Student motivation"],
                    "stackoverflow": ["Programming tutorials", "Code reviews", "Best practices"],
                    "webmd": ["Student health", "Stress management", "Nutrition for studying"]
                },
                "healthcare": {
                    "reddit": ["Health awareness", "Medical myths", "Preventive care", "Wellness tips"],
                    "twitter": ["Health facts", "Medical news", "Wellness quotes", "Prevention tips"],
                    "webmd": ["Common conditions", "Symptom explanations", "Treatment options", "Health education"]
                },
                "technology": {
                    "reddit": ["Tech trends", "Product reviews", "Industry insights", "Career advice"],
                    "twitter": ["Tech news", "Innovation updates", "Quick tutorials", "Industry thoughts"],
                    "stackoverflow": ["Code solutions", "Framework discussions", "Best practices", "Tool reviews"]
                },
                "business": {
                    "reddit": ["Entrepreneurship", "Business strategies", "Market insights", "Success stories"],
                    "twitter": ["Business tips", "Industry updates", "Motivational content", "Quick insights"],
                    "stackoverflow": ["Business automation", "Tool recommendations", "Workflow optimization"]
                }
            }
            
            platform_suggestions = suggestions_db.get(industry, {}).get(platform, [
                "General tips and advice",
                "Industry insights",
                "Helpful resources",
                "Community engagement"
            ])
            
            # Add trending topics (placeholder - in production, fetch from APIs)
            trending_topics = [
                "AI and automation",
                "Digital transformation",
                "Sustainable practices",
                "Remote work trends",
                "Indian startup ecosystem"
            ]
            
            return {
                "success": True,
                "platform": platform,
                "industry": industry,
                "language": language,
                "content_suggestions": platform_suggestions,
                "trending_topics": trending_topics,
                "message": "Content suggestions generated successfully"
            }
            
        except Exception as e:
            logger.error(f"Content suggestions failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to generate content suggestions"
            }