"""
AI Content Generation Service for VelocityPost.ai
Handles content generation using Mistral and Groq APIs
"""

import os
import requests
import json
import random
from typing import Dict, List, Optional
from datetime import datetime
from flask import current_app

class AIContentGenerator:
    """Main AI content generator class"""
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        
        # Content domains configuration
        self.content_domains = {
            'tech': {
                'name': 'Tech & Innovation',
                'keywords': ['AI', 'machine learning', 'blockchain', 'cybersecurity', 'cloud computing', 'IoT', 'automation'],
                'tone': 'informative, forward-thinking',
                'hashtags': ['#tech', '#innovation', '#AI', '#technology', '#future']
            },
            'memes': {
                'name': 'Memes & Humor',
                'keywords': ['funny', 'relatable', 'trending', 'viral', 'humor', 'comedy'],
                'tone': 'casual, humorous, engaging',
                'hashtags': ['#memes', '#funny', '#humor', '#viral', '#comedy']
            },
            'business': {
                'name': 'Business Tips',
                'keywords': ['entrepreneurship', 'startup', 'productivity', 'leadership', 'growth', 'strategy'],
                'tone': 'professional, motivational',
                'hashtags': ['#business', '#entrepreneur', '#startup', '#productivity', '#leadership']
            },
            'lifestyle': {
                'name': 'Lifestyle',
                'keywords': ['wellness', 'mindfulness', 'self-care', 'balance', 'happiness'],
                'tone': 'inspirational, positive',
                'hashtags': ['#lifestyle', '#wellness', '#selfcare', '#mindfulness', '#balance']
            },
            'fitness': {
                'name': 'Health & Fitness',
                'keywords': ['workout', 'nutrition', 'health', 'exercise', 'wellness', 'strength'],
                'tone': 'motivational, energetic',
                'hashtags': ['#fitness', '#health', '#workout', '#nutrition', '#wellness']
            },
            'finance': {
                'name': 'Finance & Investment',
                'keywords': ['investing', 'saving', 'money', 'stocks', 'crypto', 'financial planning'],
                'tone': 'analytical, educational',
                'hashtags': ['#finance', '#investing', '#money', '#crypto', '#wealth']
            },
            'travel': {
                'name': 'Travel & Adventure',
                'keywords': ['destinations', 'adventure', 'culture', 'exploration', 'wanderlust'],
                'tone': 'adventurous, inspiring',
                'hashtags': ['#travel', '#adventure', '#wanderlust', '#explore', '#destinations']
            },
            'food': {
                'name': 'Food & Recipes',
                'keywords': ['recipes', 'cooking', 'foodie', 'cuisine', 'delicious', 'ingredients'],
                'tone': 'appetizing, friendly',
                'hashtags': ['#food', '#cooking', '#recipe', '#foodie', '#delicious']
            }
        }
        
        # Platform-specific configurations
        self.platform_configs = {
            'twitter': {
                'max_length': 280,
                'style': 'concise, punchy',
                'hashtag_limit': 2
            },
            'facebook': {
                'max_length': 2000,
                'style': 'engaging, story-driven',
                'hashtag_limit': 3
            },
            'instagram': {
                'max_length': 2200,
                'style': 'visual-focused, inspiring',
                'hashtag_limit': 10
            },
            'linkedin': {
                'max_length': 3000,
                'style': 'professional, thought-leadership',
                'hashtag_limit': 3
            },
            'youtube': {
                'max_length': 5000,
                'style': 'descriptive, engaging',
                'hashtag_limit': 5
            }
        }
    
    def generate_content(self, domain: str, platform: str, custom_prompt: str = None, 
                        tone: str = None, target_audience: str = None) -> Dict:
        """Generate content for specific domain and platform"""
        try:
            # Get domain configuration
            domain_config = self.content_domains.get(domain.lower())
            if not domain_config:
                raise ValueError(f"Unsupported domain: {domain}")
            
            # Get platform configuration
            platform_config = self.platform_configs.get(platform.lower())
            if not platform_config:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Build prompt
            prompt = self._build_content_prompt(
                domain_config, platform_config, custom_prompt, tone, target_audience
            )
            
            # Try Mistral first, fallback to Groq
            content = self._generate_with_mistral(prompt)
            if not content:
                content = self._generate_with_groq(prompt)
            
            if not content:
                raise Exception("Both AI services failed to generate content")
            
            # Process and optimize content
            processed_content = self._process_generated_content(
                content, domain_config, platform_config, platform
            )
            
            # Add performance prediction
            performance_score = self._predict_performance(processed_content, domain, platform)
            
            result = {
                'content': processed_content['text'],
                'hashtags': processed_content['hashtags'],
                'domain': domain,
                'platform': platform,
                'character_count': len(processed_content['text']),
                'performance_prediction': performance_score,
                'generated_at': datetime.utcnow().isoformat(),
                'ai_provider': content.get('provider', 'mistral')
            }
            
            return result
            
        except Exception as e:
            current_app.logger.error(f'Content generation error: {str(e)}')
            raise e
    
    def generate_bulk_content(self, domain: str, platforms: List[str], count: int = 5) -> List[Dict]:
        """Generate multiple content pieces for multiple platforms"""
        try:
            results = []
            
            for platform in platforms:
                for i in range(count):
                    try:
                        content = self.generate_content(domain, platform)
                        results.append(content)
                    except Exception as e:
                        current_app.logger.error(f'Bulk content generation error for {platform}: {str(e)}')
                        continue
            
            return results
            
        except Exception as e:
            current_app.logger.error(f'Bulk content generation error: {str(e)}')
            return []
    
    def _build_content_prompt(self, domain_config: Dict, platform_config: Dict, 
                             custom_prompt: str = None, tone: str = None, 
                             target_audience: str = None) -> str:
        """Build AI prompt for content generation"""
        
        keywords = ', '.join(domain_config['keywords'][:5])
        content_tone = tone or domain_config['tone']
        max_length = platform_config['max_length']
        style = platform_config['style']
        
        base_prompt = f"""
        Create engaging social media content for {domain_config['name']} domain.
        
        Requirements:
        - Topic area: {domain_config['name']} ({keywords})
        - Platform: Optimized for {style}
        - Tone: {content_tone}
        - Maximum length: {max_length} characters
        - Target audience: {target_audience or 'General audience interested in ' + domain_config['name'].lower()}
        
        Content should be:
        - Engaging and shareable
        - Authentic and relatable
        - Include a clear call-to-action
        - Avoid controversial topics
        - Be original and creative
        """
        
        if custom_prompt:
            base_prompt += f"\n\nAdditional requirements: {custom_prompt}"
        
        base_prompt += f"\n\nGenerate ONLY the social media post text, no explanations or additional formatting."
        
        return base_prompt
    
    def _generate_with_mistral(self, prompt: str) -> Optional[Dict]:
        """Generate content using Mistral AI"""
        try:
            if not self.mistral_api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {self.mistral_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'mistral-medium',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
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
                return {
                    'text': content,
                    'provider': 'mistral'
                }
            else:
                current_app.logger.error(f'Mistral API error: {response.status_code} - {response.text}')
                return None
                
        except Exception as e:
            current_app.logger.error(f'Mistral generation error: {str(e)}')
            return None
    
    def _generate_with_groq(self, prompt: str) -> Optional[Dict]:
        """Generate content using Groq"""
        try:
            if not self.groq_api_key:
                return None
            
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'mixtral-8x7b-32768',
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 500,
                'temperature': 0.7
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                return {
                    'text': content,
                    'provider': 'groq'
                }
            else:
                current_app.logger.error(f'Groq API error: {response.status_code} - {response.text}')
                return None
                
        except Exception as e:
            current_app.logger.error(f'Groq generation error: {str(e)}')
            return None
    
    def _process_generated_content(self, content: Dict, domain_config: Dict, 
                                  platform_config: Dict, platform: str) -> Dict:
        """Process and optimize generated content"""
        text = content['text']
        
        # Remove quotes if AI added them
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        
        # Ensure it fits platform limits
        max_length = platform_config['max_length']
        if len(text) > max_length:
            # Truncate at last complete sentence or word
            truncated = text[:max_length]
            last_period = truncated.rfind('.')
            last_space = truncated.rfind(' ')
            
            if last_period > max_length * 0.8:  # If period is near end
                text = truncated[:last_period + 1]
            elif last_space > max_length * 0.8:  # If space is near end
                text = truncated[:last_space] + '...'
            else:
                text = truncated + '...'
        
        # Generate hashtags
        hashtags = self._generate_hashtags(domain_config, platform_config, platform)
        
        return {
            'text': text,
            'hashtags': hashtags
        }
    
    def _generate_hashtags(self, domain_config: Dict, platform_config: Dict, platform: str) -> List[str]:
        """Generate relevant hashtags"""
        base_hashtags = domain_config['hashtags']
        hashtag_limit = platform_config['hashtag_limit']
        
        # Select hashtags based on platform limits
        if len(base_hashtags) <= hashtag_limit:
            return base_hashtags
        
        # For platforms with higher limits, add more specific hashtags
        additional_hashtags = {
            'tech': ['#startup', '#coding', '#digital', '#software', '#data'],
            'memes': ['#lol', '#trending', '#relatable', '#mood', '#weekend'],
            'business': ['#success', '#motivation', '#goals', '#growth', '#mindset'],
            'lifestyle': ['#life', '#inspiration', '#motivation', '#positive', '#mindset'],
            'fitness': ['#gym', '#training', '#strength', '#cardio', '#healthy'],
            'finance': ['#trading', '#investment', '#portfolio', '#financial', '#savings'],
            'travel': ['#vacation', '#trip', '#photography', '#nature', '#culture'],
            'food': ['#chef', '#homecooking', '#yummy', '#ingredients', '#kitchen']
        }
        
        domain_key = list(domain_config.keys())[0] if domain_config else 'tech'
        extra_hashtags = additional_hashtags.get(domain_key, [])
        
        all_hashtags = base_hashtags + extra_hashtags
        
        # Select random hashtags up to limit
        return random.sample(all_hashtags, min(hashtag_limit, len(all_hashtags)))
    
    def _predict_performance(self, content: Dict, domain: str, platform: str) -> Dict:
        """Predict content performance using AI heuristics"""
        text = content['text']
        hashtags = content['hashtags']
        
        # Basic scoring factors
        score_factors = {
            'length_score': self._score_content_length(text, platform),
            'engagement_score': self._score_engagement_potential(text),
            'hashtag_score': self._score_hashtag_usage(hashtags, platform),
            'readability_score': self._score_readability(text),
            'trending_score': self._score_trending_potential(text, domain)
        }
        
        # Calculate weighted overall score
        weights = {
            'length_score': 0.15,
            'engagement_score': 0.30,
            'hashtag_score': 0.20,
            'readability_score': 0.20,
            'trending_score': 0.15
        }
        
        overall_score = sum(score * weights[factor] for factor, score in score_factors.items())
        
        # Convert to 0-100 scale
        overall_score = int(overall_score * 100)
        
        # Predict engagement ranges based on score
        if overall_score >= 85:
            engagement_prediction = "High (500+ interactions)"
        elif overall_score >= 70:
            engagement_prediction = "Good (100-500 interactions)"
        elif overall_score >= 50:
            engagement_prediction = "Average (50-100 interactions)"
        else:
            engagement_prediction = "Low (<50 interactions)"
        
        return {
            'overall_score': overall_score,
            'engagement_prediction': engagement_prediction,
            'score_breakdown': score_factors,
            'best_posting_times': self._suggest_posting_times(platform),
            'improvement_tips': self._generate_improvement_tips(score_factors)
        }
    
    def _score_content_length(self, text: str, platform: str) -> float:
        """Score content based on optimal length for platform"""
        length = len(text)
        
        optimal_lengths = {
            'twitter': (50, 280),
            'facebook': (100, 400),
            'instagram': (125, 300),
            'linkedin': (150, 500),
            'youtube': (200, 1000)
        }
        
        if platform not in optimal_lengths:
            return 0.7
        
        min_optimal, max_optimal = optimal_lengths[platform]
        
        if min_optimal <= length <= max_optimal:
            return 1.0
        elif length < min_optimal:
            return max(0.3, length / min_optimal)
        else:
            # Penalize overly long content
            return max(0.3, 1.0 - ((length - max_optimal) / max_optimal))
    
    def _score_engagement_potential(self, text: str) -> float:
        """Score based on engagement-driving elements"""
        score = 0.5  # Base score
        
        engagement_indicators = [
            ('?', 0.1),  # Questions
            ('!', 0.05), # Exclamations
            ('you', 0.1), # Direct address
            ('your', 0.05),
            ('tips', 0.05),
            ('how to', 0.1),
            ('secret', 0.05),
            ('amazing', 0.05),
            ('incredible', 0.05),
            ('must', 0.05),
            ('now', 0.05)
        ]
        
        text_lower = text.lower()
        for indicator, points in engagement_indicators:
            if indicator in text_lower:
                score += points
        
        return min(1.0, score)
    
    def _score_hashtag_usage(self, hashtags: List[str], platform: str) -> float:
        """Score hashtag usage"""
        if not hashtags:
            return 0.3
        
        optimal_counts = {
            'twitter': 2,
            'facebook': 3,
            'instagram': 8,
            'linkedin': 3,
            'youtube': 5
        }
        
        optimal = optimal_counts.get(platform, 3)
        actual = len(hashtags)
        
        if actual == optimal:
            return 1.0
        elif actual < optimal:
            return actual / optimal
        else:
            return max(0.5, 1.0 - ((actual - optimal) / optimal))
    
    def _score_readability(self, text: str) -> float:
        """Score readability using simple metrics"""
        words = text.split()
        sentences = text.split('.')
        
        if not words or not sentences:
            return 0.5
        
        avg_words_per_sentence = len(words) / len(sentences)
        avg_word_length = sum(len(word) for word in words) / len(words)
        
        # Optimal ranges for social media
        if 5 <= avg_words_per_sentence <= 15 and 3 <= avg_word_length <= 6:
            return 1.0
        elif 3 <= avg_words_per_sentence <= 20 and 2 <= avg_word_length <= 8:
            return 0.8
        else:
            return 0.6
    
    def _score_trending_potential(self, text: str, domain: str) -> float:
        """Score based on trending potential"""
        trending_words = {
            'tech': ['AI', 'automation', 'future', 'innovation', 'breakthrough'],
            'memes': ['viral', 'trending', 'mood', 'relatable', 'everyone'],
            'business': ['growth', 'success', 'entrepreneur', 'mindset', 'goals'],
            'lifestyle': ['wellness', 'balance', 'mindful', 'self-care', 'positive'],
            'fitness': ['transformation', 'results', 'strength', 'challenge', 'journey'],
            'finance': ['investment', 'wealth', 'portfolio', 'passive income', 'financial freedom'],
            'travel': ['adventure', 'wanderlust', 'bucket list', 'hidden gems', 'culture'],
            'food': ['recipe', 'delicious', 'homemade', 'fresh', 'comfort food']
        }
        
        domain_trends = trending_words.get(domain, [])
        text_lower = text.lower()
        
        trend_score = sum(0.1 for trend in domain_trends if trend.lower() in text_lower)
        return min(1.0, 0.5 + trend_score)
    
    def _suggest_posting_times(self, platform: str) -> List[str]:
        """Suggest optimal posting times for platform"""
        posting_times = {
            'twitter': ['9:00 AM', '1:00 PM', '5:00 PM'],
            'facebook': ['1:00 PM', '3:00 PM', '8:00 PM'],
            'instagram': ['11:00 AM', '2:00 PM', '7:00 PM'],
            'linkedin': ['8:00 AM', '12:00 PM', '5:00 PM'],
            'youtube': ['2:00 PM', '8:00 PM', '9:00 PM']
        }
        
        return posting_times.get(platform, ['9:00 AM', '1:00 PM', '6:00 PM'])
    
    def _generate_improvement_tips(self, score_factors: Dict) -> List[str]:
        """Generate improvement tips based on scores"""
        tips = []
        
        if score_factors.get('engagement_score', 0) < 0.7:
            tips.append("Add questions or call-to-actions to boost engagement")
        
        if score_factors.get('hashtag_score', 0) < 0.7:
            tips.append("Optimize hashtag count for better reach")
        
        if score_factors.get('readability_score', 0) < 0.7:
            tips.append("Use shorter sentences and simpler words")
        
        if score_factors.get('trending_score', 0) < 0.7:
            tips.append("Include trending keywords for your domain")
        
        if not tips:
            tips.append("Great content! Consider posting at suggested optimal times")
        
        return tips

# Initialize the content generator
content_generator = AIContentGenerator()