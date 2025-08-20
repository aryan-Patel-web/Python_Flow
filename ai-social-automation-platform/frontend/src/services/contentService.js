import apiService from './apiService'

// Content service for managing posts, content generation, and library
class ContentService {
  constructor() {
    this.baseURL = '/content'
  }

  // Content Library Management
  async getLibrary(params = {}) {
    try {
      const queryParams = new URLSearchParams({
        page: params.page || 1,
        limit: params.limit || 20,
        status: params.status || 'all',
        platform: params.platform || 'all',
        domain: params.domain || 'all',
        dateFrom: params.dateFrom || '',
        dateTo: params.dateTo || '',
        sortBy: params.sortBy || 'createdAt',
        sortOrder: params.sortOrder || 'desc',
        search: params.search || ''
      })

      return await apiService.content.getLibrary(queryParams)
    } catch (error) {
      console.error('Get library error:', error)
      throw error
    }
  }

  // Get single post
  async getPost(postId) {
    try {
      return await apiService.content.getPost(postId)
    } catch (error) {
      console.error('Get post error:', error)
      throw error
    }
  }

  // Create new post
  async createPost(postData) {
    try {
      const payload = {
        title: postData.title,
        content: postData.content,
        platform: postData.platform,
        domain: postData.domain,
        mediaUrls: postData.mediaUrls || [],
        scheduledAt: postData.scheduledAt,
        status: postData.status || 'draft',
        tags: postData.tags || [],
        metadata: postData.metadata || {}
      }

      return await apiService.content.createPost(payload)
    } catch (error) {
      console.error('Create post error:', error)
      throw error
    }
  }

  // Update existing post
  async updatePost(postId, updates) {
    try {
      return await apiService.content.updatePost(postId, updates)
    } catch (error) {
      console.error('Update post error:', error)
      throw error
    }
  }

  // Delete post
  async deletePost(postId) {
    try {
      return await apiService.content.deletePost(postId)
    } catch (error) {
      console.error('Delete post error:', error)
      throw error
    }
  }

  // Schedule post for publishing
  async schedulePost(postData) {
    try {
      const payload = {
        ...postData,
        status: 'scheduled'
      }

      return await apiService.content.schedulePost(payload)
    } catch (error) {
      console.error('Schedule post error:', error)
      throw error
    }
  }

  // AI Content Generation
  async generateContent(options = {}) {
    try {
      const payload = {
        domainId: options.domainId,
        platformId: options.platformId,
        prompt: options.prompt || '',
        contentType: options.contentType || 'post',
        tone: options.tone || 'professional',
        length: options.length || 'medium',
        includeHashtags: options.includeHashtags || true,
        includeEmojis: options.includeEmojis || true,
        targetAudience: options.targetAudience || 'general',
        keywords: options.keywords || []
      }

      return await apiService.content.generateContent(
        payload.domainId,
        payload.platformId,
        payload.prompt
      )
    } catch (error) {
      console.error('Generate content error:', error)
      throw error
    }
  }

  // Bulk actions on posts
  async bulkAction(action, postIds) {
    try {
      const validActions = ['publish', 'unpublish', 'delete', 'archive', 'schedule']
      
      if (!validActions.includes(action)) {
        throw new Error(`Invalid bulk action: ${action}`)
      }

      if (!Array.isArray(postIds) || postIds.length === 0) {
        throw new Error('Post IDs must be a non-empty array')
      }

      return await apiService.content.bulkAction(action, postIds)
    } catch (error) {
      console.error('Bulk action error:', error)
      throw error
    }
  }

  // Content Templates
  async getTemplates(category = 'all') {
    try {
      // Mock templates data - replace with actual API call
      const templates = [
        {
          id: 'motivational-quote',
          name: 'Motivational Quote',
          category: 'inspiration',
          description: 'Inspiring quotes with beautiful backgrounds',
          preview: '"Success is not final, failure is not fatal: it is the courage to continue that counts."',
          platforms: ['instagram', 'facebook', 'linkedin'],
          variables: ['quote', 'author', 'background']
        },
        {
          id: 'tech-tip',
          name: 'Tech Tip',
          category: 'technology',
          description: 'Quick technology tips and tricks',
          preview: '💡 Pro Tip: Use keyboard shortcuts to boost your productivity by 40%!',
          platforms: ['linkedin', 'twitter', 'facebook'],
          variables: ['tip', 'benefit', 'platform']
        },
        {
          id: 'meme-format',
          name: 'Meme Template',
          category: 'entertainment',
          description: 'Popular meme formats with customizable text',
          preview: 'When you finally fix that bug that took 5 hours... *celebration image*',
          platforms: ['instagram', 'twitter', 'facebook'],
          variables: ['topText', 'bottomText', 'memeType']
        }
      ]

      return {
        templates: category === 'all' 
          ? templates 
          : templates.filter(t => t.category === category)
      }
    } catch (error) {
      console.error('Get templates error:', error)
      throw error
    }
  }

  // Apply template to create content
  async applyTemplate(templateId, variables = {}) {
    try {
      // Mock template application - replace with actual API call
      const templates = await this.getTemplates()
      const template = templates.templates.find(t => t.id === templateId)
      
      if (!template) {
        throw new Error('Template not found')
      }

      // Generate content based on template and variables
      let content = template.preview
      
      Object.entries(variables).forEach(([key, value]) => {
        content = content.replace(`{${key}}`, value)
      })

      return {
        content,
        templateId,
        suggestedPlatforms: template.platforms
      }
    } catch (error) {
      console.error('Apply template error:', error)
      throw error
    }
  }

  // Content Optimization
  async optimizeForPlatform(content, platform) {
    try {
      const optimizationRules = {
        instagram: {
          maxLength: 2200,
          hashtagLimit: 30,
          includeEmojis: true,
          tone: 'casual'
        },
        facebook: {
          maxLength: 63206,
          hashtagLimit: 10,
          includeEmojis: false,
          tone: 'friendly'
        },
        twitter: {
          maxLength: 280,
          hashtagLimit: 3,
          includeEmojis: true,
          tone: 'concise'
        },
        linkedin: {
          maxLength: 3000,
          hashtagLimit: 5,
          includeEmojis: false,
          tone: 'professional'
        },
        youtube: {
          maxLength: 5000,
          hashtagLimit: 15,
          includeEmojis: false,
          tone: 'engaging'
        }
      }

      const rules = optimizationRules[platform] || optimizationRules.instagram
      let optimizedContent = content

      // Truncate if too long
      if (optimizedContent.length > rules.maxLength) {
        optimizedContent = optimizedContent.substring(0, rules.maxLength - 3) + '...'
      }

      // Add platform-specific formatting
      switch (platform) {
        case 'twitter':
          // Add thread indicators if content is long
          if (content.length > 280) {
            optimizedContent = content.substring(0, 250) + '... 🧵'
          }
          break
        case 'linkedin':
          // Add professional formatting
          if (!optimizedContent.includes('\n\n')) {
            optimizedContent = optimizedContent.replace(/\. /g, '.\n\n')
          }
          break
        case 'instagram':
          // Ensure hashtags are at the end
          const hashtagMatch = optimizedContent.match(/#\w+/g)
          if (hashtagMatch) {
            const contentWithoutHashtags = optimizedContent.replace(/#\w+/g, '').trim()
            const hashtags = hashtagMatch.slice(0, rules.hashtagLimit).join(' ')
            optimizedContent = `${contentWithoutHashtags}\n\n${hashtags}`
          }
          break
      }

      return {
        originalContent: content,
        optimizedContent,
        platform,
        rules,
        improvements: [
          'Optimized length for platform',
          'Adjusted tone and formatting',
          'Applied platform-specific best practices'
        ]
      }
    } catch (error) {
      console.error('Optimize content error:', error)
      throw error
    }
  }

  // Content Analytics
  async getContentAnalytics(postId) {
    try {
      // Mock analytics data - replace with actual API call
      return {
        postId,
        views: Math.floor(Math.random() * 10000),
        likes: Math.floor(Math.random() * 1000),
        comments: Math.floor(Math.random() * 100),
        shares: Math.floor(Math.random() * 50),
        clicks: Math.floor(Math.random() * 200),
        engagementRate: (Math.random() * 10).toFixed(2),
        reach: Math.floor(Math.random() * 5000),
        impressions: Math.floor(Math.random() * 8000),
        demographics: {
          ageGroups: {
            '18-24': 25,
            '25-34': 35,
            '35-44': 25,
            '45-54': 10,
            '55+': 5
          },
          genders: {
            male: 60,
            female: 38,
            other: 2
          },
          locations: [
            { country: 'United States', percentage: 45 },
            { country: 'India', percentage: 20 },
            { country: 'United Kingdom', percentage: 15 },
            { country: 'Canada', percentage: 10 },
            { country: 'Australia', percentage: 10 }
          ]
        }
      }
    } catch (error) {
      console.error('Get content analytics error:', error)
      throw error
    }
  }

  // Content Suggestions
  async getContentSuggestions(domainId, limit = 5) {
    try {
      // Mock suggestions - replace with actual API call
      const suggestions = [
        {
          id: 'suggestion-1',
          title: 'Top 5 Productivity Apps Every Professional Should Know',
          content: 'Boost your productivity with these game-changing apps that successful professionals swear by...',
          domain: domainId,
          estimatedEngagement: 8.5,
          bestPlatforms: ['linkedin', 'facebook'],
          contentType: 'list'
        },
        {
          id: 'suggestion-2',
          title: 'Monday Motivation: Turn Your Dreams Into Goals',
          content: 'Start your week strong! Here\'s how to transform wishful thinking into actionable plans...',
          domain: domainId,
          estimatedEngagement: 12.3,
          bestPlatforms: ['instagram', 'facebook'],
          contentType: 'motivational'
        },
        {
          id: 'suggestion-3',
          title: 'Behind the Scenes: How AI is Changing Content Creation',
          content: 'Take a peek behind the curtain of modern content creation and see how AI is revolutionizing...',
          domain: domainId,
          estimatedEngagement: 6.7,
          bestPlatforms: ['linkedin', 'twitter'],
          contentType: 'educational'
        }
      ]

      return {
        suggestions: suggestions.slice(0, limit),
        total: suggestions.length
      }
    } catch (error) {
      console.error('Get content suggestions error:', error)
      throw error
    }
  }

  // Trending Topics
  async getTrendingTopics(category = 'all') {
    try {
      // Mock trending topics - replace with actual API call
      const topics = [
        {
          topic: 'AI and Machine Learning',
          category: 'technology',
          trendScore: 95,
          mentions: 12500,
          growth: '+45%',
          keywords: ['artificial intelligence', 'machine learning', 'AI tools', 'automation']
        },
        {
          topic: 'Remote Work Productivity',
          category: 'business',
          trendScore: 88,
          mentions: 8900,
          growth: '+23%',
          keywords: ['remote work', 'productivity', 'work from home', 'digital nomad']
        },
        {
          topic: 'Sustainable Living',
          category: 'lifestyle',
          trendScore: 82,
          mentions: 7200,
          growth: '+18%',
          keywords: ['sustainability', 'eco-friendly', 'green living', 'climate change']
        },
        {
          topic: 'Mental Health Awareness',
          category: 'health',
          trendScore: 79,
          mentions: 6800,
          growth: '+31%',
          keywords: ['mental health', 'wellness', 'self-care', 'mindfulness']
        }
      ]

      return {
        topics: category === 'all' 
          ? topics 
          : topics.filter(t => t.category === category),
        lastUpdated: new Date().toISOString()
      }
    } catch (error) {
      console.error('Get trending topics error:', error)
      throw error
    }
  }

  // Content Performance Insights
  async getPerformanceInsights(dateRange = '30d') {
    try {
      // Mock insights - replace with actual API call
      return {
        totalPosts: 127,
        avgEngagementRate: 8.4,
        topPerformingDomain: 'memes',
        topPerformingPlatform: 'instagram',
        bestPostingTime: '18:00',
        bestPostingDay: 'Tuesday',
        contentTypePerformance: {
          'image': { posts: 45, avgEngagement: 9.2 },
          'video': { posts: 23, avgEngagement: 12.5 },
          'text': { posts: 59, avgEngagement: 6.8 }
        },
        platformPerformance: {
          'instagram': { posts: 42, avgEngagement: 11.2 },
          'facebook': { posts: 38, avgEngagement: 7.8 },
          'linkedin': { posts: 25, avgEngagement: 6.5 },
          'twitter': { posts: 22, avgEngagement: 4.9 }
        },
        recommendations: [
          'Post more video content for higher engagement',
          'Focus on Instagram and Facebook for best reach',
          'Tuesday evenings show highest engagement rates',
          'Meme content performs 40% better than average'
        ]
      }
    } catch (error) {
      console.error('Get performance insights error:', error)
      throw error
    }
  }

  // Utility methods
  validateContent(content, platform) {
    const errors = []
    
    if (!content || content.trim().length === 0) {
      errors.push('Content cannot be empty')
    }

    if (platform) {
      const limits = {
        twitter: 280,
        instagram: 2200,
        facebook: 63206,
        linkedin: 3000,
        youtube: 5000
      }

      const limit = limits[platform]
      if (limit && content.length > limit) {
        errors.push(`Content exceeds ${platform} character limit (${limit})`)
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  formatHashtags(hashtags) {
    if (!Array.isArray(hashtags)) return []
    
    return hashtags
      .map(tag => tag.replace(/[^a-zA-Z0-9]/g, ''))
      .filter(tag => tag.length > 0)
      .map(tag => `#${tag}`)
  }

  extractHashtags(content) {
    const hashtagRegex = /#[a-zA-Z0-9_]+/g
    return content.match(hashtagRegex) || []
  }

  removeHashtags(content) {
    return content.replace(/#[a-zA-Z0-9_]+/g, '').trim()
  }

  calculateReadingTime(content) {
    const wordsPerMinute = 200
    const words = content.split(/\s+/).length
    return Math.ceil(words / wordsPerMinute)
  }
}

// Create and export singleton instance
const contentService = new ContentService()

export default contentService

// Export specific methods for convenience
export const {
  getLibrary,
  getPost,
  createPost,
  updatePost,
  deletePost,
  schedulePost,
  generateContent,
  bulkAction,
  getTemplates,
  applyTemplate,
  optimizeForPlatform,
  getContentAnalytics,
  getContentSuggestions,
  getTrendingTopics,
  getPerformanceInsights,
  validateContent,
  formatHashtags,
  extractHashtags,
  removeHashtags,
  calculateReadingTime
} = contentService