import React from 'react';
import SecurePlatformConnection from '../../components/platforms/SecurePlatformConnection';

const Platforms = () => {
  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Page Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Platform Connections</h1>
          <p className="mt-2 text-lg text-gray-600">
            Connect your social media accounts securely using OAuth 2.0
          </p>
        </div>

        {/* Security Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="text-yellow-400 text-xl">⚠️</span>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-yellow-800">
                Important Security Update
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  We've upgraded to secure OAuth authentication. No more username/password forms! 
                  Your accounts are now connected using the same secure method as "Login with Google/Facebook".
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Secure Platform Connection Component */}
        <SecurePlatformConnection />

        {/* How It Works Section */}
        <div className="mt-12 bg-white rounded-lg shadow-sm border p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            How Secure Authentication Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl mb-3">1️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Click Connect</h3>
              <p className="text-sm text-gray-600">
                Choose the platform you want to connect
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl mb-3">2️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Platform Login</h3>
              <p className="text-sm text-gray-600">
                You'll be redirected to the platform's official login page
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl mb-3">3️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Authorize</h3>
              <p className="text-sm text-gray-600">
                Grant permissions for posting content on your behalf
              </p>
            </div>
            
            <div className="text-center">
              <div className="text-3xl mb-3">4️⃣</div>
              <h3 className="font-semibold text-gray-900 mb-2">Connected!</h3>
              <p className="text-sm text-gray-600">
                Secure connection established - no passwords stored
              </p>
            </div>
          </div>
        </div>

        {/* Security Features */}
        <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6 text-center">
            Why This Method is Infinitely More Secure
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="font-semibold text-red-600 mb-3">❌ Old Insecure Method</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• Required your actual passwords</li>
                <li>• Passwords stored in our database</li>
                <li>• Violated platform Terms of Service</li>
                <li>• Could lead to account suspension</li>
                <li>• No 2FA support</li>
                <li>• Single point of failure</li>
              </ul>
            </div>
            
            <div>
              <h3 className="font-semibold text-green-600 mb-3">✅ New Secure OAuth Method</h3>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• No passwords ever shared or stored</li>
                <li>• Platform-approved authentication</li>
                <li>• Complies with all Terms of Service</li>
                <li>• Supports 2FA and all security features</li>
                <li>• Revokable access anytime</li>
                <li>• Industry standard security</li>
              </ul>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border p-8">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Frequently Asked Questions</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Q: Is this the same as "Login with Google/Facebook"?
              </h3>
              <p className="text-gray-700">
                A: Yes! It's the exact same OAuth 2.0 technology. If you've ever used "Login with Google" 
                on any website, you're already familiar with this secure process.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Q: Can I revoke access if I change my mind?
              </h3>
              <p className="text-gray-700">
                A: Absolutely! You can disconnect anytime from your platform's security settings 
                or directly from our platform page. The access is instantly revoked.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Q: What if I have 2FA enabled on my accounts?
              </h3>
              <p className="text-gray-700">
                A: OAuth works perfectly with 2FA! The platform handles all security verification 
                during the authorization process.
              </p>
            </div>
            
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Q: Why did you change from username/password?
              </h3>
              <p className="text-gray-700">
                A: The old method violated platform Terms of Service and put user accounts at risk. 
                OAuth is the only secure, platform-approved method for automation tools.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Platforms;