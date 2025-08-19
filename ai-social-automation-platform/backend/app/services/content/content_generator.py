from app.ai.content_generators.base_generator import ContentGenerator as BaseGenerator

class ContentGenerator:
    def __init__(self, mistral_api_key, groq_api_key):
        self.base_generator = BaseGenerator(mistral_api_key, groq_api_key)
    
    def generate_for_domain(self, domain, platform, user_preferences=None):
        """Generate content optimized for specific domain and platform"""
        # Add user preferences and domain-specific optimization
        result = self.base_generator.generate_content(domain, platform)
        
        if result.get('success'):
            # Apply platform-specific optimizations
            optimized_content = self._optimize_for_platform(result['content'], platform)
            result['content'] = optimized_content
        
        return result
    
    def _optimize_for_platform(self, content, platform):
        """Apply platform-specific optimizations"""
        if platform == 'instagram':
            # Add relevant hashtags
            if not '#' in content:
                content += '\n\n#socialmedia #ai #automation'
        elif platform == 'twitter':
            # Ensure content fits in tweet limit
            if len(content) > 250:
                content = content[:247] + '...'
        elif platform == 'linkedin':
            # Add professional tone
            if not content.startswith('🔹'):
                content = '🔹 ' + content
        
        return content
