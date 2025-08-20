import React from 'react';
import SecurePlatformConnection from '../../components/platforms/SecurePlatformConnection';

const PlatformsPage = () => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Platform Connections</h1>
          <p className="text-gray-600 mt-2">
            Connect your social media accounts securely using official OAuth 2.0 APIs
          </p>
        </div>
      </div>

      <SecurePlatformConnection />
    </div>
  );
};

export default PlatformsPage;