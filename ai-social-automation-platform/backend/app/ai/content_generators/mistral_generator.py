# app/ai/content_generators/mistral_generator.py
import requests
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MistralGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.mistral.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_content(self, domain: str, platform: str, content_type: str = "post", **kwargs) -> Dict:
        """Generate content using Mistral AI"""
        try:
            prompt = self._build_prompt(domain, platform, content_type, **kwargs)
            
            payload = {
                "model": "mistral-medium",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 500),
                "temperature": kwargs.get('temperature', 0.7)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'content': content,
                    'platform': platform,
                    'domain': domain,
                    'content_type': content_type,
                    'provider': 'mistral',
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0)
                }
            else:
                logger.error(f"Mistral API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Mistral API error: {response.status_code}",
                    'provider': 'mistral'
                }
                
        except Exception as e:
            logger.error(f"Mistral generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'mistral'
            }
    
    def _build_prompt(self, domain: str, platform: str, content_type: str, **kwargs) -> str:
        """Build optimized prompt for Mistral"""
        
        platform_specs = {
            'instagram': 'Short, engaging caption with relevant hashtags (max 2200 chars)',
            'facebook': 'Engaging post that encourages interaction (max 500 words)',
            'youtube': 'Compelling title and description for video content',
            'twitter': 'Concise, impactful tweet (max 280 characters)',
            'linkedin': 'Professional, value-driven content for business audience'
        }
        
        domain_contexts = {
            'memes': 'Create funny, relatable content that will make people laugh and share',
            'tech_news': 'Share latest tech developments with insightful commentary',
            'coding_tips': 'Provide practical programming advice and tutorials',
            'lifestyle': 'Share inspiring content about health, wellness, and personal growth',
            'business': 'Offer valuable business insights and entrepreneurship advice',
            'motivational': 'Create inspiring, uplifting content that motivates people'
        }
        
        base_prompt = f"""
        You are an expert social media content creator specializing in {domain} content for {platform}.
        
        Domain Context: {domain_contexts.get(domain, f'Create engaging {domain} content')}
        Platform Requirements: {platform_specs.get(platform, 'Create engaging social media content')}
        
        Content Type: {content_type}
        
        Requirements:
        1. Make it engaging and shareable
        2. Include relevant hashtags where appropriate
        3. Match the tone and style of {platform}
        4. Focus on {domain} niche
        5. Encourage engagement (likes, comments, shares)
        
        Generate compelling {content_type} content now:
        """
        
        # Add specific instructions based on domain
        if domain == 'memes':
            base_prompt += "\nMake it funny and relatable. Include popular meme formats or trending topics."
        elif domain == 'tech_news':
            base_prompt += "\nInclude the latest tech trends. Be informative but accessible."
        elif domain == 'coding_tips':
            base_prompt += "\nProvide practical coding advice. Include code examples if relevant."
        
        return base_prompt.strip()

# app/ai/content_generators/groq_generator.py
import requests
import json
from typing import Dict
import logging

logger = logging.getLogger(__name__)

class GroqGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/openai/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def generate_content(self, domain: str, platform: str, content_type: str = "post", **kwargs) -> Dict:
        """Generate content using Groq AI"""
        try:
            prompt = self._build_prompt(domain, platform, content_type, **kwargs)
            
            payload = {
                "model": "mixtral-8x7b-32768",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get('max_tokens', 500),
                "temperature": kwargs.get('temperature', 0.7)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                return {
                    'success': True,
                    'content': content,
                    'platform': platform,
                    'domain': domain,
                    'content_type': content_type,
                    'provider': 'groq',
                    'tokens_used': result.get('usage', {}).get('total_tokens', 0)
                }
            else:
                logger.error(f"Groq API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': f"Groq API error: {response.status_code}",
                    'provider': 'groq'
                }
                
        except Exception as e:
            logger.error(f"Groq generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'provider': 'groq'
            }
    
    def _build_prompt(self, domain: str, platform: str, content_type: str, **kwargs) -> str:
        """Build optimized prompt for Groq"""
        return f"""
        Create engaging {domain} content for {platform}.
        
        Platform: {platform}
        Domain: {domain}
        Content Type: {content_type}
        
        Make it:
        - Engaging and shareable
        - Platform-appropriate
        - Domain-specific
        - Include relevant hashtags
        - Encourage interaction
        
        Generate {content_type} content:
        """

# app/ai/content_generators/base_generator.py
from typing import Dict, List
import logging
from .mistral_generator import MistralGenerator
from .groq_generator import GroqGenerator

logger = logging.getLogger(__name__)

class ContentGenerator:
    def __init__(self, mistral_api_key: str, groq_api_key: str):
        self.mistral = MistralGenerator(mistral_api_key) if mistral_api_key else None
        self.groq = GroqGenerator(groq_api_key) if groq_api_key else None
        self.fallback_chain = ['mistral', 'groq']
    
    def generate_content(self, domain: str, platform: str, content_type: str = "post", **kwargs) -> Dict:
        """Generate content with fallback chain"""
        
        for provider in self.fallback_chain:
            try:
                if provider == 'mistral' and self.mistral:
                    result = self.mistral.generate_content(domain, platform, content_type, **kwargs)
                elif provider == 'groq' and self.groq:
                    result = self.groq.generate_content(domain, platform, content_type, **kwargs)
                else:
                    continue
                
                if result.get('success'):
                    logger.info(f"Content generated successfully using {provider}")
                    return result
                else:
                    logger.warning(f"Content generation failed with {provider}: {result.get('error')}")
                    
            except Exception as e:
                logger.error(f"Error with {provider}: {str(e)}")
                continue
        
        # If all providers fail
        return {
            'success': False,
            'error': 'All AI providers failed to generate content',
            'providers_tried': self.fallback_chain
        }
    
    def generate_bulk_content(self, domains: List[str], platforms: List[str], count: int = 1) -> List[Dict]:
        """Generate multiple pieces of content"""
        results = []
        
        for domain in domains:
            for platform in platforms:
                for i in range(count):
                    result = self.generate_content(domain, platform)
                    if result.get('success'):
                        results.append(result)
        
        return results
    
    def optimize_for_platform(self, content: str, platform: str) -> str:
        """Optimize content for specific platform requirements"""
        platform_optimizations = {
            'twitter': lambda x: x[:250] + "..." if len(x) > 250 else x,
            'instagram': lambda x: x + "\n\n#" + " #".join(x.split()[:5]) if not "#" in x else x,
            'linkedin': lambda x: x if x.startswith("🔹") else "🔹 " + x,
            'facebook': lambda x: x + "\n\nWhat do you think? Let me know in the comments! 👇"
        }
        
        optimizer = platform_optimizations.get(platform, lambda x: x)
        return optimizer(content)