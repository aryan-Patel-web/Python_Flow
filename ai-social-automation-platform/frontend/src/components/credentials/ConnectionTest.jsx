import React, { useState, useEffect } from 'react';
import { 
  Play, 
  CheckCircle, 
  XCircle, 
  Clock, 
  AlertTriangle, 
  RefreshCw,
  Wifi,
  WifiOff,
  Settings,
  ExternalLink
} from 'lucide-react';

const ConnectionTest = ({ credentials, onTestComplete }) => {
  const [testResults, setTestResults] = useState({});
  const [testing, setTesting] = useState({});
  const [allTesting, setAllTesting] = useState(false);

  const testSteps = [
    {
      id: 'connection',
      name: 'Network Connection',
      description: 'Testing internet connectivity'
    },
    {
      id: 'authentication',
      name: 'Authentication',
      description: 'Verifying login credentials'
    },
    {
      id: 'permissions',
      name: 'Permissions',
      description: 'Checking account permissions'
    },
    {
      id: 'posting',
      name: 'Posting Capability',
      description: 'Testing content posting ability'
    }
  ];

  useEffect(() => {
    // Auto-run basic connection test on mount
    if (credentials && credentials.length > 0) {
      testBasicConnection();
    }
  }, [credentials]);

  const testBasicConnection = async () => {
    try {
      const response = await fetch('/api/credentials/test-connection', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      const data = await response.json();
      // Handle basic connection test results
    } catch (error) {
      console.error('Basic connection test failed:', error);
    }
  };

  const testSingleCredential = async (credentialId, platform) => {
    try {
      setTesting(prev => ({ ...prev, [credentialId]: true }));
      setTestResults(prev => ({ ...prev, [credentialId]: { status: 'testing', steps: {} } }));

      // Test each step
      for (const step of testSteps) {
        setTestResults(prev => ({
          ...prev,
          [credentialId]: {
            ...prev[credentialId],
            steps: {
              ...prev[credentialId].steps,
              [step.id]: { status: 'testing', message: 'Testing...' }
            }
          }
        }));

        await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate test delay

        const response = await fetch(`/api/credentials/test-step`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          },
          body: JSON.stringify({
            credential_id: credentialId,
            platform,
            step: step.id
          })
        });

        const stepResult = await response.json();
        
        setTestResults(prev => ({
          ...prev,
          [credentialId]: {
            ...prev[credentialId],
            steps: {
              ...prev[credentialId].steps,
              [step.id]: {
                status: stepResult.success ? 'success' : 'error',
                message: stepResult.message,
                details: stepResult.details
              }
            }
          }
        }));

        // If step fails, stop testing
        if (!stepResult.success) {
          setTestResults(prev => ({
            ...prev,
            [credentialId]: {
              ...prev[credentialId],
              status: 'failed',
              overallMessage: `Failed at ${step.name}: ${stepResult.message}`
            }
          }));
          break;
        }
      }

      // If all steps passed
      const allStepsPassed = testSteps.every(step => 
        testResults[credentialId]?.steps[step.id]?.status === 'success'
      );

      if (allStepsPassed) {
        setTestResults(prev => ({
          ...prev,
          [credentialId]: {
            ...prev[credentialId],
            status: 'success',
            overallMessage: 'All tests passed successfully!'
          }
        }));
      }

    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [credentialId]: {
          status: 'error',
          overallMessage: `Test failed: ${error.message}`,
          steps: {}
        }
      }));
    } finally {
      setTesting(prev => ({ ...prev, [credentialId]: false }));
    }
  };

  const testAllCredentials = async () => {
    setAllTesting(true);
    setTestResults({});

    for (const credential of credentials) {
      await testSingleCredential(credential.id, credential.platform);
    }

    setAllTesting(false);
    onTestComplete?.(testResults);
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'testing':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />;
      case 'success':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'error':
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'testing':
        return 'border-yellow-200 bg-yellow-50';
      case 'success':
        return 'border-green-200 bg-green-50';
      case 'error':
      case 'failed':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      instagram: '📷',
      facebook: '👥',
      youtube: '📹',
      twitter: '🐦',
      linkedin: '💼'
    };
    return icons[platform] || '📱';
  };

  if (!credentials || credentials.length === 0) {
    return (
      <div className="text-center py-8">
        <WifiOff className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Credentials to Test</h3>
        <p className="text-gray-600">Add some platform credentials first to test connections.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Connection Testing</h3>
          <p className="text-sm text-gray-600">Test your platform connections to ensure they're working properly</p>
        </div>
        <button
          onClick={testAllCredentials}
          disabled={allTesting}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          {allTesting ? (
            <>
              <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
              Testing All...
            </>
          ) : (
            <>
              <Play className="w-4 h-4 mr-2" />
              Test All Connections
            </>
          )}
        </button>
      </div>

      {/* Credential Tests */}
      <div className="space-y-4">
        {credentials.map((credential) => {
          const result = testResults[credential.id];
          const isCurrentlyTesting = testing[credential.id];
          
          return (
            <div
              key={credential.id}
              className={`border rounded-lg p-6 transition-all ${getStatusColor(result?.status)}`}
            >
              {/* Credential Header */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="text-2xl">
                    {getPlatformIcon(credential.platform)}
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">
                      {credential.platform.charAt(0).toUpperCase() + credential.platform.slice(1)}
                    </h4>
                    <p className="text-sm text-gray-600">{credential.account_name}</p>
                  </div>
                  {getStatusIcon(result?.status)}
                </div>
                
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => testSingleCredential(credential.id, credential.platform)}
                    disabled={isCurrentlyTesting}
                    className="flex items-center px-3 py-1 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors disabled:opacity-50"
                  >
                    {isCurrentlyTesting ? (
                      <RefreshCw className="w-4 h-4 mr-1 animate-spin" />
                    ) : (
                      <Play className="w-4 h-4 mr-1" />
                    )}
                    {isCurrentlyTesting ? 'Testing...' : 'Test'}
                  </button>
                  
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Overall Status */}
              {result?.overallMessage && (
                <div className={`p-3 rounded-md mb-4 ${
                  result.status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : result.status === 'failed' || result.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                }`}>
                  <p className="text-sm font-medium">{result.overallMessage}</p>
                </div>
              )}

              {/* Test Steps */}
              {result?.steps && Object.keys(result.steps).length > 0 && (
                <div className="space-y-3">
                  <h5 className="text-sm font-medium text-gray-700">Test Steps:</h5>
                  {testSteps.map((step) => {
                    const stepResult = result.steps[step.id];
                    if (!stepResult) return null;

                    return (
                      <div key={step.id} className="flex items-start space-x-3">
                        {getStatusIcon(stepResult.status)}
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <p className="text-sm font-medium text-gray-900">{step.name}</p>
                            <span className={`text-xs px-2 py-1 rounded-full ${
                              stepResult.status === 'success' 
                                ? 'bg-green-100 text-green-800'
                                : stepResult.status === 'error'
                                  ? 'bg-red-100 text-red-800'
                                  : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {stepResult.status}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600">{step.description}</p>
                          {stepResult.message && (
                            <p className="text-sm text-gray-700 mt-1">{stepResult.message}</p>
                          )}
                          {stepResult.details && (
                            <div className="mt-2 text-xs text-gray-600 bg-gray-50 rounded p-2">
                              <pre className="whitespace-pre-wrap">{JSON.stringify(stepResult.details, null, 2)}</pre>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}

              {/* Quick Actions */}
              {result?.status === 'success' && (
                <div className="mt-4 pt-4 border-t flex items-center space-x-4 text-sm">
                  <span className="text-green-600 font-medium">✓ Ready for automation</span>
                  <button className="text-blue-600 hover:text-blue-700 flex items-center">
                    <ExternalLink className="w-4 h-4 mr-1" />
                    View Account
                  </button>
                </div>
              )}

              {/* Error Actions */}
              {(result?.status === 'failed' || result?.status === 'error') && (
                <div className="mt-4 pt-4 border-t flex items-center justify-between">
                  <div className="flex items-center text-sm text-red-600">
                    <AlertTriangle className="w-4 h-4 mr-2" />
                    <span>Connection failed - check credentials</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="text-blue-600 hover:text-blue-700 text-sm">
                      Update Credentials
                    </button>
                    <button 
                      onClick={() => testSingleCredential(credential.id, credential.platform)}
                      className="text-gray-600 hover:text-gray-700 text-sm"
                    >
                      Retry Test
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Test Summary */}
      {Object.keys(testResults).length > 0 && (
        <div className="bg-white border rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">Test Summary</h4>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">
                {Object.values(testResults).filter(r => r.status === 'success').length}
              </div>
              <div className="text-sm text-gray-600">Passed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-600">
                {Object.values(testResults).filter(r => r.status === 'failed' || r.status === 'error').length}
              </div>
              <div className="text-sm text-gray-600">Failed</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-600">
                {Object.values(testResults).filter(r => r.status === 'testing').length}
              </div>
              <div className="text-sm text-gray-600">Testing</div>
            </div>
          </div>
        </div>
      )}

      {/* Help & Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💡 Testing Tips</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Make sure your credentials are correct and up-to-date</li>
          <li>• Some platforms may require 2FA verification</li>
          <li>• Check that your account has posting permissions</li>
          <li>• Network issues can cause temporary test failures</li>
        </ul>
      </div>
    </div>
  );
};

export default ConnectionTest;