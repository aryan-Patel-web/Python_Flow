import apiClient from './apiService';

class SchedulerService {
  /**
   * Get current scheduler settings
   */
  async getSettings() {
    try {
      const response = await apiClient.get('/scheduler/settings');
      return response.data;
    } catch (error) {
      console.error('Failed to get scheduler settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to get scheduler settings');
    }
  }

  /**
   * Update scheduler settings
   */
  async updateSettings(settings) {
    try {
      const response = await apiClient.put('/scheduler/settings', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to update scheduler settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to update scheduler settings');
    }
  }

  /**
   * Generate optimal posting times based on audience data
   */
  async generateOptimalTimes() {
    try {
      const response = await apiClient.post('/scheduler/generate-optimal-times');
      return response.data;
    } catch (error) {
      console.error('Failed to generate optimal times:', error);
      throw new Error(error.response?.data?.message || 'Failed to generate optimal posting times');
    }
  }

  /**
   * Get analytics for scheduler optimization
   */
  async getAnalytics() {
    try {
      const response = await apiClient.get('/scheduler/analytics');
      return response.data;
    } catch (error) {
      console.error('Failed to get scheduler analytics:', error);
      throw new Error(error.response?.data?.message || 'Failed to get scheduler analytics');
    }
  }

  /**
   * Get posting schedule preview
   */
  async getSchedulePreview(settings, days = 7) {
    try {
      const response = await apiClient.post('/scheduler/preview', {
        settings,
        days
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get schedule preview:', error);
      throw new Error(error.response?.data?.message || 'Failed to get schedule preview');
    }
  }

  /**
   * Get best performing times analysis
   */
  async getBestPerformingTimes(platform = null, timeframe = '30d') {
    try {
      const response = await apiClient.get('/scheduler/best-times', {
        params: { platform, timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get best performing times:', error);
      throw new Error(error.response?.data?.message || 'Failed to get best performing times');
    }
  }

  /**
   * Update platform-specific settings
   */
  async updatePlatformSettings(platform, settings) {
    try {
      const response = await apiClient.put(`/scheduler/platform/${platform}`, settings);
      return response.data;
    } catch (error) {
      console.error(`Failed to update ${platform} settings:`, error);
      throw new Error(error.response?.data?.message || 'Failed to update platform settings');
    }
  }

  /**
   * Get timezone recommendations based on audience
   */
  async getTimezoneRecommendations() {
    try {
      const response = await apiClient.get('/scheduler/timezone-recommendations');
      return response.data;
    } catch (error) {
      console.error('Failed to get timezone recommendations:', error);
      throw new Error(error.response?.data?.message || 'Failed to get timezone recommendations');
    }
  }

  /**
   * Validate scheduler configuration
   */
  async validateSettings(settings) {
    try {
      const response = await apiClient.post('/scheduler/validate', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to validate scheduler settings:', error);
      throw new Error(error.response?.data?.message || 'Failed to validate scheduler settings');
    }
  }

  /**
   * Get posting queue for next period
   */
  async getPostingQueue(days = 7) {
    try {
      const response = await apiClient.get('/scheduler/queue', {
        params: { days }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get posting queue:', error);
      throw new Error(error.response?.data?.message || 'Failed to get posting queue');
    }
  }

  /**
   * Pause scheduler for specific platform
   */
  async pausePlatform(platform) {
    try {
      const response = await apiClient.post(`/scheduler/platform/${platform}/pause`);
      return response.data;
    } catch (error) {
      console.error(`Failed to pause ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to pause platform');
    }
  }

  /**
   * Resume scheduler for specific platform
   */
  async resumePlatform(platform) {
    try {
      const response = await apiClient.post(`/scheduler/platform/${platform}/resume`);
      return response.data;
    } catch (error) {
      console.error(`Failed to resume ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to resume platform');
    }
  }

  /**
   * Get scheduler health status
   */
  async getHealthStatus() {
    try {
      const response = await apiClient.get('/scheduler/health');
      return response.data;
    } catch (error) {
      console.error('Failed to get scheduler health:', error);
      throw new Error(error.response?.data?.message || 'Failed to get scheduler health');
    }
  }

  /**
   * Test scheduler configuration
   */
  async testConfiguration(settings) {
    try {
      const response = await apiClient.post('/scheduler/test', settings);
      return response.data;
    } catch (error) {
      console.error('Failed to test scheduler configuration:', error);
      throw new Error(error.response?.data?.message || 'Failed to test scheduler configuration');
    }
  }

  /**
   * Get posting statistics
   */
  async getPostingStats(timeframe = '30d') {
    try {
      const response = await apiClient.get('/scheduler/stats', {
        params: { timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get posting stats:', error);
      throw new Error(error.response?.data?.message || 'Failed to get posting statistics');
    }
  }

  /**
   * Update content distribution settings
   */
  async updateContentDistribution(distribution) {
    try {
      const response = await apiClient.put('/scheduler/content-distribution', {
        distribution
      });
      return response.data;
    } catch (error) {
      console.error('Failed to update content distribution:', error);
      throw new Error(error.response?.data?.message || 'Failed to update content distribution');
    }
  }

  /**
   * Get audience activity patterns
   */
  async getAudienceActivity(platform, timeframe = '30d') {
    try {
      const response = await apiClient.get(`/scheduler/audience-activity`, {
        params: { platform, timeframe }
      });
      return response.data;
    } catch (error) {
      console.error('Failed to get audience activity:', error);
      throw new Error(error.response?.data?.message || 'Failed to get audience activity patterns');
    }
  }

  /**
   * Set posting blackout periods
   */
  async setBlackoutPeriods(periods) {
    try {
      const response = await apiClient.put('/scheduler/blackout-periods', {
        periods
      });
      return response.data;
    } catch (error) {
      console.error('Failed to set blackout periods:', error);
      throw new Error(error.response?.data?.message || 'Failed to set blackout periods');
    }
  }

  /**
   * Get posting velocity recommendations
   */
  async getVelocityRecommendations() {
    try {
      const response = await apiClient.get('/scheduler/velocity-recommendations');
      return response.data;
    } catch (error) {
      console.error('Failed to get velocity recommendations:', error);
      throw new Error(error.response?.data?.message || 'Failed to get velocity recommendations');
    }
  }
}

export const schedulerService = new SchedulerService();