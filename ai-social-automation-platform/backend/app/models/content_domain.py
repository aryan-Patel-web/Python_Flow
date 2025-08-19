# backend/app/models/content_domain.py
from datetime import datetime, timezone
from mongoengine import Document, StringField, BooleanField, DateTimeField, ReferenceField, DictField, ListField, IntField, FloatField
from .user import User

class ContentDomain(Document):
    """Model for content domains and their configurations"""
    
    user = ReferenceField(User, required=True)
    domain_type = StringField(required=True, choices=[
        'memes', 'tech_news', 'coding_tips', 'lifestyle', 'business',
        'fitness', 'travel', 'food', 'fashion', 'gaming', 'music',
        'education', 'motivation', 'quotes', 'news', 'sports'
    ])
    
    # Domain configuration
    is_active = BooleanField(default=True)
    priority = IntField(default=1, min_value=1, max_value=10)  # 1 = highest priority
    
    # Content generation settings
    generation_settings = DictField(default=lambda: {
        'tone': 'casual',  # casual, professional, funny, inspiring, informative
        'style': 'engaging',  # engaging, educational, promotional, storytelling
        'length': 'medium',  # short, medium, long
        'hashtags': True,
        'emojis': True,
        'call_to_action': True,
        'target_audience': 'general'
    })
    
    # Platform-specific optimizations
    platform_optimizations = DictField(default=lambda: {
        'instagram': {
            'hashtag_count': 25,
            'story_highlights': True,
            'reel_optimization': True,
            'carousel_posts': True
        },
        'facebook': {
            'link_previews': True,
            'video_optimization': True,
            'event_promotion': True
        },
        'youtube': {
            'seo_optimization': True,
            'thumbnail_generation': True,
            'chapter_markers': True
        },
        'twitter': {
            'thread_creation': True,
            'trending_hashtags': True,
            'character_optimization': True
        },
        'linkedin': {
            'professional_tone': True,
            'industry_keywords': True,
            'thought_leadership': True
        }
    })
    
    # Content scheduling
    posting_schedule = DictField(default=lambda: {
        'frequency': 2,  # posts per day
        'preferred_times': ['09:00', '15:00', '20:00'],
        'days_active': [1, 2, 3, 4, 5, 6, 7],  # Monday = 1
        'timezone': 'UTC',
        'auto_schedule': True
    })
    
    # Keywords and topics
    keywords = ListField(StringField(max_length=50), default=list)
    topics = ListField(StringField(max_length=100), default=list)
    excluded_keywords = ListField(StringField(max_length=50), default=list)
    
    # Performance tracking
    performance_metrics = DictField(default=lambda: {
        'total_posts': 0,
        'total_engagement': 0,
        'average_engagement': 0.0,
        'best_performing_content': [],
        'optimal_post_times': [],
        'engagement_rate': 0.0
    })
    
    # AI model preferences
    ai_preferences = DictField(default=lambda: {
        'primary_model': 'mistral',  # mistral, groq, openai
        'fallback_model': 'groq',
        'creativity_level': 0.7,  # 0.0 - 1.0
        'consistency_mode': False,
        'custom_prompts': {}
    })
    
    # Content filters and guidelines
    content_guidelines = DictField(default=lambda: {
        'avoid_controversial': True,
        'family_friendly': True,
        'brand_safe': True,
        'custom_filters': [],
        'approval_required': False
    })
    
    # Timestamps
    created_at = DateTimeField(default=datetime.now(timezone.utc))
    updated_at = DateTimeField(default=datetime.now(timezone.utc))
    last_generated_at = DateTimeField()
    
    meta = {
        'collection': 'content_domains',
        'indexes': [
            ('user', 'domain_type'),
            'user',
            'domain_type',
            'is_active',
            'priority',
            'created_at'
        ]
    }
    
    def __str__(self):
        return f"{self.user.username} - {self.domain_type.replace('_', ' ').title()}"
    
    def clean(self):
        """Validate and clean data before saving"""
        self.updated_at = datetime.now(timezone.utc)
        
        # Ensure keywords are lowercase and unique
        self.keywords = list(set([kw.lower().strip() for kw in self.keywords if kw.strip()]))
        self.excluded_keywords = list(set([kw.lower().strip() for kw in self.excluded_keywords if kw.strip()]))
        
        # Clean topics
        self.topics = list(set([topic.strip() for topic in self.topics if topic.strip()]))
    
    def get_content_specialist(self):
        """Get the appropriate content specialist for this domain"""
        from app.ai.domain_specialists import get_specialist
        return get_specialist(self.domain_type)
    
    def generate_content(self, platform='instagram', content_type='post'):
        """Generate content for this domain"""
        specialist = self.get_content_specialist()
        
        if not specialist:
            raise ValueError(f"No specialist available for domain: {self.domain_type}")
        
        # Update generation settings with platform optimizations
        settings = self.generation_settings.copy()
        if platform in self.platform_optimizations:
            settings.update(self.platform_optimizations[platform])
        
        content = specialist.generate_content(
            platform=platform,
            content_type=content_type,
            settings=settings,
            keywords=self.keywords,
            topics=self.topics,
            excluded_keywords=self.excluded_keywords
        )
        
        # Update last generated timestamp
        self.last_generated_at = datetime.now(timezone.utc)
        self.performance_metrics['total_posts'] += 1
        self.save()
        
        return content
    
    def update_performance_metrics(self, engagement_data):
        """Update performance metrics with new engagement data"""
        metrics = self.performance_metrics
        
        # Update totals
        metrics['total_engagement'] += engagement_data.get('total_engagement', 0)
        
        # Calculate new average
        if metrics['total_posts'] > 0:
            metrics['average_engagement'] = metrics['total_engagement'] / metrics['total_posts']
        
        # Update engagement rate
        if 'engagement_rate' in engagement_data:
            current_rate = metrics.get('engagement_rate', 0.0)
            new_rate = engagement_data['engagement_rate']
            metrics['engagement_rate'] = (current_rate + new_rate) / 2
        
        # Track best performing content
        if engagement_data.get('performance_score', 0) > 0.8:
            best_content = {
                'content_id': engagement_data.get('post_id'),
                'performance_score': engagement_data.get('performance_score'),
                'engagement': engagement_data.get('total_engagement'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            metrics['best_performing_content'].append(best_content)
            
            # Keep only top 10 best performing
            metrics['best_performing_content'] = sorted(
                metrics['best_performing_content'],
                key=lambda x: x['performance_score'],
                reverse=True
            )[:10]
        
        self.performance_metrics = metrics
        self.save()
    
    def get_optimal_posting_times(self):
        """Get optimal posting times based on performance data"""
        return self.performance_metrics.get('optimal_post_times', self.posting_schedule['preferred_times'])
    
    def should_generate_content(self):
        """Check if new content should be generated based on schedule"""
        if not self.is_active:
            return False
        
        # Check if enough time has passed since last generation
        if self.last_generated_at:
            time_diff = datetime.now(timezone.utc) - self.last_generated_at
            min_interval_hours = 24 / self.posting_schedule['frequency']
            
            if time_diff.total_seconds() < (min_interval_hours * 3600):
                return False
        
        return True
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            'id': str(self.id),
            'domain_type': self.domain_type,
            'is_active': self.is_active,
            'priority': self.priority,
            'generation_settings': self.generation_settings,
            'platform_optimizations': self.platform_optimizations,
            'posting_schedule': self.posting_schedule,
            'keywords': self.keywords,
            'topics': self.topics,
            'excluded_keywords': self.excluded_keywords,
            'performance_metrics': self.performance_metrics,
            'ai_preferences': self.ai_preferences,
            'content_guidelines': self.content_guidelines,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_generated_at': self.last_generated_at.isoformat() if self.last_generated_at else None
        }
    
    @classmethod
    def get_active_domains(cls, user, platform=None):
        """Get active domains for a user, optionally optimized for a specific platform"""
        domains = cls.objects(user=user, is_active=True).order_by('priority', '-created_at')
        
        if platform:
            # Filter domains that have optimizations for the specific platform
            filtered_domains = []
            for domain in domains:
                if platform in domain.platform_optimizations:
                    filtered_domains.append(domain)
            return filtered_domains
        
        return list(domains)
    
    @classmethod
    def get_domain_by_type(cls, user, domain_type):
        """Get a specific domain type for a user"""
        try:
            return cls.objects(user=user, domain_type=domain_type, is_active=True).first()
        except cls.DoesNotExist:
            return None