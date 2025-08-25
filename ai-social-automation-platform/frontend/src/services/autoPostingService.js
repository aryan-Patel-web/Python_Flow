import apiClient from './apiService';

class AutoPostingService {
  /**
   * Get current automation status
   */
  async getStatus() {
    try {
      const response = await apiClient.get('/auto-posting/status');
      return response.data;
    } catch (error) {
      console.error('Failed to get automation status:', error);
      throw new Error(error.response?.data?.message || 'Failed to get automation status');
    }
  }

  /**
   * Start auto-posting automation
   */
  async startAutomation() {
    try {
      const response = await apiClient.post('/auto-posting/start');
      return response.data;
    } catch (error) {
      console.error('Failed to start automation:', error);
      throw new Error(error.response?.data?.message || 'Failed to start automation');
    }
  }

  /**
   * Pause auto-posting automation
   */
  async pauseAutomation() {
    try {
      const response = await apiClient.post('/auto-posting/pause');
      return response.data;
    } catch (error) {
      console.error('Failed to pause automation:', error);
      throw new Error(error.response?.data?.message || 'Failed to pause automation');
    }
  }

  /**
   * Stop auto-posting automation
   */
  async stopAutomation() {
    try {
      const response = await apiClient.post('/auto-posting/stop');
      return response.data;
    } catch (error) {
      console.error('Failed to stop automation:', error);
      throw new Error(error.response?.data?.message || 'Failed to stop automation');
    }
  }

  /**
   * Get automation statistics
   */
  async getStats(timeframe = '7d') {
    try {
      const response = await apiClient.get('/auto-posting/stats', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get automation stats:', error);
      throw new Error(error.response?.data?.message || 'Failed to get automation statistics');
    }
  }

  /**
   * Get recent auto-generated posts
   */
  async getRecentPosts(limit = 20) {
    try {
      const response = await apiClient.get('/auto-posting/recent-posts', {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get recent posts:', error);
      throw new Error(error.response?.data?.message || 'Failed to get recent posts');
    }
  }

  /**
   * Get scheduled posts queue
   */
  async getScheduledPosts() {
    try {
      const response = await apiClient.get('/auto-posting/scheduled');
      return response.data;
    } catch (error) {
      console.error('Failed to get scheduled posts:', error);
      throw new Error(error.response?.data?.message || 'Failed to get scheduled posts');
    }
  }

  /**
   * Update automation settings
   */
  async updateSettings(settings) {
    try {
      const response = await apiClient.put('/auto-posting/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update automation settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to update automation settings');
    }
  }

  /**
   * Get automation settings
   */
  async getSettings() {
    try {
      const response = await apiClient.get('/auto-posting/settings');
      return response.data;
    } catch (error) {
      console.error('Failed to get automation settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to get automation settings');
    }
  }

  /**
   * Force generate and post content immediately
   */
  async forcePost(platforms = [], domain = null) {
    try {
      const response = await apiClient.post('/auto-posting/force-post', {
        platforms,
        domain
      });
      return response.data;
    } catch (error) {
      console.error('Failed to force post:', error);
      throw new Error(error.response?.data?.message || 'Failed to force post');
    }
  }

  /**
   * Get automation logs
   */
  async getLogs(page = 1, limit = 50) {
    try {
      const response = await apiClient.get('/auto-posting/logs', {
        params: { page, limit }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get automation logs:', error);
      throw new Error(error.response?.data?.message || 'Failed to get automation logs');
    }
  }

  /**
   * Get next scheduled post time
   */
  async getNextPostTime() {
    try {
      const response = await apiClient.get('/auto-posting/next-post-time');
      return response.data;
    } catch (error) {
      console.error('Failed to get next post time:', error);
      throw new Error(error.response?.data?.message || 'Failed to get next post time');
    }
  }

  /**
   * Cancel a scheduled post
   */
  async cancelScheduledPost(postId) {
    try {
      const response = await apiClient.delete(`/auto-posting/scheduled/${postId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to cancel scheduled post:', error);
      throw new Error(error.response?.data?.message || 'Failed to cancel scheduled post');
    }
  }

  /**
   * Reschedule a post
   */
  async reschedulePost(postId, newTime) {
    try {
      const response = await apiClient.put(`/auto-posting/scheduled/${postId}/reschedule`, {
        scheduledFor: newTime
      });
      return response.data;
    } catch (error) {
      console.error('Failed to reschedule post:', error);
      throw new Error(error.response?.data?.message || 'Failed to reschedule post');
    }
  }

  /**
   * Get automation performance metrics
   */
  async getPerformanceMetrics(timeframe = '30d') {
    try {
      const response = await apiClient.get('/auto-posting/performance', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get performance metrics:', error);
      throw new Error(error.response?.data?.message || 'Failed to get performance metrics');
    }
  }

  /**
   * Test automation setup
   */
  async testAutomation() {
    try {
      const response = await apiClient.post('/auto-posting/test');
      return response.data;
    } catch (error) {
      console.error('Failed to test automation:', error);
      throw new Error(error.response?.data?.message || 'Failed to test automation');
    }
  }

  /**
   * Get automation health check
   */
  async getHealthCheck() {
    try {
      const response = await apiClient.get('/auto-posting/health');
      return response.data;
    } catch (error) {
      console.error('Failed to get automation health:', error);
      throw new Error(error.response?.data?.message || 'Failed to get automation health');
    }
  }

  /**
   * Update posting velocity settings
   */
  async updateVelocitySettings(settings) {
    try {
      const response = await apiClient.put('/auto-posting/velocity', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update velocity settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to update velocity settings');
    }
  }

  /**
   * Get posting velocity analytics
   */
  async getVelocityAnalytics() {
    try {
      const response = await apiClient.get('/auto-posting/velocity/analytics');
      return response.data;
    } catch (error) {
      console.error('Failed to get velocity analytics:', error);
      throw new Error(error.response?.data?.message || 'Failed to get velocity analytics');
    }
  }
}

export const autoPostingService = new AutoPostingService();