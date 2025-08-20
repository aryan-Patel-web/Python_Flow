// API Configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  TIMEOUT: parseInt(import.meta.env.VITE_API_TIMEOUT) || 10000,
  RETRY_ATTEMPTS: 3,
  RETRY_DELAY: 1000
}

// Authentication
export const AUTH_CONFIG = {
  TOKEN_KEY: 'auth_token',
  REFRESH_TOKEN_KEY: 'refresh_token',
  USER_KEY: 'user_data',
  TOKEN_EXPIRY_BUFFER: 5 * 60 * 1000, // 5 minutes
  SESSION_TIMEOUT: 24 * 60 * 60 * 1000 // 24 hours
}

// Social Media Platforms
export const PLATFORMS = {
  INSTAGRAM: {
    id: 'instagram',
    name: 'Instagram',
    color: '#E1306C',
    features: ['posts', 'stories', 'reels'],
    limits: { posts_per_day: 25, stories_per_day: 100 }
  },
  FACEBOOK: {
    id: 'facebook',
    name: 'Facebook',
    color: '#1877F2',
    features: ['posts', 'videos', 'events'],
    limits: { posts_per_day: 25, videos_per_day: 10 }
  },
  LINKEDIN: {
    id: 'linkedin',
    name: 'LinkedIn',
    color: '#0A66C2',
    features: ['posts', 'articles', 'company_updates'],
    limits: { posts_per_day: 5, articles_per_week: 3 }
  },
  YOUTUBE: {
    id: 'youtube',
    name: 'YouTube',
    color: '#FF0000',
    features: ['videos', 'shorts', 'community_posts'],
    limits: { videos_per_day: 6, shorts_per_day: 10 }
  },
  TWITTER: {
    id: 'twitter',
    name: 'Twitter',
    color: '#1DA1F2',
    features: ['tweets', 'threads', 'spaces'],
    limits: { tweets_per_day: 300, threads_per_day: 10 }
  },
  TIKTOK: {
    id: 'tiktok',
    name: 'TikTok',
    color: '#000000',
    features: ['videos', 'live'],
    limits: { videos_per_day: 10 }
  }
}

// Content Domains
export const CONTENT_DOMAINS = {
  MEMES: {
    id: 'memes',
    name: 'Memes & Humor',
    description: 'Funny memes, jokes, and humorous content',
    tags: ['funny', 'memes', 'humor', 'entertainment'],
    engagement_rate: 'high'
  },
  TECH: {
    id: 'tech',
    name: 'Technology',
    description: 'Latest tech news, tutorials, and insights',
    tags: ['technology', 'programming', 'ai', 'software'],
    engagement_rate: 'medium'
  },
  BUSINESS: {
    id: 'business',
    name: 'Business',
    description: 'Business tips, entrepreneurship, and success stories',
    tags: ['business', 'entrepreneur', 'success', 'tips'],
    engagement_rate: 'medium'
  },
  LIFESTYLE: {
    id: 'lifestyle',
    name: 'Lifestyle',
    description: 'Health, wellness, and lifestyle content',
    tags: ['lifestyle', 'health', 'wellness', 'motivation'],
    engagement_rate: 'high'
  },
  FINANCE: {
    id: 'finance',
    name: 'Finance',
    description: 'Financial advice, investing, and money management',
    tags: ['finance', 'investing', 'money', 'wealth'],
    engagement_rate: 'medium'
  },
  EDUCATION: {
    id: 'education',
    name: 'Education',
    description: 'Educational content, tutorials, and learning resources',
    tags: ['education', 'learning', 'tutorial', 'knowledge'],
    engagement_rate: 'medium'
  }
}

// Subscription Plans
export const SUBSCRIPTION_PLANS = {
  FREE: {
    id: 'free',
    name: 'Starter',
    price: { monthly: 0, yearly: 0 },
    features: {
      platforms: 2,
      posts_per_day: 3,
      ai_generations: 50,
      analytics: 'basic',
      support: 'email',
      scheduling: false,
      team_members: 1
    },
    popular: false
  },
  PRO: {
    id: 'pro',
    name: 'Professional',
    price: { monthly: 29, yearly: 290 },
    features: {
      platforms: 5,
      posts_per_day: 6,
      ai_generations: 200,
      analytics: 'advanced',
      support: 'priority',
      scheduling: true,
      team_members: 3
    },
    popular: true
  },
  ENTERPRISE: {
    id: 'enterprise',
    name: 'Enterprise',
    price: { monthly: 99, yearly: 990 },
    features: {
      platforms: 'unlimited',
      posts_per_day: 'unlimited',
      ai_generations: 'unlimited',
      analytics: 'premium',
      support: 'dedicated',
      scheduling: true,
      team_members: 'unlimited',
      white_label: true,
      api_access: true
    },
    popular: false
  }
}

// Content Types
export const CONTENT_TYPES = {
  TEXT: { id: 'text', name: 'Text Post', icon: 'FileText' },
  IMAGE: { id: 'image', name: 'Image Post', icon: 'Image' },
  VIDEO: { id: 'video', name: 'Video Post', icon: 'Video' },
  CAROUSEL: { id: 'carousel', name: 'Carousel Post', icon: 'MoreHorizontal' },
  STORY: { id: 'story', name: 'Story', icon: 'Smartphone' },
  REEL: { id: 'reel', name: 'Reel/Short', icon: 'Film' }
}

// Post Status
export const POST_STATUS = {
  DRAFT: { id: 'draft', name: 'Draft', color: 'gray' },
  SCHEDULED: { id: 'scheduled', name: 'Scheduled', color: 'yellow' },
  PUBLISHED: { id: 'published', name: 'Published', color: 'green' },
  FAILED: { id: 'failed', name: 'Failed', color: 'red' },
  ARCHIVED: { id: 'archived', name: 'Archived', color: 'gray' }
}

// Analytics Metrics
export const ANALYTICS_METRICS = {
  ENGAGEMENT: ['likes', 'comments', 'shares', 'saves'],
  REACH: ['views', 'impressions', 'reach'],
  GROWTH: ['followers', 'following', 'profile_visits'],
  PERFORMANCE: ['engagement_rate', 'reach_rate', 'click_through_rate']
}

// Time Ranges
export const TIME_RANGES = {
  '7d': { label: 'Last 7 days', days: 7 },
  '30d': { label: 'Last 30 days', days: 30 },
  '90d': { label: 'Last 90 days', days: 90 },
  '1y': { label: 'Last year', days: 365 }
}

// App Configuration
export const APP_CONFIG = {
  NAME: import.meta.env.VITE_APP_NAME || 'AI Social Media Automation',
  VERSION: import.meta.env.VITE_APP_VERSION || '1.0.0',
  ENVIRONMENT: import.meta.env.VITE_APP_ENV || 'development',
  DEBUG: import.meta.env.VITE_DEBUG_MODE === 'true',
  FEATURES: {
    ANALYTICS: import.meta.env.VITE_ENABLE_ANALYTICS !== 'false',
    BILLING: import.meta.env.VITE_ENABLE_BILLING !== 'false',
    NOTIFICATIONS: import.meta.env.VITE_ENABLE_NOTIFICATIONS !== 'false'
  }
}

// Error Messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'Resource not found.',
  VALIDATION_ERROR: 'Please check your input and try again.',
  RATE_LIMIT: 'Too many requests. Please wait and try again.',
  SESSION_EXPIRED: 'Your session has expired. Please login again.'
}

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Welcome back!',
  REGISTER: 'Account created successfully!',
  LOGOUT: 'Logged out successfully.',
  SAVE: 'Changes saved successfully.',
  DELETE: 'Deleted successfully.',
  UPLOAD: 'Upload completed successfully.',
  CONNECT: 'Platform connected successfully.',
  DISCONNECT: 'Platform disconnected.',
  POST_CREATED: 'Post created successfully.',
  POST_SCHEDULED: 'Post scheduled successfully.',
  POST_PUBLISHED: 'Post published successfully.'
}

// Validation Rules
export const VALIDATION = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PASSWORD: {
    MIN_LENGTH: 6,
    REQUIRE_UPPERCASE: false,
    REQUIRE_LOWERCASE: false,
    REQUIRE_NUMBER: false,
    REQUIRE_SPECIAL: false
  },
  USERNAME: {
    MIN_LENGTH: 3,
    MAX_LENGTH: 30,
    PATTERN: /^[a-zA-Z0-9_]+$/
  },
  POST_CONTENT: {
    MAX_LENGTH: {
      twitter: 280,
      instagram: 2200,
      facebook: 63206,
      linkedin: 3000,
      youtube: 5000
    }
  }
}

// File Upload
export const FILE_UPLOAD = {
  MAX_SIZE: 10 * 1024 * 1024, // 10MB
  ALLOWED_TYPES: {
    IMAGE: ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'],
    VIDEO: ['video/mp4', 'video/avi', 'video/mov', 'video/wmv'],
    DOCUMENT: ['application/pdf', 'text/plain', 'application/msword']
  }
}

export default {
  API_CONFIG,
  AUTH_CONFIG,
  PLATFORMS,
  CONTENT_DOMAINS,
  SUBSCRIPTION_PLANS,
  CONTENT_TYPES,
  POST_STATUS,
  ANALYTICS_METRICS,
  TIME_RANGES,
  APP_CONFIG,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  VALIDATION,
  FILE_UPLOAD
}