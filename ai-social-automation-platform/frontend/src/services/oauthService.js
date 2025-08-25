import apiClient from './apiService';

class OAuthService {
  /**
   * Get OAuth authorization URL for a platform
   */
  async getAuthUrl(platform, options = {}) {
    try {
      const response = await apiClient.post('/oauth/auth-url', {
        platform,
        redirectUri: options.redirectUri,
        scopes: options.scopes || []
      });
      
      return response.data.authUrl;
    } catch (error) {
      console.error(`Failed to get OAuth URL for ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to get authorization URL');
    }
  }

  /**
   * Handle OAuth callback and exchange code for tokens
   */
  async handleCallback(platform, callbackData) {
    try {
      const response = await apiClient.post('/oauth/callback', {
        platform,
        code: callbackData.code,
        state: callbackData.state,
        redirectUri: callbackData.redirectUri
      });

      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error(`OAuth callback failed for ${platform}:`, error);
      return {
        success: false,
        error: error.response?.data?.message || 'OAuth callback failed'
      };
    }
  }

  /**
   * Get all connected platforms for the current user
   */
  async getConnectedPlatforms() {
    try {
      const response = await apiClient.get('/oauth/connected-platforms');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch connected platforms:', error);
      throw new Error(error.response?.data?.message || 'Failed to load connected platforms');
    }
  }

  /**
   * Get connection status for a specific platform
   */
  async getPlatformStatus(platform) {
    try {
      const response = await apiClient.get(`/oauth/platform/${platform}/status`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get ${platform} status:`, error);
      throw new Error(error.response?.data?.message || 'Failed to get platform status');
    }
  }

  /**
   * Disconnect a platform
   */
  async disconnect(platform) {
    try {
      const response = await apiClient.delete(`/oauth/platform/${platform}/disconnect`);
      return response.data;
    } catch (error) {
      console.error(`Failed to disconnect ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to disconnect platform');
    }
  }

  /**
   * Refresh access token for a platform
   */
  async refreshToken(platform) {
    try {
      const response = await apiClient.post(`/oauth/platform/${platform}/refresh-token`);
      return response.data;
    } catch (error) {
      console.error(`Failed to refresh token for ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to refresh access token');
    }
  }

  /**
   * Test platform connection
   */
  async testConnection(platform) {
    try {
      const response = await apiClient.post(`/oauth/platform/${platform}/test`);
      return {
        success: true,
        data: response.data
      };
    } catch (error) {
      console.error(`Connection test failed for ${platform}:`, error);
      return {
        success: false,
        error: error.response?.data?.message || 'Connection test failed'
      };
    }
  }

  /**
   * Get platform-specific configuration
   */
  async getPlatformConfig(platform) {
    try {
      const response = await apiClient.get(`/oauth/platform/${platform}/config`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get ${platform} config:`, error);
      throw new Error(error.response?.data?.message || 'Failed to get platform configuration');
    }
  }

  /**
   * Update platform settings
   */
  async updatePlatformSettings(platform, settings) {
    try {
      const response = await apiClient.put(`/oauth/platform/${platform}/settings`, settings);
      return response.data;
    } catch (error) {
      console.error(`Failed to update ${platform} settings:`, error);
      throw new Error(error.response?.data?.message || 'Failed to update platform settings');
    }
  }

  /**
   * Get user profile from connected platform
   */
  async getPlatformProfile(platform) {
    try {
      const response = await apiClient.get(`/oauth/platform/${platform}/profile`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get ${platform} profile:`, error);
      throw new Error(error.response?.data?.message || 'Failed to get platform profile');
    }
  }

  /**
   * Get platform permissions and scopes
   */
  async getPlatformPermissions(platform) {
    try {
      const response = await apiClient.get(`/oauth/platform/${platform}/permissions`);
      return response.data;
    } catch (error) {
      console.error(`Failed to get ${platform} permissions:`, error);
      throw new Error(error.response?.data?.message || 'Failed to get platform permissions');
    }
  }

  /**
   * Request additional permissions for a platform
   */
  async requestAdditionalPermissions(platform, scopes) {
    try {
      const response = await apiClient.post(`/oauth/platform/${platform}/request-permissions`, {
        scopes
      });
      
      return response.data.authUrl;
    } catch (error) {
      console.error(`Failed to request additional permissions for ${platform}:`, error);
      throw new Error(error.response?.data?.message || 'Failed to request additional permissions');
    }
  }
}

export const oauthService = new OAuthService();