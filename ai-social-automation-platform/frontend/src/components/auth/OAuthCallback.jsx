import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../common/LoadingSpinner';
import { oauthService } from '../../services/oauthService';

const OAuthCallback = ({ platform }) => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('processing');
  const [message, setMessage] = useState('');

  const platformNames = {
    facebook: 'Facebook',
    instagram: 'Instagram', 
    twitter: 'Twitter/X',
    linkedin: 'LinkedIn',
    youtube: 'YouTube',
    tiktok: 'TikTok',
    pinterest: 'Pinterest'
  };

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        setStatus('processing');
        setMessage(`Connecting your ${platformNames[platform]} account...`);

        const code = searchParams.get('code');
        const state = searchParams.get('state');
        const error = searchParams.get('error');
        const errorDescription = searchParams.get('error_description');

        // Handle OAuth errors
        if (error) {
          console.error(`OAuth error for ${platform}:`, error, errorDescription);
          setStatus('error');
          setMessage(errorDescription || `Failed to connect ${platformNames[platform]} account`);
          toast.error(`OAuth Error: ${errorDescription || 'Connection failed'}`);
          
          setTimeout(() => {
            navigate('/platforms', { replace: true });
          }, 3000);
          return;
        }

        // Validate required parameters
        if (!code) {
          setStatus('error');
          setMessage('Authorization code not received');
          toast.error('OAuth authentication failed - no authorization code');
          
          setTimeout(() => {
            navigate('/platforms', { replace: true });
          }, 3000);
          return;
        }

        // Exchange code for access token and save platform connection
        const result = await oauthService.handleCallback(platform, {
          code,
          state,
          redirectUri: `${window.location.origin}/auth/callback/${platform}`
        });

        if (result.success) {
          setStatus('success');
          setMessage(`Successfully connected ${platformNames[platform]}! Auto-posting is now enabled.`);
          toast.success(`🎉 ${platformNames[platform]} connected successfully!`);
          
          // Redirect to platforms page after 2 seconds
          setTimeout(() => {
            navigate('/platforms', { 
              replace: true,
              state: { connectedPlatform: platform }
            });
          }, 2000);
        } else {
          throw new Error(result.error || 'Failed to connect platform');
        }

      } catch (error) {
        console.error(`OAuth callback error for ${platform}:`, error);
        setStatus('error');
        setMessage(error.message || `Failed to connect ${platformNames[platform]} account`);
        toast.error(`Connection failed: ${error.message}`);
        
        setTimeout(() => {
          navigate('/platforms', { replace: true });
        }, 3000);
      }
    };

    handleOAuthCallback();
  }, [platform, searchParams, navigate]);

  const getStatusIcon = () => {
    switch (status) {
      case 'processing':
        return <LoadingSpinner size="lg" color="blue" />;
      case 'success':
        return (
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
      default:
        return <LoadingSpinner size="lg" color="blue" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'success':
        return 'text-green-800';
      case 'error':
        return 'text-red-800';
      default:
        return 'text-blue-800';
    }
  };

  const getBackgroundColor = () => {
    switch (status) {
      case 'success':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
      <div className={`max-w-md w-full ${getBackgroundColor()} rounded-xl border-2 p-8 text-center`}>
        <div className="mb-6">
          {getStatusIcon()}
        </div>
        
        <div className="mb-4">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            {platformNames[platform]} OAuth
          </h1>
          <p className={`text-lg font-medium ${getStatusColor()}`}>
            {message}
          </p>
        </div>

        {status === 'processing' && (
          <div className="space-y-2 text-sm text-gray-600">
            <p>✓ Validating authorization code</p>
            <p>✓ Exchanging for access token</p>
            <p>✓ Setting up auto-posting permissions</p>
            <p>• Finalizing connection...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-2 text-sm text-green-700">
            <p>✅ Platform connected successfully</p>
            <p>✅ Auto-posting permissions granted</p>
            <p>✅ AI content generation enabled</p>
            <p className="font-medium">Redirecting to platforms...</p>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <div className="text-sm text-red-700">
              <p>❌ Connection failed</p>
              <p>Please try connecting again</p>
            </div>
            <button
              onClick={() => navigate('/platforms')}
              className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
            >
              Return to Platforms
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default OAuthCallback;