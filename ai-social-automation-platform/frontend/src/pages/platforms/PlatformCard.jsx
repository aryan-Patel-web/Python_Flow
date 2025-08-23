import React, { useState } from 'react';
import { Shield, CheckCircle, X, ExternalLink, Lock, Loader } from 'lucide-react';

const PlatformCard = ({ 
  platform, 
  onConnect, 
  onDisconnect, 
  isConnected, 
  disabled, 
  loading 
}) => {
  const [showDetails, setShowDetails] = useState(false);

  const handleAction = () => {
    if (isConnected) {
      onDisconnect(platform);
    } else {
      onConnect(platform);
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-center space-x-4 mb-4">
        <div className={`w-12 h-12 bg-gradient-to-r ${platform.color} rounded-lg flex items-center justify-center text-white text-xl shadow-sm`}>
          {platform.icon}
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
          <div className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs ${
            isConnected 
              ? 'text-green-600 bg-green-100' 
              : 'text-blue-600 bg-blue-100'
          }`}>
            {isConnected ? (
              <>
                <CheckCircle className="w-3 h-3" />
                <span>Connected</span>
              </>
            ) : (
              <>
                <Shield className="w-3 h-3" />
                <span>OAuth 2.0</span>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-gray-600 mb-4">{platform.description}</p>

      {/* Security Features */}
      <div className="mb-4">
        <p className="text-sm font-medium text-gray-700 mb-2">Security Features:</p>
        <ul className="text-xs text-gray-500 space-y-1">
          <li className="flex items-center space-x-2">
            <Shield className="w-3 h-3 text-green-500" />
            <span>Official {platform.name} OAuth API</span>
          </li>
          <li className="flex items-center space-x-2">
            <Lock className="w-3 h-3 text-green-500" />
            <span>Encrypted token storage</span>
          </li>
          <li className="flex items-center space-x-2">
            <CheckCircle className="w-3 h-3 text-green-500" />
            <span>Revokable access</span>
          </li>
        </ul>
      </div>

      {/* Scopes (if details shown) */}
      {showDetails && platform.scopes && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg">
          <p className="text-sm font-medium text-gray-700 mb-2">Permissions requested:</p>
          <ul className="text-xs text-gray-600 space-y-1">
            {platform.scopes.map((scope, index) => (
              <li key={index} className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                <span>{scope}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Actions */}
      <div className="space-y-2">
        <button
          onClick={handleAction}
          disabled={disabled || loading}
          className={`w-full py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center justify-center space-x-2 ${
            isConnected
              ? 'bg-red-50 text-red-600 border border-red-200 hover:bg-red-100 hover:border-red-300'
              : disabled || loading
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-blue-600 text-white hover:bg-blue-700 shadow-sm hover:shadow'
          }`}
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              <span>Connecting...</span>
            </>
          ) : isConnected ? (
            <>
              <X className="w-4 h-4" />
              <span>Disconnect</span>
            </>
          ) : (
            <>
              <ExternalLink className="w-4 h-4" />
              <span>Connect Securely</span>
            </>
          )}
        </button>

        {/* Details Toggle */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="w-full py-1.5 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      {/* Connection Status */}
      {isConnected && (
        <div className="mt-3 p-2 bg-green-50 rounded-lg">
          <p className="text-xs text-green-700 text-center">
            ✓ Ready for automation
          </p>
        </div>
      )}
    </div>
  );
};

export default PlatformCard;