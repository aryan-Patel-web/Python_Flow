import os
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import requests
from groq import Groq
from openai import OpenAI
from bson.objectid import ObjectId

# File processing imports
import PyPDF2
import docx
from pptx import Presentation
from PIL import Image
import pytesseract
import pdfplumber
from langdetect import detect
import pandas as pd

from config.database import db_instance
from services.file_processor_service import FileProcessorService
from utils.response_utils import create_response

logger = logging.getLogger(__name__)

class AIContentService:
    def __init__(self):
        # Initialize AI clients with fallback handling
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Initialize clients
        self.groq_client = None
        self.openai_client = None
        
        try:
            if self.groq_api_key:
                self.groq_client = Groq(api_key=self.groq_api_key)
        except Exception as e:
            logger.warning(f"Groq client initialization failed: {str(e)}")
        
        try:
            if self.openai_api_key:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
        except Exception as e:
            logger.warning(f"OpenAI client initialization failed: {str(e)}")
        
        # Initialize file processor
        self.file_processor = FileProcessorService()
        
        # Content domains configuration
        self.content_domains = {
            "tech": {
                "name": "Technology & Innovation",
                "topics": [
                    "AI and Machine Learning", "Web Development", "Mobile Apps", 
                    "Cybersecurity", "Cloud Computing", "DevOps", "Data Science",
                    "Blockchain", "IoT", "Automation"
                ],
                "tone": "informative, cutting-edge, professional",
                "hashtags": ["#Tech", "#Innovation", "#AI", "#Development", "#Future"]
            },
            "business": {
                "name": "Business & Entrepreneurship",
                "topics": [
                    "Startup Tips", "Leadership", "Marketing", "Sales", "Finance",
                    "Productivity", "Team Management", "Strategy", "Growth Hacking"
                ],
                "tone": "authoritative, motivational, professional",
                "hashtags": ["#Business", "#Entrepreneur", "#Leadership", "#Growth", "#Success"]
            },
            "lifestyle": {
                "name": "Lifestyle & Wellness",
                "topics": [
                    "Health & Fitness", "Travel", "Food", "Fashion", "Home Decor",
                    "Self-Care", "Mindfulness", "Relationships", "Hobbies"
                ],
                "tone": "friendly, inspiring, relatable",
                "hashtags": ["#Lifestyle", "#Wellness", "#Health", "#Travel", "#SelfCare"]
            },
            "finance": {
                "name": "Finance & Investment",
                "topics": [
                    "Personal Finance", "Investment Tips", "Cryptocurrency", 
                    "Real Estate", "Budgeting", "Retirement Planning", "Trading"
                ],
                "tone": "educational, trustworthy, data-driven",
                "hashtags": ["#Finance", "#Investment", "#Money", "#Wealth", "#Trading"]
            },
            "memes": {
                "name": "Memes & Humor",
                "topics": [
                    "Programming Memes", "Work From Home", "Developer Life",
                    "Office Humor", "Tech Jokes", "Startup Memes"
                ],
                "tone": "funny, relatable, casual, witty",
                "hashtags": ["#Memes", "#Humor", "#Funny", "#Relatable", "#LOL"]
            }
        }
        
        # Platform specifications
        self.platform_specs = {
            "instagram": {
                "max_length": 2200,
                "optimal_length": 125,
                "supports_hashtags": True,
                "supports_emojis": True,
                "style": "visual, engaging, hashtag-heavy"
            },
            "twitter": {
                "max_length": 280,
                "optimal_length": 100,
                "supports_hashtags": True,
                "supports_emojis": True,
                "style": "concise, witty, conversational"
            },
            "linkedin": {
                "max_length": 3000,
                "optimal_length": 150,
                "supports_hashtags": True,
                "supports_emojis": False,
                "style": "professional, thought-leadership, industry-focused"
            },
            "facebook": {
                "max_length": 63206,
                "optimal_length": 80,
                "supports_hashtags": True,
                "supports_emojis": True,
                "style": "engaging, community-focused, conversational"
            },
            "youtube": {
                "max_length": 5000,
                "optimal_length": 200,
                "supports_hashtags": True,
                "supports_emojis": True,
                "style": "descriptive, engaging, SEO-optimized"
            }
        }

    def generate_content(self, user_id: str, request_data: Dict) -> Dict:
        """
        Generate AI content with enhanced features including file processing
        """
        try:
            # Validate request
            domain = request_data.get('domain', 'general')
            platform = request_data.get('platform', 'instagram')
            custom_prompt = request_data.get('custom_prompt', '')
            creativity_level = request_data.get('creativity_level', 70)
            include_hashtags = request_data.get('include_hashtags', True)
            include_emojis = request_data.get('include_emojis', True)
            follow_trends = request_data.get('follow_trends', True)
            
            # NEW: File processing
            uploaded_file_id = request_data.get('uploaded_file_id')
            file_content = ""
            file_context = {}
            
            if uploaded_file_id:
                # Process uploaded file
                file_result = self.file_processor.process_file(uploaded_file_id)
                if file_result['success']:
                    file_content = file_result['content']
                    file_context = file_result['context']
                else:
                    logger.warning(f"File processing failed: {file_result['error']}")
            
            # Enhanced content generation with file context
            content_result = self._generate_ai_content(
                domain=domain,
                platform=platform,
                custom_prompt=custom_prompt,
                creativity_level=creativity_level,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis,
                follow_trends=follow_trends,
                file_content=file_content,
                file_context=file_context
            )
            
            if not content_result['success']:
                return create_response(False, "Content generation failed", None, 500)
            
            # Save generation record
            generation_record = self._save_generation_record(
                user_id=user_id,
                request_data=request_data,
                result=content_result['content'],
                file_context=file_context
            )
            
            # Create response
            response_data = {
                "generated_content": content_result['content'],
                "generation_id": str(generation_record.inserted_id),
                "file_processed": bool(uploaded_file_id),
                "file_context": file_context if uploaded_file_id else None
            }
            
            return create_response(True, "Content generated successfully", response_data)
            
        except Exception as e:
            logger.error(f"Content generation error: {str(e)}")
            return create_response(False, "Content generation failed. Please try again.", None, 500)

    def _generate_ai_content(self, domain: str, platform: str, custom_prompt: str, 
                           creativity_level: int, include_hashtags: bool, include_emojis: bool,
                           follow_trends: bool, file_content: str = "", file_context: Dict = {}) -> Dict:
        """
        Generate content using AI with file context
        """
        try:
            # Build comprehensive prompt
            prompt = self._build_enhanced_prompt(
                domain=domain,
                platform=platform,
                custom_prompt=custom_prompt,
                creativity_level=creativity_level,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis,
                follow_trends=follow_trends,
                file_content=file_content,
                file_context=file_context
            )
            
            # Try Mistral first (primary)
            content = self._try_mistral_generation(prompt, creativity_level)
            
            if not content:
                # Fallback to Groq
                logger.info("Mistral failed, trying Groq...")
                content = self._try_groq_generation(prompt, creativity_level)
            
            if not content:
                # Final fallback to OpenAI
                logger.info("Groq failed, trying OpenAI...")
                content = self._try_openai_generation(prompt, creativity_level)
            
            if not content:
                return {"success": False, "error": "All AI services failed"}
            
            # Process and enhance generated content
            processed_content = self._process_generated_content(
                content=content,
                platform=platform,
                domain=domain,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis
            )
            
            return {"success": True, "content": processed_content}
            
        except Exception as e:
            logger.error(f"AI content generation error: {str(e)}")
            return {"success": False, "error": str(e)}

    def _build_enhanced_prompt(self, domain: str, platform: str, custom_prompt: str,
                             creativity_level: int, include_hashtags: bool, include_emojis: bool,
                             follow_trends: bool, file_content: str = "", file_context: Dict = {}) -> str:
        """
        Build comprehensive prompt with file context
        """
        domain_config = self.content_domains.get(domain, self.content_domains['business'])
        platform_config = self.platform_specs.get(platform, self.platform_specs['instagram'])
        
        # Base prompt
        prompt_parts = [
            f"You are an expert social media content creator specializing in {domain_config['name']}.",
            f"Create engaging content for {platform.title()} with a {domain_config['tone']} tone.",
            f"Platform requirements: {platform_config['style']}, max {platform_config['max_length']} characters, optimal ~{platform_config['optimal_length']} characters."
        ]
        
        # Add file context if available
        if file_content and file_context:
            file_type = file_context.get('file_type', 'document')
            file_summary = file_context.get('summary', '')
            
            prompt_parts.extend([
                f"\nIMPORTANT: Base your content on this uploaded {file_type}:",
                f"File Summary: {file_summary}",
                f"Key Content: {file_content[:1000]}...",  # Limit to avoid token limits
                f"Create content that builds upon, summarizes, or transforms this source material."
            ])
        
        # Add custom prompt
        if custom_prompt:
            prompt_parts.append(f"\nSpecific Request: {custom_prompt}")
        
        # Add creativity instructions
        creativity_instruction = {
            range(0, 30): "Be conservative and professional",
            range(30, 60): "Be moderately creative with some unique angles",
            range(60, 85): "Be highly creative with engaging hooks and unique perspectives",
            range(85, 101): "Be extremely creative with bold ideas and unconventional approaches"
        }
        
        for range_val, instruction in creativity_instruction.items():
            if creativity_level in range_val:
                prompt_parts.append(f"\nCreativity Level ({creativity_level}/100): {instruction}")
                break
        
        # Add formatting requirements
        format_requirements = []
        
        if include_hashtags and platform_config['supports_hashtags']:
            relevant_hashtags = domain_config['hashtags'][:5]  # Limit hashtags
            format_requirements.append(f"Include relevant hashtags from: {', '.join(relevant_hashtags)}")
        
        if include_emojis and platform_config['supports_emojis']:
            format_requirements.append("Include appropriate emojis to increase engagement")
        
        if follow_trends:
            format_requirements.append("Reference current trends and popular topics when relevant")
        
        if format_requirements:
            prompt_parts.append(f"\nFormatting: {'; '.join(format_requirements)}")
        
        # Add platform-specific instructions
        platform_instructions = {
            'instagram': "Focus on visual storytelling, use line breaks for readability",
            'twitter': "Keep it punchy and conversational, encourage retweets",
            'linkedin': "Professional tone, thought leadership, industry insights",
            'facebook': "Community-focused, encourage comments and shares",
            'youtube': "SEO-optimized description, include call-to-action"
        }
        
        if platform in platform_instructions:
            prompt_parts.append(f"\n{platform.title()} Specific: {platform_instructions[platform]}")
        
        prompt_parts.append("\nGenerate only the content, no explanations or meta-text.")
        
        return "\n".join(prompt_parts)

    def _try_mistral_generation(self, prompt: str, creativity_level: int) -> Optional[str]:
        """Try Mistral AI for content generation"""
        try:
            if not self.mistral_api_key:
                return None
            
            # Use Mistral API via HTTP requests
            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }
            
            # Adjust temperature based on creativity level
            temperature = min(creativity_level / 100, 0.9)
            
            data = {
                'model': 'mistral-large-latest',
                'messages': [{'role': 'user', 'content': prompt}],
                'temperature': temperature,
                'max_tokens': 500,
                'top_p': 0.9
            }
            
            response = requests.post(
                'https://api.mistral.ai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                return content
            else:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Mistral generation error: {str(e)}")
            return None

    def _try_groq_generation(self, prompt: str, creativity_level: int) -> Optional[str]:
        """Try Groq for content generation"""
        try:
            if not self.groq_client:
                return None
            
            temperature = min(creativity_level / 100, 0.9)
            
            completion = self.groq_client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=500,
                top_p=0.9
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Groq generation error: {str(e)}")
            return None

    def _try_openai_generation(self, prompt: str, creativity_level: int) -> Optional[str]:
        """Try OpenAI for content generation"""
        try:
            if not self.openai_client:
                return None
            
            temperature = min(creativity_level / 100, 0.9)
            
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=500,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI generation error: {str(e)}")
            return None

    def _process_generated_content(self, content: str, platform: str, domain: str,
                                 include_hashtags: bool, include_emojis: bool) -> Dict:
        """Process and enhance generated content with analytics"""
        try:
            platform_config = self.platform_specs.get(platform, self.platform_specs['instagram'])
            
            # Ensure content fits platform limits
            if len(content) > platform_config['max_length']:
                content = content[:platform_config['max_length'] - 3] + "..."
            
            # Count elements
            word_count = len(content.split())
            character_count = len(content)
            hashtag_count = content.count('#')
            emoji_count = len([char for char in content if char.encode('unicode_escape').startswith(b'\\U')])
            
            # Performance prediction (mock algorithm - replace with actual ML model)
            performance_score = self._predict_performance(
                content=content,
                platform=platform,
                domain=domain,
                word_count=word_count,
                hashtag_count=hashtag_count,
                emoji_count=emoji_count
            )
            
            # Generate engagement predictions
            base_engagement = {
                'instagram': {'likes': 150, 'comments': 12, 'shares': 8},
                'twitter': {'likes': 80, 'retweets': 15, 'replies': 6},
                'linkedin': {'likes': 45, 'comments': 8, 'shares': 12},
                'facebook': {'likes': 120, 'comments': 18, 'shares': 25},
                'youtube': {'views': 500, 'likes': 45, 'comments': 12}
            }
            
            platform_base = base_engagement.get(platform, base_engagement['instagram'])
            performance_multiplier = performance_score / 100
            
            predicted_engagement = {
                key: max(1, int(value * performance_multiplier))
                for key, value in platform_base.items()
            }
            
            return {
                "content": content,
                "domain": domain,
                "platform": platform,
                "performance_prediction": {
                    "score": performance_score,
                    "grade": self._score_to_grade(performance_score),
                    "predicted_engagement": predicted_engagement,
                    "confidence": min(85 + (performance_score - 50) * 0.3, 99)
                },
                "metadata": {
                    "word_count": word_count,
                    "character_count": character_count,
                    "hashtag_count": hashtag_count,
                    "emoji_count": emoji_count,
                    "generated_at": datetime.utcnow().isoformat(),
                    "ai_model_used": "mistral-primary-groq-fallback",
                    "creativity_level": None,
                    "platform_optimized": True,
                    "fits_character_limit": character_count <= platform_config['max_length']
                }
            }
            
        except Exception as e:
            logger.error(f"Content processing error: {str(e)}")
            return {
                "content": content,
                "error": "Processing failed",
                "metadata": {"generated_at": datetime.utcnow().isoformat()}
            }

    def _predict_performance(self, content: str, platform: str, domain: str,
                           word_count: int, hashtag_count: int, emoji_count: int) -> int:
        """Predict content performance score (1-100)"""
        try:
            score = 50  # Base score
            
            # Platform-specific optimizations
            platform_config = self.platform_specs.get(platform, self.platform_specs['instagram'])
            optimal_length = platform_config['optimal_length']
            
            # Length scoring
            length_diff = abs(len(content) - optimal_length)
            if length_diff <= 20:
                score += 20
            elif length_diff <= 50:
                score += 10
            else:
                score -= 5
            
            # Hashtag scoring
            if platform_config['supports_hashtags']:
                if 3 <= hashtag_count <= 8:
                    score += 15
                elif 1 <= hashtag_count <= 2 or hashtag_count > 10:
                    score += 5
                else:
                    score -= 5
            
            # Emoji scoring
            if platform_config['supports_emojis']:
                if 1 <= emoji_count <= 3:
                    score += 10
                elif emoji_count > 5:
                    score -= 5
            
            # Content quality indicators
            if '?' in content:  # Questions increase engagement
                score += 8
            if any(word in content.lower() for word in ['tips', 'how', 'why', 'what', 'guide']):
                score += 12
            if any(word in content.lower() for word in ['new', 'trending', '2024', '2025', 'latest']):
                score += 8
            
            # Word count optimization
            if platform == 'twitter' and word_count <= 20:
                score += 10
            elif platform == 'linkedin' and 20 <= word_count <= 40:
                score += 15
            elif platform == 'instagram' and 15 <= word_count <= 30:
                score += 12
            
            return max(1, min(100, score))
            
        except Exception as e:
            logger.error(f"Performance prediction error: {str(e)}")
            return 65  # Default score

    def _score_to_grade(self, score: int) -> str:
        """Convert numerical score to letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "C+"
        elif score >= 65:
            return "C"
        elif score >= 60:
            return "D+"
        else:
            return "D"

    def _save_generation_record(self, user_id: str, request_data: Dict, 
                              result: Dict, file_context: Dict) -> Any:
        """Save content generation record to database"""
        try:
            db = db_instance.get_db()
            
            record = {
                'user_id': user_id,
                'domain': request_data.get('domain'),
                'platform': request_data.get('platform'),
                'custom_prompt': request_data.get('custom_prompt', ''),
                'creativity_level': request_data.get('creativity_level', 70),
                'generated_content': result.get('content', ''),
                'performance_score': result.get('performance_prediction', {}).get('score', 0),
                'metadata': result.get('metadata', {}),
                'file_context': file_context,
                'created_at': datetime.utcnow(),
                'usage_type': 'ai_generation'
            }
            
            return db.content_generations.insert_one(record)
            
        except Exception as e:
            logger.error(f"Error saving generation record: {str(e)}")
            return None

    def generate_content_variants(self, user_id: str, base_content: str, 
                                count: int = 3, platform: str = 'instagram') -> Dict:
        """Generate multiple variants of content (Pro+ feature)"""
        try:
            # Check user plan (this would be implemented in user service)
            # For now, assume it's allowed
            
            variants = []
            base_prompt = f"Create {count} different variations of this social media post for {platform}:\n\n{base_content}\n\nMake each variant unique in style and approach while keeping the core message."
            
            # Generate variants using primary AI service
            for i in range(count):
                variant_prompt = f"{base_prompt}\n\nVariant {i+1}: Focus on {'engagement' if i == 0 else 'information' if i == 1 else 'emotion'} style."
                
                variant_content = self._try_mistral_generation(variant_prompt, 75)
                if not variant_content:
                    variant_content = self._try_groq_generation(variant_prompt, 75)
                
                if variant_content:
                    processed_variant = self._process_generated_content(
                        content=variant_content,
                        platform=platform,
                        domain='general',
                        include_hashtags=True,
                        include_emojis=True
                    )
                    variants.append(processed_variant)
            
            return create_response(True, f"Generated {len(variants)} variants", {
                "variants": variants,
                "original_content": base_content
            })
            
        except Exception as e:
            logger.error(f"Variant generation error: {str(e)}")
            return create_response(False, "Variant generation failed", None, 500)

    def get_content_domains(self) -> Dict:
        """Get available content domains"""
        try:
            domains_list = []
            for domain_id, domain_info in self.content_domains.items():
                domains_list.append({
                    "id": domain_id,
                    "name": domain_info["name"],
                    "topics": domain_info["topics"][:5],  # Limit topics for response
                    "tone": domain_info["tone"],
                    "sample_hashtags": domain_info["hashtags"][:3]
                })
            
            return create_response(True, "Content domains retrieved", {
                "domains": domains_list,
                "total": len(domains_list)
            })
            
        except Exception as e:
            logger.error(f"Error getting content domains: {str(e)}")
            return create_response(False, "Failed to get domains", None, 500)

    def get_user_generations(self, user_id: str, limit: int = 20, offset: int = 0) -> Dict:
        """Get user's recent content generations"""
        try:
            db = db_instance.get_db()
            
            generations = list(
                db.content_generations
                .find({'user_id': user_id})
                .sort('created_at', -1)
                .limit(limit)
                .skip(offset)
            )
            
            # Convert ObjectIds to strings
            for gen in generations:
                gen['_id'] = str(gen['_id'])
                gen['created_at'] = gen['created_at'].isoformat()
            
            total_count = db.content_generations.count_documents({'user_id': user_id})
            
            return create_response(True, "Generations retrieved", {
                "generations": generations,
                "total": total_count,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"Error getting user generations: {str(e)}")
            return create_response(False, "Failed to get generations", None, 500)

    def get_usage_stats(self, user_id: str) -> Dict:
        """Get user's AI content generation usage statistics"""
        try:
            db = db_instance.get_db()
            
            # Current month stats
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_count = db.content_generations.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': current_month_start}
            })
            
            # Today's stats
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            daily_count = db.content_generations.count_documents({
                'user_id': user_id,
                'created_at': {'$gte': today_start}
            })
            
            # Total stats
            total_count = db.content_generations.count_documents({'user_id': user_id})
            
            # Average performance score
            pipeline = [
                {'$match': {'user_id': user_id, 'performance_score': {'$exists': True}}},
                {'$group': {'_id': None, 'avg_score': {'$avg': '$performance_score'}}}
            ]
            
            avg_result = list(db.content_generations.aggregate(pipeline))
            avg_score = round(avg_result[0]['avg_score'], 1) if avg_result else 0
            
            return create_response(True, "Usage stats retrieved", {
                "monthly_generations": monthly_count,
                "daily_generations": daily_count,
                "total_generations": total_count,
                "average_performance_score": avg_score,
                "month_start": current_month_start.isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return create_response(False, "Failed to get usage stats", None, 500)