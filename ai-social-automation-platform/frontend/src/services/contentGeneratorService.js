import apiClient from './apiService';

class ContentGeneratorService {
  /**
   * Generate AI content based on domain and settings
   */
  async generateContent(request) {
    try {
      const response = await apiClient.post('/content/generate', request);
      return response.data;
    } catch (error) {
      console.error('Content generation failed:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate content');
    }
  }

  /**
   * Get recent generated content
   */
  async getRecentContent(limit = 20, page = 1) {
    try {
      const response = await apiClient.get('/content/recent', {
        params: { limit, page }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get recent content:', error);
      throw new Error(error.response?.data?.message || 'Failed to get recent content');
    }
  }

  /**
   * Update/edit existing content
   */
  async updateContent(content) {
    try {
      const response = await apiClient.put(`/content/${content.id}`, {
        text: content.text,
        platforms: content.platforms,
        tags: content.tags
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update content:', error);
      throw new Error(error.response?.data?.message || 'Failed to update content');
    }
  }

  /**
   * Delete content
   */
  async deleteContent(contentId) {
    try {
      const response = await apiClient.delete(`/content/${contentId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to delete content:', error);
      throw new Error(error.response?.data?.message || 'Failed to delete content');
    }
  }

  /**
   * Schedule content for posting
   */
  async schedulePost(content, scheduledTime = null) {
    try {
      const response = await apiClient.post('/content/schedule', {
        contentId: content.id,
        platforms: content.platforms,
        scheduledFor: scheduledTime || 'optimal'
      });
      return response.data;
    } catch (error) {
      console.error('Failed to schedule post:', error);
      throw new Error(error.response?.data?.message || 'Failed to schedule post');
    }
  }

  /**
   * Post content immediately
   */
  async postNow(content) {
    try {
      const response = await apiClient.post('/content/post-now', {
        contentId: content.id,
        platforms: content.platforms
      });
      return response.data;
    } catch (error) {
      console.error('Failed to post content now:', error);
      throw new Error(error.response?.data?.message || 'Failed to post content immediately');
    }
  }

  /**
   * Generate content for specific prompt
   */
  async generateFromPrompt(prompt, platforms, settings = {}) {
    try {
      const response = await apiClient.post('/content/generate-prompt', {
        prompt,
        platforms,
        settings
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate from prompt:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate content from prompt');
    }
  }

  /**
   * Get content templates by domain
   */
  async getTemplates(domain) {
    try {
      const response = await apiClient.get('/content/templates', {
        params: { domain }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get templates:', error);
      throw new Error(error.response?.data?.message || 'Failed to get content templates');
    }
  }

  /**
   * Create custom template
   */
  async createTemplate(template) {
    try {
      const response = await apiClient.post('/content/templates', template);
      return response.data;
    } catch (error) {
      console.error('Failed to create template:', error);
      throw new Error(error.response?.data?.message || 'Failed to create template');
    }
  }

  /**
   * Get content performance prediction
   */
  async getPerformancePrediction(content, platforms) {
    try {
      const response = await apiClient.post('/content/predict-performance', {
        content,
        platforms
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get performance prediction:', error);
      throw new Error(error.response?.data?.message || 'Failed to predict content performance');
    }
  }

  /**
   * Generate hashtags for content
   */
  async generateHashtags(content, platform, count = 10) {
    try {
      const response = await apiClient.post('/content/generate-hashtags', {
        content,
        platform,
        count
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate hashtags:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate hashtags');
    }
  }

  /**
   * Generate image for content
   */
  async generateImage(content, style = 'auto') {
    try {
      const response = await apiClient.post('/content/generate-image', {
        content,
        style
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate image:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate image');
    }
  }

  /**
   * Optimize content for specific platform
   */
  async optimizeForPlatform(content, platform) {
    try {
      const response = await apiClient.post('/content/optimize', {
        content,
        platform
      });
      return response.data;
    } catch (error) {
      console.error('Failed to optimize content:', error);
      throw new Error(error.response?.data?.message || 'Failed to optimize content for platform');
    }
  }

  /**
   * Get trending topics for domain
   */
  async getTrendingTopics(domain, platform = null) {
    try {
      const response = await apiClient.get('/content/trending', {
        params: { domain, platform }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get trending topics:', error);
      throw new Error(error.response?.data?.message || 'Failed to get trending topics');
    }
  }

  /**
   * Generate content variations
   */
  async generateVariations(contentId, count = 3) {
    try {
      const response = await apiClient.post(`/content/${contentId}/variations`, {
        count
      });
      return response.data;
    } catch (error) {
      console.error('Failed to generate variations:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate content variations');
    }
  }

  /**
   * Get content analytics
   */
  async getContentAnalytics(contentId) {
    try {
      const response = await apiClient.get(`/content/${contentId}/analytics`);
      return response.data;
    } catch (error) {
      console.error('Failed to get content analytics:', error);
      throw new Error(error.response?.data?.message || 'Failed to get content analytics');
    }
  }

  /**
   * Save content as draft
   */
  async saveDraft(content) {
    try {
      const response = await apiClient.post('/content/drafts', content);
      return response.data;
    } catch (error) {
      console.error('Failed to save draft:', error);
      throw new Error(error.response?.data?.message || 'Failed to save draft');
    }
  }

  /**
   * Get saved drafts
   */
  async getDrafts() {
    try {
      const response = await apiClient.get('/content/drafts');
      return response.data;
    } catch (error) {
      console.error('Failed to get drafts:', error);
      throw new Error(error.response?.data?.message || 'Failed to get drafts');
    }
  }

  /**
   * Bulk generate content
   */
  async bulkGenerate(requests) {
    try {
      const response = await apiClient.post('/content/bulk-generate', {
        requests
      });
      return response.data;
    } catch (error) {
      console.error('Failed to bulk generate:', error);
      throw new Error(error.response?.data?.message || 'Failed to bulk generate content');
    }
  }

  /**
   * Get AI model settings
   */
  async getAISettings() {
    try {
      const response = await apiClient.get('/content/ai-settings');
      return response.data;
    } catch (error) {
      console.error('Failed to get AI settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to get AI settings');
    }
  }

  /**
   * Update AI model settings
   */
  async updateAISettings(settings) {
    try {
      const response = await apiClient.put('/content/ai-settings', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update AI settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to update AI settings');
    }
  }

  /**
   * Get content generation history
   */
  async getGenerationHistory(filters = {}) {
    try {
      const response = await apiClient.get('/content/history', {
        params: filters
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get generation history:', error);
      throw new Error(error.response?.data?.message || 'Failed to get generation history');
    }
  }

  /**
   * Rate content quality
   */
  async rateContent(contentId, rating, feedback = '') {
    try {
      const response = await apiClient.post(`/content/${contentId}/rate`, {
        rating,
        feedback
      });
      return response.data;
    } catch (error) {
      console.error('Failed to rate content:', error);
      throw new Error(error.response?.data?.message || 'Failed to rate content');
    }
  }

  /**
   * Get content suggestions based on performance
   */
  async getContentSuggestions(domain, platform) {
    try {
      const response = await apiClient.get('/content/suggestions', {
        params: { domain, platform }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get content suggestions:', error);
      throw new Error(error.response?.data?.message || 'Failed to get content suggestions');
    }
  }
}

export const contentGeneratorService = new ContentGeneratorService();