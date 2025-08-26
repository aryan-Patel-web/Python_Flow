"""
AI Content Generation Service for VelocityPost.ai
Uses Mistral AI + Groq as fallback for generating social media content
"""

import os
import json
import random
import asyncio
import aiohttp
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class AIContentGenerator:
    """AI-powered content generation for social media platforms"""
    
    def __init__(self):
        self.mistral_api_key = os.getenv('MISTRAL_API_KEY')
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # API Endpoints
        self.mistral_url = "https://api.mistral.ai/v1/chat/completions"
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.openai_url = "https://api.openai.com/v1/chat/completions"
        
        # Content domains and their characteristics
        self.content_domains = {
            'tech': {
                'name': 'Technology & Innovation',
                'topics': [
                    'AI and Machine Learning', 'Web Development', 'Mobile Apps', 
                    'Cloud Computing', 'Cybersecurity', 'Blockchain', 'IoT', 
                    'Software Development', 'Tech News', 'Programming Tips'
                ],
                'tone': 'informative, cutting-edge, professional',
                'hashtags': ['#tech', '#innovation', '#AI', '#programming', '#development', '#software']
            },
            'memes': {
                'name': 'Memes & Humor',
                'topics': [
                    'Programming Memes', 'Work From Home', 'Developer Life',
                    'Tech Humor', 'Internet Culture', 'Funny Observations',
                    'Relatable Content', 'Pop Culture', 'Social Media Trends'
                ],
                'tone': 'funny, relatable, casual, witty',
                'hashtags': ['#memes', '#humor', '#funny', '#relatable', '#lol', '#comedy']
            },
            'business': {
                'name': 'Business & Entrepreneurship',
                'topics': [
                    'Startup Tips', 'Leadership', 'Marketing Strategies',
                    'Productivity', 'Business Growth', 'Success Stories',
                    'Industry Insights', 'Networking', 'Business News'
                ],
                'tone': 'professional, motivational, authoritative',
                'hashtags': ['#business', '#entrepreneur', '#startup', '#leadership', '#success', '#growth']
            },
            'lifestyle': {
                'name': 'Lifestyle & Personal Development',
                'topics': [
                    'Self Improvement', 'Work-Life Balance', 'Mental Health',
                    'Productivity Tips', 'Motivation', 'Health & Wellness',
                    'Travel', 'Hobbies', 'Personal Growth'
                ],
                'tone': 'inspiring, personal, encouraging',
                'hashtags': ['#lifestyle', '#motivation', '#selfcare', '#wellness', '#growth', '#inspiration']
            },
            'fitness': {
                'name': 'Health & Fitness',
                'topics': [
                    'Workout Tips', 'Nutrition', 'Mental Health',
                    'Fitness Motivation', 'Healthy Recipes', 'Exercise Routines',
                    'Wellness Tips', 'Sports', 'Recovery'
                ],
                'tone': 'energetic, motivational, health-focused',
                'hashtags': ['#fitness', '#health', '#workout', '#nutrition', '#wellness', '#motivation']
            },
            'finance': {
                'name': 'Finance & Investment',
                'topics': [
                    'Personal Finance', 'Investment Tips', 'Cryptocurrency',
                    'Stock Market', 'Saving Money', 'Financial Planning',
                    'Economic News', 'Budgeting', 'Passive Income'
                ],
                'tone': 'informative, trustworthy, analytical',
                'hashtags': ['#finance', '#investing', '#money', '#crypto', '#stocks', '#financialfreedom']
            },
            'travel': {
                'name': 'Travel & Adventure',
                'topics': [
                    'Travel Tips', 'Destinations', 'Culture',
                    'Adventure Stories', 'Budget Travel', 'Solo Travel',
                    'Photography', 'Local Experiences', 'Travel Hacks'
                ],
                'tone': 'adventurous, inspiring, descriptive',
                'hashtags': ['#travel', '#adventure', '#explore', '#wanderlust', '#culture', '#photography']
            },
            'food': {
                'name': 'Food & Cooking',
                'topics': [
                    'Recipes', 'Cooking Tips', 'Food Photography',
                    'Restaurant Reviews', 'Healthy Eating', 'Baking',
                    'International Cuisine', 'Food Trends', 'Kitchen Hacks'
                ],
                'tone': 'appetizing, descriptive, enthusiastic',
                'hashtags': ['#food', '#cooking', '#recipe', '#foodie', '#delicious', '#homemade']
            }
        }
        
        # Platform-specific requirements
        self.platform_specs = {
            'instagram': {
                'max_length': 2200,
                'optimal_length': 150,
                'hashtag_limit': 30,
                'style': 'visual-first, engaging, hashtag-heavy'
            },
            'facebook': {
                'max_length': 63206,
                'optimal_length': 250,
                'hashtag_limit': 10,
                'style': 'conversational, story-telling, engaging'
            },
            'twitter': {
                'max_length': 280,
                'optimal_length': 250,
                'hashtag_limit': 5,
                'style': 'concise, witty, news-worthy'
            },
            'linkedin': {
                'max_length': 3000,
                'optimal_length': 500,
                'hashtag_limit': 10,
                'style': 'professional, insightful, industry-focused'
            },
            'youtube': {
                'max_length': 1000,
                'optimal_length': 200,
                'hashtag_limit': 15,
                'style': 'descriptive, engaging, SEO-friendly'
            },
            'pinterest': {
                'max_length': 500,
                'optimal_length': 100,
                'hashtag_limit': 20,
                'style': 'descriptive, keyword-rich, actionable'
            }
        }
    
    async def generate_content(
        self,
        domain: str,
        platform: str,
        content_type: str = 'post',
        custom_prompt: Optional[str] = None,
        creativity_level: int = 75,
        include_hashtags: bool = True,
        include_emojis: bool = True,
        follow_trends: bool = True
    ) -> Dict:
        """Generate AI content for specific domain and platform"""
        
        try:
            # Validate inputs
            if domain not in self.content_domains:
                raise ValueError(f"Unsupported domain: {domain}")
            
            if platform not in self.platform_specs:
                raise ValueError(f"Unsupported platform: {platform}")
            
            # Get domain and platform specs
            domain_config = self.content_domains[domain]
            platform_config = self.platform_specs[platform]
            
            # Build content generation prompt
            prompt = self._build_content_prompt(
                domain_config=domain_config,
                platform_config=platform_config,
                content_type=content_type,
                custom_prompt=custom_prompt,
                creativity_level=creativity_level,
                include_hashtags=include_hashtags,
                include_emojis=include_emojis,
                follow_trends=follow_trends
            )
            
            # Generate content using AI services (try Mistral first, then Groq, then OpenAI)
            content_text = await self._generate_with_fallback(prompt, creativity_level)
            
            # Post-process and optimize content
            optimized_content = self._optimize_content(
                content=content_text,
                platform=platform,
                domain=domain,
                include_hashtags=include_hashtags
            )
            
            # Generate performance prediction
            performance_prediction = self._predict_performance(
                content=optimized_content,
                domain=domain,
                platform=platform
            )
            
            # Generate suggested media (if applicable)
            media_suggestions = self._generate_media_suggestions(
                content=optimized_content,
                domain=domain,
                platform=platform
            )
            
            return {
                'content': optimized_content,
                'domain': domain,
                'platform': platform,
                'content_type': content_type,
                'performance_prediction': performance_prediction,
                'media_suggestions': media_suggestions,
                'metadata': {
                    'word_count': len(optimized_content.split()),
                    'character_count': len(optimized_content),
                    'hashtag_count': len([word for word in optimized_content.split() if word.startswith('#')]),
                    'emoji_count': len([char for char in optimized_content if char in '😀😃😄😁😆😅😂🤣☺️😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏😒😞😔😟😕🙁☹️😣😖😫😩🥺😢😭😤😠😡🤬🤯😳🥵🥶😱😨😰😥😓🤗🤔🤭🤫🤥😶😐😑😬🙄😯😦😧😮😲🥱😴🤤😪😵🤐🥴🤢🤮🤧😷🤒🤕🤑🤠😈👿👹👺🤡💩👻💀☠️👽👾🤖🎃😺😸😹😻😼😽🙀😿😾']),
                    'generated_at': datetime.utcnow().isoformat(),
                    'ai_model_used': self._get_last_used_model(),
                    'creativity_level': creativity_level
                }
            }
            
        except Exception as e:
            logger.error(f"Content generation failed for {domain}/{platform}: {e}")
            raise Exception(f"Content generation failed: {str(e)}")
    
    def _build_content_prompt(
        self,
        domain_config: Dict,
        platform_config: Dict,
        content_type: str,
        custom_prompt: Optional[str],
        creativity_level: int,
        include_hashtags: bool,
        include_emojis: bool,
        follow_trends: bool
    ) -> str:
        """Build comprehensive prompt for AI content generation"""
        
        # Get current trends if requested
        trending_topics = self._get_trending_topics(domain_config['name']) if follow_trends else []
        
        # Base prompt structure
        prompt = f"""You are an expert social media content creator specializing in {domain_config['name']} content for {platform_config.get('style', 'social media')}.

CONTENT REQUIREMENTS:
- Platform: {platform_config.get('style', 'general social media')}
- Domain: {domain_config['name']} ({domain_config['tone']})
- Content Type: {content_type}
- Max Length: {platform_config['max_length']} characters
- Optimal Length: {platform_config['optimal_length']} characters
- Creativity Level: {creativity_level}/100

CONTENT GUIDELINES:
- Write in a {domain_config['tone']} tone
- Target topics: {', '.join(random.sample(domain_config['topics'], min(3, len(domain_config['topics']))))}
- Make it engaging and authentic
- Ensure it provides value to the audience
- Use natural, conversational language"""

        if custom_prompt:
            prompt += f"\n- Custom Requirements: {custom_prompt}"

        if trending_topics:
            prompt += f"\n- Consider incorporating these trending topics: {', '.join(trending_topics[:3])}"

        if include_emojis:
            prompt += "\n- Include relevant emojis (2-5 emojis, strategically placed)"

        if include_hashtags:
            hashtag_count = min(platform_config.get('hashtag_limit', 10), 8)
            prompt += f"\n- Include {hashtag_count} relevant hashtags from: {', '.join(domain_config['hashtags'])}"

        # Platform-specific instructions
        platform_instructions = {
            'instagram': "Focus on visual storytelling. Use line breaks for readability. Include a call-to-action.",
            'facebook': "Create engaging stories that encourage comments and shares. Ask questions to boost engagement.",
            'twitter': "Be concise and impactful. Use thread-worthy content or standalone tweets. Consider current events.",
            'linkedin': "Professional tone with industry insights. Share valuable knowledge or career advice.",
            'youtube': "Create compelling descriptions that improve discoverability. Include relevant keywords.",
            'pinterest': "Use descriptive, keyword-rich text that helps with search. Focus on actionable content."
        }

        if platform_instructions.get(platform_config.get('platform')):
            prompt += f"\n- Platform-specific: {platform_instructions[platform_config.get('platform')]}"

        prompt += "\n\nGenerate ONE high-quality social media post that follows all these requirements. Return only the post content, no explanations or meta-commentary."

        return prompt
    
    async def _generate_with_fallback(self, prompt: str, creativity_level: int) -> str:
        """Generate content with AI service fallback (Mistral -> Groq -> OpenAI)"""
        
        # Convert creativity level to temperature (0.1 to 1.0)
        temperature = max(0.1, min(1.0, creativity_level / 100))
        
        # Try Mistral first
        if self.mistral_api_key:
            try:
                content = await self._call_mistral(prompt, temperature)
                if content:
                    self._last_used_model = 'mistral'
                    return content
            except Exception as e:
                logger.warning(f"Mistral API failed: {e}")
        
        # Fallback to Groq
        if self.groq_api_key:
            try:
                content = await self._call_groq(prompt, temperature)
                if content:
                    self._last_used_model = 'groq'
                    return content
            except Exception as e:
                logger.warning(f"Groq API failed: {e}")
        
        # Final fallback to OpenAI
        if self.openai_api_key:
            try:
                content = await self._call_openai(prompt, temperature)
                if content:
                    self._last_used_model = 'openai'
                    return content
            except Exception as e:
                logger.warning(f"OpenAI API failed: {e}")
        
        # If all APIs fail, return a template-based content
        logger.error("All AI services failed, using template fallback")
        self._last_used_model = 'template'
        return self._generate_template_content(prompt)
    
    async def _call_mistral(self, prompt: str, temperature: float) -> str:
        """Call Mistral AI API"""
        headers = {
            'Authorization': f'Bearer {self.mistral_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'mistral-large-latest',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.mistral_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"Mistral API error {response.status}: {error_text}")
    
    async def _call_groq(self, prompt: str, temperature: float) -> str:
        """Call Groq Cloud API"""
        headers = {
            'Authorization': f'Bearer {self.groq_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'mixtral-8x7b-32768',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.groq_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"Groq API error {response.status}: {error_text}")
    
    async def _call_openai(self, prompt: str, temperature: float) -> str:
        """Call OpenAI API (fallback)"""
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'gpt-3.5-turbo',
            'messages': [
                {'role': 'user', 'content': prompt}
            ],
            'temperature': temperature,
            'max_tokens': 1000,
            'top_p': 0.9
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(self.openai_url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content'].strip()
                else:
                    error_text = await response.text()
                    raise Exception(f"OpenAI API error {response.status}: {error_text}")
    
    def _generate_template_content(self, prompt: str) -> str:
        """Generate template-based content as final fallback"""
        templates = {
            'tech': [
                "🚀 Exciting developments in technology today! The future of innovation is here. What tech trends are you most excited about? #tech #innovation #future",
                "💻 Pro tip: Always keep learning new technologies. The tech industry moves fast, and staying updated is key to success! #programming #learning #tech",
                "🔧 Building something amazing with code today! There's nothing quite like solving complex problems with elegant solutions. #coding #development #programming"
            ],
            'business': [
                "📈 Success in business comes down to one thing: providing real value to your customers. Focus on solving problems, not just making sales. #business #entrepreneur #success",
                "💡 Great leaders don't create followers, they create more leaders. Invest in your team's growth and watch your business thrive! #leadership #teamwork #growth",
                "🎯 Setting clear goals is the first step to achieving them. What's your biggest business goal for this month? #goals #business #motivation"
            ],
            'lifestyle': [
                "🌟 Remember: self-care isn't selfish, it's essential. Take time for yourself today - you deserve it! #selfcare #wellness #motivation",
                "✨ Small daily improvements lead to stunning long-term results. What's one thing you can do today to better yourself? #growth #improvement #mindset",
                "🙏 Gratitude changes everything. What are three things you're grateful for today? #gratitude #positivity #mindfulness"
            ]
        }
        
        # Extract domain from prompt or use general
        domain = 'business'  # Default
        for d in templates.keys():
            if d in prompt.lower():
                domain = d
                break
        
        return random.choice(templates.get(domain, templates['business']))
    
    def _optimize_content(self, content: str, platform: str, domain: str, include_hashtags: bool) -> str:
        """Post-process and optimize generated content"""
        
        # Clean up the content
        content = content.strip()
        
        # Remove any unwanted prefixes/suffixes
        unwanted_starts = ["Here's a", "Here is a", "Caption:", "Post:", "Content:"]
        for start in unwanted_starts:
            if content.lower().startswith(start.lower()):
                content = content[len(start):].strip()
        
        # Ensure proper length for platform
        platform_config = self.platform_specs[platform]
        max_length = platform_config['max_length']
        
        if len(content) > max_length:
            # Truncate smartly (preserve hashtags if possible)
            if include_hashtags and '#' in content:
                # Split content and hashtags
                parts = content.split('#')
                main_content = parts[0].strip()
                hashtags = ['#' + part.split()[0] for part in parts[1:] if part.strip()]
                hashtag_text = ' '.join(hashtags)
                
                # Calculate available space for main content
                available_space = max_length - len(hashtag_text) - 2  # 2 for space
                
                if available_space > 50:  # Ensure minimum content length
                    content = main_content[:available_space].strip() + ' ' + hashtag_text
                else:
                    content = content[:max_length]
            else:
                content = content[:max_length]
        
        # Platform-specific optimizations
        if platform == 'instagram':
            # Ensure line breaks for readability
            if len(content) > 100 and '\n' not in content[:100]:
                sentences = content.split('. ')
                if len(sentences) > 1:
                    mid_point = len(sentences) // 2
                    content = '. '.join(sentences[:mid_point]) + '.\n\n' + '. '.join(sentences[mid_point:])
        
        elif platform == 'twitter':
            # Ensure it fits in a tweet
            if len(content) > 280:
                content = content[:277] + '...'
        
        elif platform == 'linkedin':
            # Add professional formatting
            if not content.startswith('🔥') and not content.startswith('💡'):
                professional_emojis = ['💡', '🚀', '📈', '🎯', '⭐']
                content = random.choice(professional_emojis) + ' ' + content
        
        return content
    
    def _predict_performance(self, content: str, domain: str, platform: str) -> Dict:
        """Predict content performance using various metrics"""
        
        score = 50  # Base score
        factors = []
        
        # Length optimization
        platform_config = self.platform_specs[platform]
        optimal_length = platform_config['optimal_length']
        content_length = len(content)
        
        if abs(content_length - optimal_length) <= optimal_length * 0.2:
            score += 15
            factors.append("Optimal length")
        elif content_length < optimal_length * 0.5:
            score -= 10
            factors.append("Too short")
        elif content_length > platform_config['max_length'] * 0.8:
            score -= 5
            factors.append("Quite long")
        
        # Hashtag analysis
        hashtag_count = len([word for word in content.split() if word.startswith('#')])
        optimal_hashtags = platform_config.get('hashtag_limit', 5)
        
        if 0 < hashtag_count <= optimal_hashtags:
            score += 10
            factors.append("Good hashtag usage")
        elif hashtag_count > optimal_hashtags:
            score -= 5
            factors.append("Too many hashtags")
        
        # Emoji analysis
        emoji_count = len([char for char in content if char in '😀😃😄😁😆😅😂🤣☺️😊😇🙂🙃😉😌😍🥰😘😗😙😚😋😛😝😜🤪🤨🧐🤓😎🤩🥳😏'])
        if 1 <= emoji_count <= 5:
            score += 8
            factors.append("Good emoji usage")
        elif emoji_count > 8:
            score -= 5
            factors.append("Too many emojis")
        
        # Engagement triggers
        engagement_words = ['what', 'how', 'why', 'do you', 'what do you think', 'share', 'comment', 'thoughts', '?']
        if any(word in content.lower() for word in engagement_words):
            score += 12
            factors.append("Encourages engagement")
        
        # Call-to-action detection
        cta_words = ['check out', 'learn more', 'click', 'visit', 'follow', 'subscribe', 'join', 'download']
        if any(word in content.lower() for word in cta_words):
            score += 8
            factors.append("Includes call-to-action")
        
        # Domain-specific bonuses
        domain_config = self.content_domains[domain]
        domain_keywords = [topic.lower() for topic in domain_config['topics']]
        if any(keyword in content.lower() for keyword in domain_keywords[:5]):
            score += 10
            factors.append("Relevant to domain")
        
        # Platform-specific bonuses
        if platform == 'linkedin' and any(word in content.lower() for word in ['professional', 'career', 'business', 'industry']):
            score += 8
            factors.append("Professional content")
        
        if platform == 'instagram' and '\n' in content:
            score += 5
            factors.append("Good formatting")
        
        # Trending topics bonus (simplified)
        trending_keywords = ['AI', 'trending', 'latest', 'new', '2024', '2025', 'update']
        if any(word in content for word in trending_keywords):
            score += 7
            factors.append("Includes trending topics")
        
        # Cap the score
        score = max(10, min(100, score))
        
        return {
            'score': score,
            'grade': self._get_performance_grade(score),
            'factors': factors,
            'predicted_engagement': {
                'likes': self._predict_likes(score, platform),
                'comments': self._predict_comments(score, platform),
                'shares': self._predict_shares(score, platform)
            },
            'recommendations': self._get_recommendations(score, content, platform)
        }
    
    def _get_performance_grade(self, score: int) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B+'
        elif score >= 60:
            return 'B'
        elif score >= 50:
            return 'C'
        else:
            return 'D'
    
    def _predict_likes(self, score: int, platform: str) -> int:
        """Predict likes based on score and platform"""
        base_likes = {
            'instagram': 50,
            'facebook': 25,
            'twitter': 30,
            'linkedin': 15,
            'youtube': 20,
            'pinterest': 10
        }
        
        base = base_likes.get(platform, 25)
        multiplier = score / 50
        return int(base * multiplier * random.uniform(0.8, 1.5))
    
    def _predict_comments(self, score: int, platform: str) -> int:
        """Predict comments based on score and platform"""
        base_comments = {
            'instagram': 8,
            'facebook': 12,
            'twitter': 5,
            'linkedin': 3,
            'youtube': 6,
            'pinterest': 2
        }
        
        base = base_comments.get(platform, 5)
        multiplier = score / 50
        return int(base * multiplier * random.uniform(0.7, 1.3))
    
    def _predict_shares(self, score: int, platform: str) -> int:
        """Predict shares based on score and platform"""
        base_shares = {
            'instagram': 3,
            'facebook': 8,
            'twitter': 15,
            'linkedin': 5,
            'youtube': 2,
            'pinterest': 20
        }
        
        base = base_shares.get(platform, 5)
        multiplier = score / 50
        return int(base * multiplier * random.uniform(0.6, 1.4))
    
    def _get_recommendations(self, score: int, content: str, platform: str) -> List[str]:
        """Get content improvement recommendations"""
        recommendations = []
        
        if score < 60:
            recommendations.append("Consider adding more engaging elements like questions or call-to-actions")
        
        if '#' not in content:
            recommendations.append("Add relevant hashtags to increase discoverability")
        
        hashtag_count = len([word for word in content.split() if word.startswith('#')])
        if hashtag_count > self.platform_specs[platform].get('hashtag_limit', 10):
            recommendations.append("Reduce the number of hashtags for better engagement")
        
        if '?' not in content and platform in ['facebook', 'instagram']:
            recommendations.append("Ask a question to encourage comments and engagement")
        
        if len(content) < self.platform_specs[platform]['optimal_length'] * 0.6:
            recommendations.append("Consider expanding the content to provide more value")
        
        emoji_count = len([char for char in content if char in '😀😃😄😁😆😅'])
        if emoji_count == 0 and platform in ['instagram', 'facebook']:
            recommendations.append("Add 1-2 relevant emojis to make the content more engaging")
        
        return recommendations[:3]  # Return top 3 recommendations
    
    def _generate_media_suggestions(self, content: str, domain: str, platform: str) -> Dict:
        """Generate media suggestions based on content"""
        
        suggestions = {
            'images': [],
            'videos': [],
            'graphics': []
        }
        
        # Domain-specific media suggestions
        if domain == 'tech':
            suggestions['images'] = [
                'Code snippet screenshots',
                'Tech product photos',
                'Infographic about tech trends',
                'Behind-the-scenes development'
            ]
            suggestions['videos'] = [
                'Coding timelapse',
                'Product demo',
                'Tech explanation video'
            ]
        
        elif domain == 'business':
            suggestions['images'] = [
                'Professional headshots',
                'Office/workspace photos',
                'Chart or graph visuals',
                'Team collaboration shots'
            ]
            suggestions['videos'] = [
                'Behind-the-scenes business',
                'Quick tip videos',
                'Day-in-the-life content'
            ]
        
        elif domain == 'lifestyle':
            suggestions['images'] = [
                'Lifestyle photography',
                'Motivational quotes',
                'Personal moments',
                'Aesthetic flat lays'
            ]
            suggestions['videos'] = [
                'Morning routine',
                'Wellness tips',
                'Personal story content'
            ]
        
        # Platform-specific adjustments
        if platform == 'instagram':
            suggestions['graphics'].extend([
                'Instagram story templates',
                'Carousel post designs',
                'Quote graphics with brand colors'
            ])
        
        elif platform == 'pinterest':
            suggestions['graphics'].extend([
                'Vertical pin designs',
                'Step-by-step guides',
                'List-style graphics'
            ])
        
        return suggestions
    
    def _get_trending_topics(self, domain: str) -> List[str]:
        """Get trending topics for domain (simplified implementation)"""
        # In a real implementation, this would call trending APIs
        trending_by_domain = {
            'Technology & Innovation': ['AI automation', 'Web3', 'Sustainable tech', 'Remote work tools'],
            'Memes & Humor': ['Work from home', 'AI memes', 'Gen Z humor', 'Social media trends'],
            'Business & Entrepreneurship': ['Digital marketing', 'Startup funding', 'Remote teams', 'AI in business'],
            'Lifestyle & Personal Development': ['Mindfulness', 'Work-life balance', 'Digital detox', 'Productivity hacks'],
            'Health & Fitness': ['Mental health', 'Home workouts', 'Nutrition tips', 'Wellness trends'],
            'Finance & Investment': ['Cryptocurrency', 'Personal finance apps', 'Investment tips', 'Financial literacy'],
            'Travel & Adventure': ['Sustainable travel', 'Digital nomad life', 'Local experiences', 'Travel photography'],
            'Food & Cooking': ['Healthy recipes', 'Meal prep', 'International cuisine', 'Food photography']
        }
        
        return trending_by_domain.get(domain, [])
    
    def _get_last_used_model(self) -> str:
        """Get the last used AI model"""
        return getattr(self, '_last_used_model', 'unknown')
    
    async def generate_multiple_variants(
        self,
        domain: str,
        platform: str,
        count: int = 5,
        **kwargs
    ) -> List[Dict]:
        """Generate multiple content variants"""
        
        variants = []
        for i in range(count):
            try:
                # Slightly vary creativity for diversity
                creativity = kwargs.get('creativity_level', 75) + random.randint(-10, 10)
                creativity = max(10, min(100, creativity))
                
                variant_kwargs = {**kwargs, 'creativity_level': creativity}
                variant = await self.generate_content(domain, platform, **variant_kwargs)
                variants.append(variant)
                
                # Small delay to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.warning(f"Failed to generate variant {i+1}: {e}")
                continue
        
        return variants
    
    def get_domain_info(self, domain: str) -> Dict:
        """Get information about a content domain"""
        if domain not in self.content_domains:
            raise ValueError(f"Unsupported domain: {domain}")
        
        return self.content_domains[domain]
    
    def get_platform_info(self, platform: str) -> Dict:
        """Get information about a platform"""
        if platform not in self.platform_specs:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return self.platform_specs[platform]
    
    def get_supported_domains(self) -> List[Dict]:
        """Get list of supported content domains"""
        return [
            {
                'id': domain_id,
                'name': config['name'],
                'topics': config['topics'],
                'tone': config['tone']
            }
            for domain_id, config in self.content_domains.items()
        ]
    
    def get_supported_platforms(self) -> List[Dict]:
        """Get list of supported platforms"""
        return [
            {
                'id': platform_id,
                'max_length': config['max_length'],
                'optimal_length': config['optimal_length'],
                'style': config['style']
            }
            for platform_id, config in self.platform_specs.items()
        ]


# Global instance
ai_content_generator = AIContentGenerator()


# Async wrapper functions for use in Flask routes
def generate_content_sync(domain: str, platform: str, **kwargs) -> Dict:
    """Synchronous wrapper for content generation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            ai_content_generator.generate_content(domain, platform, **kwargs)
        )
        return result
    finally:
        loop.close()


def generate_multiple_variants_sync(domain: str, platform: str, count: int = 5, **kwargs) -> List[Dict]:
    """Synchronous wrapper for multiple variant generation"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            ai_content_generator.generate_multiple_variants(domain, platform, count, **kwargs)
        )
        return result
    finally:
        loop.close()


if __name__ == '__main__':
    # Test the AI content generator
    import asyncio
    
    async def test_generator():
        try:
            # Test content generation
            content = await ai_content_generator.generate_content(
                domain='tech',
                platform='instagram',
                creativity_level=80,
                include_hashtags=True,
                include_emojis=True
            )
            
            print("✅ Content Generation Test:")
            print(f"Content: {content['content']}")
            print(f"Performance Score: {content['performance_prediction']['score']}/100")
            print(f"AI Model Used: {content['metadata']['ai_model_used']}")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
    
    # Run test
    asyncio.run(test_generator())