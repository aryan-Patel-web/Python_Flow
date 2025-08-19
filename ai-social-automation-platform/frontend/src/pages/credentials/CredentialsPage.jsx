import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import { credentialsService } from '../../services/credentialsService';
import PlatformSetup from '../../components/credentials/PlatformSetup';
import PlatformCard from '../../components/credentials/PlatformCard';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const CredentialsPage = () => {
  const [platforms, setPlatforms] = useState({});
  const [loading, setLoading] = useState(true);
  const [showSetup, setShowSetup] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);

  const supportedPlatforms = [
    { id: 'instagram', name: 'Instagram', description: 'Post images, reels, and stories', icon: '📸', color: 'bg-pink-500' },
    { id: 'facebook', name: 'Facebook', description: 'Share posts, images, and videos', icon: '📘', color: 'bg-blue-600' },
    { id: 'youtube', name: 'YouTube', description: 'Upload videos and shorts', icon: '📺', color: 'bg-red-500' },
    { id: 'twitter', name: 'Twitter/X', description: 'Post tweets and threads', icon: '🐦', color: 'bg-sky-500' },
    { id: 'linkedin', name: 'LinkedIn', description: 'Professional posts and articles', icon: '💼', color: 'bg-blue-700' }
  ];

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      const response = await credentialsService.getAllCredentials();
      setPlatforms(response.platforms || {});
    } catch (error) {
      toast.error('Failed to fetch credentials');
    } finally {
      setLoading(false);
    }
  };

  const handleSetupPlatform = (platformId) => {
    setSelectedPlatform(platformId);
    setShowSetup(true);
  };

  const handleSetupComplete = () => {
    setShowSetup(false);
    setSelectedPlatform(null);
    fetchCredentials();
    toast.success('Platform connected successfully!');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Social Media Credentials
        </h1>
        <p className="text-gray-600">
          Connect your social media accounts to enable AI automation
        </p>
      </div>

      {/* Connected Platforms */}
      {Object.keys(platforms).length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Connected Platforms
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(platforms).map(([platformId, platformData]) => (
              <PlatformCard
                key={platformId}
                platform={supportedPlatforms.find(p => p.id === platformId)}
                data={platformData}
                onReconnect={() => handleSetupPlatform(platformId)}
              />
            ))}
          </div>
        </div>
      )}

      {/* Available Platforms */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Available Platforms
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {supportedPlatforms
            .filter(platform => !platforms[platform.id])
            .map((platform) => (
              <div
                key={platform.id}
                className="card hover:shadow-md transition-shadow cursor-pointer"
                onClick={() => handleSetupPlatform(platform.id)}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-12 h-12 ${platform.color} rounded-lg flex items-center justify-center text-white text-xl`}>
                    {platform.icon}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                    <p className="text-sm text-gray-600">{platform.description}</p>
                  </div>
                </div>
                <button className="mt-4 w-full btn-primary">
                  Connect {platform.name}
                </button>
              </div>
            ))}
        </div>
      </div>

      {/* Setup Modal */}
      {showSetup && (
        <PlatformSetup
          platform={supportedPlatforms.find(p => p.id === selectedPlatform)}
          onComplete={handleSetupComplete}
          onCancel={() => setShowSetup(false)}
        />
      )}
    </div>
  );
};

export default CredentialsPage;
