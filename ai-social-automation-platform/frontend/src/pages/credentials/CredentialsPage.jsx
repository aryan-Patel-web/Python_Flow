import { useState } from 'react'
import { 
  Key, 
  Shield, 
  Plus, 
  Instagram, 
  Facebook, 
  Linkedin, 
  Youtube, 
  Twitter,
  CheckCircle,
  XCircle,
  AlertTriangle
} from 'lucide-react'

const CredentialsPage = () => {
  const [showAddModal, setShowAddModal] = useState(false)
  const [selectedPlatform, setSelectedPlatform] = useState(null)

  const platforms = [
    {
      name: 'Instagram',
      icon: Instagram,
      status: 'connected',
      lastVerified: '2 hours ago',
      description: 'Post images, reels, and stories automatically',
      color: 'from-pink-500 to-purple-600'
    },
    {
      name: 'Facebook',
      icon: Facebook,
      status: 'connected',
      lastVerified: '1 day ago',
      description: 'Share posts, images, and videos to your page',
      color: 'from-blue-600 to-blue-700'
    },
    {
      name: 'LinkedIn',
      icon: Linkedin,
      status: 'connected',
      lastVerified: '3 hours ago',
      description: 'Professional content and networking posts',
      color: 'from-blue-700 to-blue-800'
    },
    {
      name: 'YouTube',
      icon: Youtube,
      status: 'warning',
      lastVerified: '1 week ago',
      description: 'Upload videos and manage your channel',
      color: 'from-red-600 to-red-700'
    },
    {
      name: 'Twitter',
      icon: Twitter,
      status: 'disconnected',
      lastVerified: 'Never',
      description: 'Tweet content and engage with followers',
      color: 'from-sky-500 to-sky-600'
    }
  ]

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-600" />
      case 'disconnected':
        return <XCircle className="w-5 h-5 text-red-600" />
      default:
        return <XCircle className="w-5 h-5 text-gray-600" />
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'connected':
        return 'Connected'
      case 'warning':
        return 'Needs Attention'
      case 'disconnected':
        return 'Not Connected'
      default:
        return 'Unknown'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'connected':
        return 'text-green-700 bg-green-50 border-green-200'
      case 'warning':
        return 'text-yellow-700 bg-yellow-50 border-yellow-200'
      case 'disconnected':
        return 'text-red-700 bg-red-50 border-red-200'
      default:
        return 'text-gray-700 bg-gray-50 border-gray-200'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Platform Credentials
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Connect your social media accounts to enable automated posting
          </p>
        </div>
        <div className="mt-4 flex md:ml-4 md:mt-0">
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Add Platform</span>
          </button>
        </div>
      </div>

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start space-x-3">
          <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="text-sm font-medium text-blue-900">Security & Privacy</h3>
            <p className="text-sm text-blue-700 mt-1">
              Your credentials are encrypted with AES-256 encryption and stored securely. 
              We never store your passwords in plain text and only use them to authenticate 
              with social media platforms on your behalf.
            </p>
          </div>
        </div>
      </div>

      {/* Platform Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {platforms.map((platform) => {
          const Icon = platform.icon
          return (
            <div key={platform.name} className="bg-white rounded-lg shadow-sm border overflow-hidden">
              {/* Platform Header */}
              <div className={`h-20 bg-gradient-to-r ${platform.color} flex items-center justify-center`}>
                <Icon className="w-8 h-8 text-white" />
              </div>

              {/* Platform Content */}
              <div className="p-6">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                  <div className={`flex items-center space-x-1 px-2 py-1 rounded-full text-xs font-medium border ${getStatusColor(platform.status)}`}>
                    {getStatusIcon(platform.status)}
                    <span>{getStatusText(platform.status)}</span>
                  </div>
                </div>

                <p className="text-sm text-gray-600 mb-4">
                  {platform.description}
                </p>

                <div className="space-y-3">
                  <div className="text-xs text-gray-500">
                    Last verified: {platform.lastVerified}
                  </div>

                  <div className="flex space-x-2">
                    {platform.status === 'connected' ? (
                      <>
                        <button className="flex-1 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors">
                          Test Connection
                        </button>
                        <button className="flex-1 px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                          Disconnect
                        </button>
                      </>
                    ) : platform.status === 'warning' ? (
                      <>
                        <button className="flex-1 px-3 py-2 text-sm font-medium text-white bg-yellow-600 rounded-lg hover:bg-yellow-700 transition-colors">
                          Reconnect
                        </button>
                        <button className="flex-1 px-3 py-2 text-sm font-medium text-red-700 bg-red-50 rounded-lg hover:bg-red-100 transition-colors">
                          Remove
                        </button>
                      </>
                    ) : (
                      <button
                        onClick={() => {
                          setSelectedPlatform(platform)
                          setShowAddModal(true)
                        }}
                        className="w-full px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
                      >
                        Connect Account
                      </button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Add Platform Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto">
          <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={() => setShowAddModal(false)}></div>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="sm:flex sm:items-start">
                  <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 sm:mx-0 sm:h-10 sm:w-10">
                    <Key className="h-6 w-6 text-blue-600" />
                  </div>
                  <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">
                      Connect {selectedPlatform?.name || 'Platform'}
                    </h3>
                    <div className="mt-2">
                      <p className="text-sm text-gray-500">
                        Enter your {selectedPlatform?.name || 'platform'} credentials to enable automated posting.
                      </p>
                    </div>
                  </div>
                </div>

                <form className="mt-6 space-y-4">
                  <div>
                    <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                      Username/Email
                    </label>
                    <input
                      type="text"
                      id="username"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2"
                      placeholder="Enter your username or email"
                    />
                  </div>
                  <div>
                    <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                      Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 sm:text-sm px-3 py-2"
                      placeholder="Enter your password"
                    />
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3">
                    <div className="flex">
                      <AlertTriangle className="h-5 w-5 text-yellow-400" />
                      <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                          <strong>Security Note:</strong> Your credentials are encrypted and stored securely. 
                          We recommend using app passwords when available.
                        </p>
                      </div>
                    </div>
                  </div>
                </form>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button
                  type="button"
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Connect Account
                </button>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Usage Guidelines */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Guidelines</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Best Practices</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Use app passwords when available</li>
              <li>• Enable 2FA on your social accounts</li>
              <li>• Regularly verify your connections</li>
              <li>• Monitor posting limits to avoid restrictions</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-gray-900 mb-2">Troubleshooting</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Check if your account has 2FA enabled</li>
              <li>• Verify your credentials are correct</li>
              <li>• Ensure your account isn't restricted</li>
              <li>• Contact support if issues persist</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CredentialsPage