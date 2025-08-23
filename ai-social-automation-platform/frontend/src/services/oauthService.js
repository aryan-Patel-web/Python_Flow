/**
 * Secure OAuth Service for VelocityPost.ai
 * Handles secure OAuth 2.0 authentication flows for social media platforms
 * No username/password storage - uses official platform APIs only
 */
class OAuthService {
  constructor() {
    this.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:5000';
    this.frontendURL = import.meta.env.VITE_FRONTEND_URL || window.location.origin;
  }

  /**
   * Initiate secure OAuth flow for a platform
   * @param {string} platform - Platform identifier (facebook, instagram, etc.)
   */
  async connectPlatform(platform) {
    const platformKey = platform.toLowerCase();
    
    try {
      // Validate platform
      if (!this._isValidPlatform(platformKey)) {
        throw new Error(`Unsupported platform: ${platform}`);
      }

      // Store platform info for callback
      sessionStorage.setItem('oauth_platform', platformKey);
      
      // Generate and store state for CSRF protection
      const state = this._generateSecureState();
      sessionStorage.setItem('oauth_state', state);

      // Generate PKCE parameters for enhanced security (especially Twitter)
      let codeChallenge, codeVerifier;
      if (this._requiresPKCE(platformKey)) {
        codeVerifier = this._generateCodeVerifier();
        sessionStorage.setItem('oauth_code_verifier', codeVerifier);
        codeChallenge = await this._generateCodeChallenge(codeVerifier);
      }

      // Build OAuth URL
      const oauthURL = this._buildOAuthURL(platformKey, state, codeChallenge);
      
      // Redirect to OAuth provider (secure authentication)
      window.location.href = oauthURL;
      
    } catch (error) {
      console.error('OAuth initiation failed:', error);
      this._cleanupSession();
      throw error;
    }
  }

  /**
   * Handle OAuth callback from platform
   * @param {string} platform - Platform identifier
   * @param {string} code - Authorization code
   * @param {string} state - State parameter for CSRF protection
   */
  async handleCallback(platform, code, state) {
    try {
      // Validate state parameter (prevents CSRF attacks)
      const expectedState = sessionStorage.getItem('oauth_state');
      if (expectedState && state && expectedState !== state) {
        throw new Error('Invalid state parameter - possible CSRF attack');
      }

      // Prepare callback payload
      const payload = {
        platform: platform.toLowerCase(),
        code,
        state
      };

      // Add PKCE code verifier for platforms that require it
      if (this._requiresPKCE(platform.toLowerCase())) {
        const codeVerifier = sessionStorage.getItem('oauth_code_verifier');
        if (!codeVerifier) {
          throw new Error('Missing PKCE code verifier');
        }
        payload.code_verifier = codeVerifier;
      }

      // Exchange code for tokens via backend (secure server-side exchange)
      const response = await fetch(`${this.baseURL}/api/auth/oauth/callback`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify(payload),
        credentials: 'include',
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP ${response.status}: OAuth callback failed`);
      }

      const result = await response.json();
      
      // Clean up session storage
      this._cleanupSession();
      
      return result;
      
    } catch (error) {
      console.error('OAuth callback failed:', error);
      this._cleanupSession();
      throw error;
    }
  }

  /**
   * Build secure OAuth authorization URL for a platform
   * @private
   */
  _buildOAuthURL(platform, state, codeChallenge) {
    const configs = {
      facebook: {
        url: 'https://www.facebook.com/v18.0/dialog/oauth',
        params: {
          client_id: import.meta.env.VITE_FACEBOOK_APP_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/facebook`,
          scope: 'pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish',
          response_type: 'code',
          state,
        }
      },
      instagram: {
        url: 'https://api.instagram.com/oauth/authorize',
        params: {
          client_id: import.meta.env.VITE_INSTAGRAM_CLIENT_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/instagram`,
          scope: 'user_profile,user_media',
          response_type: 'code',
          state,
        }
      },
      twitter: {
        url: 'https://twitter.com/i/oauth2/authorize',
        params: {
          response_type: 'code',
          client_id: import.meta.env.VITE_TWITTER_CLIENT_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/twitter`,
          scope: 'tweet.read tweet.write users.read offline.access',
          state,
          code_challenge: codeChallenge,
          code_challenge_method: 'S256',
        }
      },
      linkedin: {
        url: 'https://www.linkedin.com/oauth/v2/authorization',
        params: {
          response_type: 'code',
          client_id: import.meta.env.VITE_LINKEDIN_CLIENT_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/linkedin`,
          scope: 'w_member_social r_liteprofile r_emailaddress',
          state,
        }
      },
      youtube: {
        url: 'https://accounts.google.com/o/oauth2/v2/auth',
        params: {
          client_id: import.meta.env.VITE_GOOGLE_CLIENT_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/youtube`,
          scope: 'https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly',
          response_type: 'code',
          access_type: 'offline',
          include_granted_scopes: 'true',
          state,
        }
      },
      tiktok: {
        url: 'https://www.tiktok.com/auth/authorize/',
        params: {
          client_key: import.meta.env.VITE_TIKTOK_CLIENT_KEY,
          response_type: 'code',
          scope: 'user.info.basic,video.upload',
          redirect_uri: `${this.frontendURL}/auth/callback/tiktok`,
          state,
        }
      },
      pinterest: {
        url: 'https://www.pinterest.com/oauth/',
        params: {
          response_type: 'code',
          client_id: import.meta.env.VITE_PINTEREST_CLIENT_ID,
          redirect_uri: `${this.frontendURL}/auth/callback/pinterest`,
          scope: 'read_public,write_public',
          state,
        }
      }
    };

    const config = configs[platform];
    if (!config) {
      throw new Error(`OAuth configuration not found for platform: ${platform}`);
    }

    // Validate required environment variables
    const requiredParam = this._getRequiredClientParam(platform);
    if (!config.params[requiredParam]) {
      throw new Error(`Missing environment variable for ${platform}. Please check your .env.local file.`);
    }

    // Build URL with parameters
    const url = new URL(config.url);
    Object.entries(config.params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, value);
      }
    });

    return url.toString();
  }

  /**
   * Generate cryptographically secure state parameter
   * @private
   */
  _generateSecureState() {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Generate PKCE code verifier
   * @private
   */
  _generateCodeVerifier() {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return this._base64URLEncode(array);
  }

  /**
   * Generate PKCE code challenge from verifier
   * @private
   */
  async _generateCodeChallenge(verifier) {
    const data = new TextEncoder().encode(verifier);
    const digest = await window.crypto.subtle.digest('SHA-256', data);
    return this._base64URLEncode(new Uint8Array(digest));
  }

  /**
   * Base64 URL encode
   * @private
   */
  _base64URLEncode(bytes) {
    let str = '';
    bytes.forEach(byte => str += String.fromCharCode(byte));
    return btoa(str)
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=+$/, '');
  }

  /**
   * Check if platform requires PKCE
   * @private
   */
  _requiresPKCE(platform) {
    return ['twitter'].includes(platform.toLowerCase());
  }

  /**
   * Validate platform support
   * @private
   */
  _isValidPlatform(platform) {
    const supportedPlatforms = ['facebook', 'instagram', 'twitter', 'linkedin', 'youtube', 'tiktok', 'pinterest'];
    return supportedPlatforms.includes(platform.toLowerCase());
  }

  /**
   * Get the required client parameter name for environment validation
   * @private
   */
  _getRequiredClientParam(platform) {
    const paramMap = {
      facebook: 'client_id',
      instagram: 'client_id',
      twitter: 'client_id',
      linkedin: 'client_id',
      youtube: 'client_id',
      tiktok: 'client_key',
      pinterest: 'client_id'
    };
    return paramMap[platform] || 'client_id';
  }

  /**
   * Clean up OAuth session data
   * @private
   */
  _cleanupSession() {
    sessionStorage.removeItem('oauth_platform');
    sessionStorage.removeItem('oauth_state');
    sessionStorage.removeItem('oauth_code_verifier');
  }

  /**
   * Get environment variable status for debugging
   */
  getEnvironmentStatus() {
    const envVars = {
      VITE_FACEBOOK_APP_ID: !!import.meta.env.VITE_FACEBOOK_APP_ID,
      VITE_INSTAGRAM_CLIENT_ID: !!import.meta.env.VITE_INSTAGRAM_CLIENT_ID,
      VITE_TWITTER_CLIENT_ID: !!import.meta.env.VITE_TWITTER_CLIENT_ID,
      VITE_LINKEDIN_CLIENT_ID: !!import.meta.env.VITE_LINKEDIN_CLIENT_ID,
      VITE_GOOGLE_CLIENT_ID: !!import.meta.env.VITE_GOOGLE_CLIENT_ID,
      VITE_TIKTOK_CLIENT_KEY: !!import.meta.env.VITE_TIKTOK_CLIENT_KEY,
      VITE_PINTEREST_CLIENT_ID: !!import.meta.env.VITE_PINTEREST_CLIENT_ID,
    };

    return envVars;
  }

  /**
   * Get connected platforms for user
   */
  async getConnectedPlatforms() {
    try {
      const response = await fetch(`${this.baseURL}/api/platforms/connected`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
      });

      if (response.ok) {
        return await response.json();
      }
      return [];
    } catch (error) {
      console.error('Failed to fetch connected platforms:', error);
      return [];
    }
  }

  /**
   * Disconnect a platform
   */
  async disconnectPlatform(platform) {
    try {
      const response = await fetch(`${this.baseURL}/api/platforms/disconnect`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token') || ''}`,
        },
        body: JSON.stringify({ platform }),
      });

      return response.ok;
    } catch (error) {
      console.error('Failed to disconnect platform:', error);
      return false;
    }
  }
}

// Export singleton instance
export default new OAuthService();