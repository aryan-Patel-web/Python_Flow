import React, { useState, useEffect } from 'react';
import { Globe, Smartphone, Info, AlertTriangle, Shield, CheckCircle, ExternalLink } from 'lucide-react';
import PlatformCard from './PlatformCard';
import oauthService from '../../services/oauthService';

const SecurePlatformConnection = () => {
  const [connecting, setConnecting] = useState(null);
  const [connected, setConnected] = useState({});
  const [loading, setLoading] = useState(true);

  // Load connected platforms from backend or session storage
  useEffect(() => {
    const loadConnectedPlatforms = async () => {
      try {
        // Try to load from backend first
        const response = await fetch('/api/platforms/connected', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setConnected(data.platforms || {});
        } else {
          // Fallback to session storage
          const sessionData = sessionStorage.getItem('connected_platforms');
          if (sessionData) {
            setConnected(JSON.parse(sessionData));
          }
        }
      } catch (error) {
        console.error('Failed to load connected platforms:', error);
        // Fallback to session storage
        const sessionData = sessionStorage.getItem('connected_platforms');
        if (sessionData) {
          setConnected(JSON.parse(sessionData));
        }
      } finally {
        setLoading(false);
      }
    };

    loadConnectedPlatforms();
  }, []);

  const platforms = [
    { 
      id: 'facebook', 
      name: 'Facebook', 
      icon: '📘', 
      color: 'from-blue-600 to-blue-500',
      description: 'Connect to post on Facebook pages and groups',
      scopes: ['pages_manage_posts', 'pages_read_engagement']
    },
    { 
      id: 'instagram', 
      name: 'Instagram', 
      icon: '📸', 
      color: 'from-pink-500 to-rose-500',
      description: 'Share photos and stories on Instagram',
      scopes: ['user_profile', 'user_media']
    },
    { 
      id: 'twitter', 
      name: 'Twitter/X', 
      icon: '🐦', 
      color: 'from-sky-500 to-sky-400',
      description: 'Post tweets and manage your Twitter presence',
      scopes: ['tweet.read', 'tweet.write', 'users.read']
    },
    { 
      id: 'linkedin', 
      name: 'LinkedIn', 
      icon: '💼', 
      color: 'from-blue-700 to-cyan-600',
      description: 'Share professional content on LinkedIn',
      scopes: ['w_member_social', 'r_liteprofile']
    },
    { 
      id: 'youtube', 
      name: 'YouTube', 
      icon: '📺', 
      color: 'from-red-600 to-rose-600',
      description: 'Upload and manage YouTube videos',
      scopes: ['youtube.upload', 'youtube.readonly']
    },
    { 
      id: 'tiktok', 
      name: 'TikTok', 
      icon: '🎵', 
      color: 'from-gray-900 to-gray-700',
      description: 'Create and share TikTok videos',
      scopes: ['video.upload', 'user.info.basic']
    }
  ];

  const handleConnect = async (platform) => {
    try {
      setConnecting(platform.id);
      await oauthService.connectPlatform(platform.id);
      // OAuth redirect happens inside connectPlatform
    } catch (error) {
      console.error('OAuth initiation failed:', error);
      setConnecting(null);
      alert(`Failed to start OAuth for ${platform.name}. Please check your configuration.`);
    }
  };

  const handleDisconnect = async (platform) => {
    if (!window.confirm(`Are you sure you want to disconnect ${platform.name}?`)) {
      return;
    }

    try {
      const response = await fetch(`/api/platforms/${platform.id}/disconnect`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });

      if (response.ok) {
        setConnected(prev => {
          const updated = { ...prev };
          delete updated[platform.id];
          sessionStorage.setItem('connected_platforms', JSON.stringify(updated));
          return updated;
        });
      } else {
        alert('Failed to disconnect platform');
      }
    } catch (error) {
      console.error('Disconnect failed:', error);
      alert('Failed to disconnect platform');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-3 text-gray-600">Loading platforms...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Security Notice */}
      <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">
        <div className="flex items-start space-x-3">
          <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900">100% Secure OAuth 2.0 Authentication</h3>
            <p className="text-sm text-blue-700 mt-1">
              We use official platform APIs with OAuth 2.0. Your passwords are never stored - only encrypted access tokens.
              You can revoke access anytime from your platform's security settings.
            </p>
          </div>
        </div>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {platforms.map((platform) => (
          <PlatformCard
            key={platform.id}
            platform={platform}
            isConnected={!!connected[platform.id]}
            onConnect={handleConnect}
            onDisconnect={handleDisconnect}
            disabled={connecting === platform.id}
            loading={connecting === platform.id}
          />
        ))}
      </div>

      {/* Configuration Help */}
      <div className="rounded-xl border border-yellow-200 bg-yellow-50 p-4">
        <div className="flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-yellow-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-yellow-900">Configuration Required</h3>
            <p className="text-sm text-yellow-800 mt-1">
              To connect platforms, you need to register OAuth apps with each platform and add the credentials 
              to your environment variables. Check the documentation for setup instructions.
            </p>
          </div>
        </div>
      </div>

      {/* Technical Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-center space-x-2 mb-3">
            <Globe className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-900">Callback URLs</span>
          </div>
          <div className="text-sm text-gray-700 space-y-1">
            <div className="font-mono text-xs bg-gray-100 p-2 rounded">
              {window.location.origin}/auth/callback/[platform]
            </div>
            <p className="text-xs text-gray-500">
              Use this pattern for your OAuth app redirect URIs
            </p>
          </div>
        </div>

        <div className="rounded-xl border border-gray-200 bg-white p-4">
          <div className="flex items-center space-x-2 mb-3">
            <Smartphone className="w-4 h-4 text-gray-600" />
            <span className="font-medium text-gray-900">Security Features</span>
          </div>
          <ul className="text-sm text-gray-700 space-y-1">
            <li className="flex items-center space-x-2">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span>PKCE for enhanced security</span>
            </li>
            <li className="flex items-center space-x-2">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span>State parameter CSRF protection</span>
            </li>
            <li className="flex items-center space-x-2">
              <CheckCircle className="w-3 h-3 text-green-500" />
              <span>Encrypted token storage</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Developer Resources */}
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <h3 className="font-medium text-gray-900 mb-3">Developer Resources</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          {[
            { name: 'Facebook', url: 'https://developers.facebook.com/' },
            { name: 'Instagram', url: 'https://developers.facebook.com/docs/instagram-basic-display-api' },
            { name: 'Twitter', url: 'https://developer.twitter.com/' },
            { name: 'LinkedIn', url: 'https://www.linkedin.com/developers/' },
            { name: 'YouTube', url: 'https://console.developers.google.com/' },
            { name: 'TikTok', url: 'https://developers.tiktok.com/' }
          ].map((resource) => (
            <a
              key={resource.name}
              href={resource.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-700 transition-colors"
            >
              <ExternalLink className="w-3 h-3" />
              <span>{resource.name} Docs</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SecurePlatformConnection;