import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  Shield, Check, ExternalLink, Zap, Bot, AlertCircle,
  Facebook, Twitter, Linkedin, Youtube, Instagram
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { oauthService } from '../../services/oauthService';

const Platforms = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState({});
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(null);
  const location = useLocation();

  const platforms = [
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'bg-blue-600',
      description: 'Pages, Groups, and Personal Posts',
      features: ['Auto-post to pages', 'Audience targeting', 'Story posting'],
      permissions: ['manage_pages', 'publish_pages', 'pages_show_list']
    },
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: 'bg-gradient-to-r from-purple-500 to-pink-500',
      description: 'Business and Creator Accounts',
      features: ['Photo & video posts', 'Stories', 'Reels automation'],
      permissions: ['instagram_basic', 'instagram_content_publish']
    },
    {
      id: 'twitter',
      name: 'Twitter/X',
      icon: Twitter,
      color: 'bg-black',
      description: 'Tweet Automation & Engagement',
      features: ['Tweet scheduling', 'Thread creation', 'Auto-replies'],
      permissions: ['tweet.write', 'tweet.read', 'users.read']
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      color: 'bg-blue-700',
      description: 'Professional Network Posts',
      features: ['Personal posts', 'Company pages', 'Article publishing'],
      permissions: ['w_member_social', 'r_liteprofile', 'r_emailaddress']
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      color: 'bg-red-600',
      description: 'Video Upload & Management',
      features: ['Video uploads', 'Playlist management', 'Community posts'],
      permissions: ['youtube.upload', 'youtube.readonly']
    }
  ];

  useEffect(() => {
    fetchConnectedPlatforms();
    
    // Check if we just connected a platform
    const connectedPlatform = location.state?.connectedPlatform;
    if (connectedPlatform) {
      toast.success(`${platforms.find(p => p.id === connectedPlatform)?.name} connected successfully!`);
    }
  }, [location.state]);

  const fetchConnectedPlatforms = async () => {
    try {
      const connected = await oauthService.getConnectedPlatforms();
      setConnectedPlatforms(connected);
    } catch (error) {
      console.error('Failed to fetch connected platforms:', error);
      toast.error('Failed to load platform connections');
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (platformId) => {
    try {
      setConnecting(platformId);
      
      // Get OAuth authorization URL
      const authUrl = await oauthService.getAuthUrl(platformId, {
        redirectUri: `${window.location.origin}/auth/callback/${platformId}`,
        scopes: platforms.find(p => p.id === platformId)?.permissions || []
      });

      // Redirect to OAuth provider
      window.location.href = authUrl;
      
    } catch (error) {
      console.error(`Failed to initiate OAuth for ${platformId}:`, error);
      toast.error(`Failed to connect ${platforms.find(p => p.id === platformId)?.name}`);
      setConnecting(null);
    }
  };

  const handleDisconnect = async (platformId) => {
    if (!window.confirm(`Disconnect ${platforms.find(p => p.id === platformId)?.name}? This will stop all auto-posting.`)) {
      return;
    }

    try {
      await oauthService.disconnect(platformId);
      setConnectedPlatforms(prev => ({
        ...prev,
        [platformId]: null
      }));
      toast.success('Platform disconnected successfully');
    } catch (error) {
      console.error(`Failed to disconnect ${platformId}:`, error);
      toast.error('Failed to disconnect platform');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Loading platform connections..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <Shield className="w-8 h-8" />
          <div>
            <h1 className="text-2xl font-bold">Secure Platform Connections</h1>
            <p className="text-blue-100">OAuth 2.0 authenticated auto-posting</p>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Shield className="w-5 h-5" />
              <span className="font-medium">Bank-Level Security</span>
            </div>
            <p className="text-sm text-blue-100 mt-1">OAuth 2.0 authentication</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Bot className="w-5 h-5" />
              <span className="font-medium">AI-Powered Posting</span>
            </div>
            <p className="text-sm text-blue-100 mt-1">Intelligent content automation</p>
          </div>
          <div className="bg-white/10 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <Zap className="w-5 h-5" />
              <span className="font-medium">Real-Time Analytics</span>
            </div>
            <p className="text-sm text-blue-100 mt-1">Performance tracking</p>
          </div>
        </div>
      </div>

      {/* Security Notice */}
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <AlertCircle className="w-5 h-5 text-green-600 mt-0.5" />
          <div className="text-sm text-green-800">
            <p className="font-medium">🔒 Your credentials are secure</p>
            <p>We use OAuth 2.0 - the same security standard used by banks. We never see or store your passwords.</p>
          </div>
        </div>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {platforms.map((platform) => {
          const isConnected = connectedPlatforms[platform.id];
          const isConnecting = connecting === platform.id;
          const IconComponent = platform.icon;

          return (
            <div key={platform.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-4">
                  <div className={`w-12 h-12 ${platform.color} rounded-lg flex items-center justify-center`}>
                    <IconComponent className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                    <p className="text-sm text-gray-600">{platform.description}</p>
                  </div>
                </div>
                
                {isConnected ? (
                  <div className="flex items-center space-x-2 text-green-600">
                    <Check className="w-5 h-5" />
                    <span className="text-sm font-medium">Connected</span>
                  </div>
                ) : (
                  <div className="text-gray-400">
                    <span className="text-sm">Not connected</span>
                  </div>
                )}
              </div>

              {/* Features */}
              <div className="mb-4">
                <h4 className="text-sm font-medium text-gray-700 mb-2">Features:</h4>
                <ul className="space-y-1">
                  {platform.features.map((feature, index) => (
                    <li key={index} className="flex items-center space-x-2 text-sm text-gray-600">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Connection Status */}
              {isConnected ? (
                <div className="space-y-3">
                  <div className="bg-green-50 border border-green-200 rounded-lg p-3">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-green-800">
                          Connected as: {isConnected.username || isConnected.name}
                        </p>
                        <p className="text-xs text-green-600">
                          Auto-posting enabled • {isConnected.postsCount || 0} posts created
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-green-600">Connected</p>
                        <p className="text-xs text-gray-500">
                          {new Date(isConnected.connectedAt).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <Link
                      to="/auto-posting"
                      className="flex-1 bg-blue-600 hover:bg-blue-700 text-white text-center py-2 px-4 rounded-lg font-medium transition-colors"
                    >
                      Manage Auto-Posting
                    </Link>
                    <button
                      onClick={() => handleDisconnect(platform.id)}
                      className="px-4 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                    >
                      Disconnect
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={() => handleConnect(platform.id)}
                  disabled={isConnecting}
                  className={`w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-lg font-medium transition-colors ${
                    isConnecting 
                      ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                      : 'bg-gray-900 hover:bg-gray-800 text-white'
                  }`}
                >
                  {isConnecting ? (
                    <>
                      <LoadingSpinner size="sm" color="gray" />
                      <span>Connecting...</span>
                    </>
                  ) : (
                    <>
                      <Shield className="w-4 h-4" />
                      <span>Connect Securely</span>
                      <ExternalLink className="w-4 h-4" />
                    </>
                  )}
                </button>
              )}

              {/* Permissions */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <h4 className="text-xs font-medium text-gray-500 mb-2">Permissions Required:</h4>
                <div className="flex flex-wrap gap-1">
                  {platform.permissions.map((permission, index) => (
                    <span
                      key={index}
                      className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded"
                    >
                      {permission}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Next Steps */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">🚀 Next Steps</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Link
            to="/domains"
            className="bg-white p-4 rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">1</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Select Domains</h4>
                <p className="text-sm text-gray-600">Choose content categories</p>
              </div>
            </div>
          </Link>
          
          <Link
            to="/content-generator"
            className="bg-white p-4 rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">2</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Generate Content</h4>
                <p className="text-sm text-gray-600">AI creates posts</p>
              </div>
            </div>
          </Link>
          
          <Link
            to="/auto-posting"
            className="bg-white p-4 rounded-lg border border-blue-200 hover:border-blue-300 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">3</span>
              </div>
              <div>
                <h4 className="font-medium text-gray-900">Start Auto-Posting</h4>
                <p className="text-sm text-gray-600">Activate automation</p>
              </div>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Platforms;