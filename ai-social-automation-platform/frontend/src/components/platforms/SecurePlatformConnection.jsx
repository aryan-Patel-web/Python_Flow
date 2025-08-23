import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import oauthService from '../../services/oauthService';

const SecurePlatformConnection = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(null);

  // Secure platform configurations - NO passwords needed
  const platforms = [
    {
      id: 'facebook',
      name: 'Facebook',
      icon: '📘',
      description: 'Share posts, stories, and manage your Facebook pages',
      security: 'Highest Security',
      methods: ['OAuth 2.0 (Recommended)', 'App Password'],
      color: 'bg-blue-600 hover:bg-blue-700',
      borderColor: 'border-blue-200'
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: '📷',
      description: 'Post photos, stories, and reels to your Instagram account',
      security: 'Highest Security',
      methods: ['Instagram Basic Display API', 'Instagram Business API'],
      color: 'bg-pink-600 hover:bg-pink-700',
      borderColor: 'border-pink-200'
    },
    {
      id: 'twitter',
      name: 'Twitter/X',
      icon: '🐦',
      description: 'Tweet content and engage with your Twitter audience',
      security: 'Highest Security',
      methods: ['Twitter API v2 OAuth'],
      color: 'bg-gray-900 hover:bg-gray-800',
      borderColor: 'border-gray-200'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: '💼',
      description: 'Share professional content with your LinkedIn network',
      security: 'Highest Security',
      methods: ['LinkedIn OAuth 2.0'],
      color: 'bg-blue-700 hover:bg-blue-800',
      borderColor: 'border-blue-200'
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: '📺',
      description: 'Upload videos and manage your YouTube channel',
      security: 'Highest Security',
      methods: ['Google OAuth 2.0'],
      color: 'bg-red-600 hover:bg-red-700',
      borderColor: 'border-red-200'
    },
    {
      id: 'tiktok',
      name: 'TikTok',
      icon: '🎵',
      description: 'Post videos to your TikTok account',
      security: 'Highest Security',
      methods: ['TikTok for Business API'],
      color: 'bg-gray-800 hover:bg-gray-900',
      borderColor: 'border-gray-200'
    }
  ];

  useEffect(() => {
    loadConnectedPlatforms();
  }, []);

  const loadConnectedPlatforms = async () => {
    try {
      const connected = await oauthService.getConnectedPlatforms();
      setConnectedPlatforms(connected);
    } catch (error) {
      console.error('Failed to load connected platforms:', error);
      toast.error('Failed to load platform connections');
    } finally {
      setLoading(false);
    }
  };

  const handleSecureConnect = async (platform) => {
    try {
      setConnecting(platform.id);
      toast.loading(`Connecting to ${platform.name} securely...`, { id: 'secure-connect' });
      
      // Initiate secure OAuth flow - NO passwords involved
      await oauthService.connectPlatform(platform.id);
      
    } catch (error) {
      console.error('Secure connection failed:', error);
      toast.error(`Failed to connect to ${platform.name}: ${error.message}`, { id: 'secure-connect' });
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platform) => {
    if (!window.confirm(`Disconnect ${platform.name}? You can reconnect anytime.`)) {
      return;
    }

    try {
      const success = await oauthService.disconnectPlatform(platform.id);
      
      if (success) {
        setConnectedPlatforms(prev => prev.filter(p => p !== platform.id));
        toast.success(`Safely disconnected from ${platform.name}`);
      } else {
        toast.error(`Failed to disconnect from ${platform.name}`);
      }
    } catch (error) {
      console.error('Disconnect failed:', error);
      toast.error(`Failed to disconnect from ${platform.name}`);
    }
  };

  const isConnected = (platformId) => {
    return connectedPlatforms.includes(platformId);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Loading secure connections...</span>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Security Header */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg p-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <span className="text-green-500 text-2xl">🔒</span>
          </div>
          <div className="ml-4">
            <h2 className="text-lg font-semibold text-gray-900 mb-2">
              Secure Authentication
            </h2>
            <p className="text-gray-700 mb-3">
              We use OAuth 2.0 and official APIs to connect your accounts securely. 
              <strong> We never store your passwords.</strong>
            </p>
          </div>
        </div>
      </div>

      {/* Platform Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {platforms.map((platform) => (
          <div
            key={platform.id}
            className={`bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow border-2 ${platform.borderColor}`}
          >
            <div className="p-6">
              {/* Platform Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <span className="text-3xl mr-3">{platform.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {platform.security}
                    </span>
                  </div>
                </div>
                {isConnected(platform.id) && (
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                    ✓ Connected
                  </span>
                )}
              </div>

              {/* Security Methods */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Secure connection methods:</h4>
                <ul className="text-xs text-gray-600 space-y-1">
                  {platform.methods.map((method, index) => (
                    <li key={index} className="flex items-center">
                      <span className="text-green-500 mr-2">•</span>
                      {method}
                    </li>
                  ))}
                </ul>
              </div>

              {/* Connect Button */}
              <div className="space-y-2">
                {!isConnected(platform.id) ? (
                  <button
                    onClick={() => handleSecureConnect(platform)}
                    disabled={connecting === platform.id}
                    className={`w-full text-white py-3 px-4 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${platform.color}`}
                  >
                    {connecting === platform.id ? (
                      <span className="flex items-center justify-center">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Connecting Securely...
                      </span>
                    ) : (
                      '🔒 Connect Securely'
                    )}
                  </button>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-center justify-center py-3 px-4 bg-green-100 text-green-800 rounded-lg font-medium">
                      <span className="text-green-600 mr-2">✓</span>
                      Securely Connected
                    </div>
                    <button
                      onClick={() => handleDisconnect(platform)}
                      className="w-full border-2 border-gray-300 text-gray-700 py-2 px-4 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>
                )}
              </div>

              {/* Security Note */}
              {!isConnected(platform.id) && (
                <div className="mt-3 text-xs text-gray-500 text-center">
                  🛡️ No passwords required - uses official {platform.name} OAuth
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Security Information */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Why This is Secure</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl mb-2">🔐</div>
            <h4 className="font-medium text-gray-900 mb-1">OAuth 2.0</h4>
            <p className="text-sm text-gray-600">
              Industry-standard secure authentication. Your credentials never pass through our servers.
            </p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">✅</div>
            <h4 className="font-medium text-gray-900 mb-1">Official APIs</h4>
            <p className="text-sm text-gray-600">
              We only use official platform APIs, ensuring compliance and security best practices.
            </p>
          </div>
          <div className="text-center">
            <div className="text-2xl mb-2">🔑</div>
            <h4 className="font-medium text-gray-900 mb-1">Token-Based</h4>
            <p className="text-sm text-gray-600">
              Secure access tokens that can be revoked anytime from your platform's security settings.
            </p>
          </div>
        </div>
      </div>

      {/* Connected Platforms Summary */}
      {connectedPlatforms.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center">
            <span className="text-blue-500 text-2xl mr-3">🎉</span>
            <div>
              <h3 className="text-lg font-semibold text-blue-900">
                {connectedPlatforms.length} Platform{connectedPlatforms.length !== 1 ? 's' : ''} Securely Connected
              </h3>
              <p className="text-blue-700 mt-1">
                Great! You can now automate content posting to your connected platforms safely.
              </p>
              <button 
                onClick={() => window.location.href = '/domains'}
                className="mt-3 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200"
              >
                Next: Choose Content Domains →
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecurePlatformConnection;