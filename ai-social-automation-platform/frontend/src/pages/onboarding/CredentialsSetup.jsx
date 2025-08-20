import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  ArrowRight, 
  ArrowLeft, 
  CheckCircle, 
  AlertCircle, 
  Instagram, 
  Facebook, 
  Youtube, 
  Linkedin, 
  Twitter,
  Lock,
  Shield,
  Eye,
  EyeOff,
  Plus
} from 'lucide-react'
import Button from '../../components/common/Button'
import Input from '../../components/common/Input'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import { useAuth } from '../../context/AuthContext'
import useCredentials from '../../hooks/useCredentials'
import useToast from '../../hooks/useToast'

const CredentialsSetup = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { saveCredentials, testConnection, testing } = useCredentials()
  const { success, error: showError } = useToast()
  
  const [selectedPlatforms, setSelectedPlatforms] = useState([])
  const [credentials, setCredentials] = useState({})
  const [showPasswords, setShowPasswords] = useState({})
  const [connectionStatus, setConnectionStatus] = useState({})
  const [currentStep, setCurrentStep] = useState('selection') // 'selection', 'credentials'

  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: '#E1306C',
      description: 'Share photos, stories, and reels with your audience',
      fields: ['username', 'password'],
      placeholder: { username: 'your_username', password: 'your_password' },
      tips: 'Make sure your account is set to Business or Creator account for best results.'
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: '#1877F2',
      description: 'Connect with your audience through posts and videos',
      fields: ['email', 'password'],
      placeholder: { email: 'your@email.com', password: 'your_password' },
      tips: 'Ensure you have admin access to the Facebook page you want to manage.'
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      color: '#FF0000',
      description: 'Upload and share video content with the world',
      fields: ['email', 'password'],
      placeholder: { email: 'your@gmail.com', password: 'your_password' },
      tips: 'Your Google account should have access to the YouTube channel you want to manage.'
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      color: '#0A66C2',
      description: 'Professional networking and thought leadership',
      fields: ['email', 'password'],
      placeholder: { email: 'your@email.com', password: 'your_password' },
      tips: 'Personal profiles work best. Company pages require special permissions.'
    },
    {
      id: 'twitter',
      name: 'Twitter',
      icon: Twitter,
      color: '#1DA1F2',
      description: 'Share thoughts and engage in real-time conversations',
      fields: ['username', 'password'],
      placeholder: { username: 'your_username', password: 'your_password' },
      tips: 'Make sure your account has posting permissions enabled.'
    }
  ]

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    )
  }

  const handleNextStep = () => {
    if (selectedPlatforms.length === 0) {
      showError('Please select at least one platform to continue')
      return
    }
    setCurrentStep('credentials')
  }

  const handleCredentialChange = (platformId, field, value) => {
    setCredentials(prev => ({
      ...prev,
      [platformId]: {
        ...prev[platformId],
        [field]: value
      }
    }))
  }

  const togglePasswordVisibility = (platformId, field) => {
    setShowPasswords(prev => ({
      ...prev,
      [`${platformId}_${field}`]: !prev[`${platformId}_${field}`]
    }))
  }

  const handleTestConnection = async (platformId) => {
    const platform = platforms.find(p => p.id === platformId)
    const platformCredentials = credentials[platformId]

    if (!platformCredentials) {
      showError('Please enter your credentials first')
      return
    }

    // Validate required fields
    const missingFields = platform.fields.filter(field => !platformCredentials[field]?.trim())
    if (missingFields.length > 0) {
      showError(`Please fill in all required fields: ${missingFields.join(', ')}`)
      return
    }

    try {
      const result = await testConnection(platformId, {
        platformType: platformId,
        ...platformCredentials
      })

      if (result.success) {
        setConnectionStatus(prev => ({ ...prev, [platformId]: 'success' }))
        success(`${platform.name} connected successfully!`)
      } else {
        setConnectionStatus(prev => ({ ...prev, [platformId]: 'error' }))
        showError(result.error || `Failed to connect to ${platform.name}`)
      }
    } catch (error) {
      setConnectionStatus(prev => ({ ...prev, [platformId]: 'error' }))
      showError(`Connection to ${platform.name} failed`)
    }
  }

  const handleSaveAndContinue = async () => {
    const connectedPlatforms = selectedPlatforms.filter(id => connectionStatus[id] === 'success')
    
    if (connectedPlatforms.length === 0) {
      showError('Please test and connect at least one platform before continuing')
      return
    }

    try {
      // Save all connected platforms
      for (const platformId of connectedPlatforms) {
        await saveCredentials({
          platformType: platformId,
          isConnected: true,
          ...credentials[platformId]
        })
      }

      success(`Successfully connected ${connectedPlatforms.length} platform(s)!`)
      navigate('/onboarding/domain-setup')
    } catch (error) {
      showError('Failed to save platform connections')
    }
  }

  const handleBack = () => {
    if (currentStep === 'credentials') {
      setCurrentStep('selection')
    } else {
      navigate('/onboarding/plan-selection')
    }
  }

  const handleSkip = () => {
    navigate('/onboarding/domain-setup')
  }

  const getConnectionIcon = (platformId) => {
    const status = connectionStatus[platformId]
    const isTestingPlatform = testing[platformId]

    if (isTestingPlatform) {
      return <LoadingSpinner className="w-5 h-5" />
    }
    
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Connect Your Platforms</h1>
              <p className="text-gray-600">
                {currentStep === 'selection' 
                  ? 'Choose which social media platforms you want to automate'
                  : 'Enter your credentials to connect your accounts'
                }
              </p>
            </div>
            <div className="text-sm text-gray-500">
              Step 2 of 4
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {currentStep === 'selection' ? (
          <>
            {/* Security Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
              <div className="flex items-start space-x-3">
                <Shield className="w-6 h-6 text-blue-600 mt-1" />
                <div>
                  <h3 className="font-semibold text-blue-900 mb-2">🔒 Your Security is Our Priority</h3>
                  <p className="text-blue-800 text-sm">
                    We use military-grade encryption to protect your credentials. Your passwords are encrypted 
                    and stored securely. You can revoke access at any time from your dashboard.
                  </p>
                </div>
              </div>
            </div>

            {/* Platform Selection */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Select Platforms to Connect</h2>
              
              <div className="grid md:grid-cols-2 gap-6">
                {platforms.map((platform) => (
                  <div
                    key={platform.id}
                    onClick={() => handlePlatformToggle(platform.id)}
                    className={`relative p-6 border-2 rounded-lg cursor-pointer transition-all ${
                      selectedPlatforms.includes(platform.id)
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start space-x-4">
                      <div 
                        className="w-12 h-12 rounded-lg flex items-center justify-center text-white flex-shrink-0"
                        style={{ backgroundColor: platform.color }}
                      >
                        <platform.icon className="w-6 h-6" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 mb-2">{platform.name}</h3>
                        <p className="text-sm text-gray-600 mb-3">{platform.description}</p>
                        <p className="text-xs text-gray-500">{platform.tips}</p>
                      </div>
                    </div>
                    
                    {selectedPlatforms.includes(platform.id) && (
                      <div className="absolute top-4 right-4">
                        <CheckCircle className="w-6 h-6 text-blue-600" />
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {selectedPlatforms.length > 0 && (
                <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 text-sm">
                    ✓ {selectedPlatforms.length} platform(s) selected: {selectedPlatforms.map(id => 
                      platforms.find(p => p.id === id)?.name
                    ).join(', ')}
                  </p>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            {/* Credentials Form */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Enter Your Credentials</h2>
              
              <div className="space-y-8">
                {selectedPlatforms.map((platformId) => {
                  const platform = platforms.find(p => p.id === platformId)
                  return (
                    <div key={platformId} className="border border-gray-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div 
                            className="w-8 h-8 rounded-lg flex items-center justify-center text-white"
                            style={{ backgroundColor: platform.color }}
                          >
                            <platform.icon className="w-4 h-4" />
                          </div>
                          <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                        </div>
                        {getConnectionIcon(platformId)}
                      </div>

                      <div className="grid md:grid-cols-2 gap-4 mb-4">
                        {platform.fields.map((field) => (
                          <div key={field}>
                            <label className="block text-sm font-medium text-gray-700 mb-2 capitalize">
                              {field} <span className="text-red-500">*</span>
                            </label>
                            <div className="relative">
                              <Input
                                type={field === 'password' && !showPasswords[`${platformId}_${field}`] ? 'password' : 'text'}
                                placeholder={platform.placeholder[field]}
                                value={credentials[platformId]?.[field] || ''}
                                onChange={(e) => handleCredentialChange(platformId, field, e.target.value)}
                                className="pr-10"
                              />
                              {field === 'password' && (
                                <button
                                  type="button"
                                  onClick={() => togglePasswordVisibility(platformId, field)}
                                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                >
                                  {showPasswords[`${platformId}_${field}`] ? (
                                    <EyeOff className="w-4 h-4" />
                                  ) : (
                                    <Eye className="w-4 h-4" />
                                  )}
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center justify-between">
                        <Button
                          onClick={() => handleTestConnection(platformId)}
                          disabled={testing[platformId] || !credentials[platformId]}
                          variant="outline"
                          size="sm"
                        >
                          {testing[platformId] ? 'Testing...' : 'Test Connection'}
                        </Button>

                        {connectionStatus[platformId] === 'error' && (
                          <span className="text-sm text-red-600">Connection failed</span>
                        )}

                        {connectionStatus[platformId] === 'success' && (
                          <span className="text-sm text-green-600">✓ Connected</span>
                        )}
                      </div>

                      {connectionStatus[platformId] === 'error' && (
                        <div className="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
                          <p className="text-sm text-red-600">
                            Connection failed. Please verify your credentials and try again.
                          </p>
                        </div>
                      )}

                      {connectionStatus[platformId] === 'success' && (
                        <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <p className="text-sm text-green-600">
                            Successfully connected to {platform.name}! AI can now post to this account.
                          </p>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
            </div>

            {/* Help Section */}
            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <h3 className="font-semibold text-gray-900 mb-4">💡 Having trouble connecting?</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-gray-600">
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Common Issues:</h4>
                  <ul className="space-y-1">
                    <li>• Double-check your username/email and password</li>
                    <li>• Ensure 2FA is disabled temporarily</li>
                    <li>• Try logging into the platform directly first</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-gray-800 mb-2">Security Notes:</h4>
                  <ul className="space-y-1">
                    <li>• We only use your credentials to post content</li>
                    <li>• Your passwords are encrypted and secure</li>
                    <li>• You can revoke access anytime</li>
                  </ul>
                </div>
              </div>
            </div>
          </>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            onClick={handleBack}
            variant="outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="flex space-x-4">
            <Button
              onClick={handleSkip}
              variant="outline"
            >
              Skip for now
            </Button>
            
            {currentStep === 'selection' ? (
              <Button
                onClick={handleNextStep}
                disabled={selectedPlatforms.length === 0}
              >
                Continue ({selectedPlatforms.length} selected)
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            ) : (
              <Button
                onClick={handleSaveAndContinue}
                disabled={selectedPlatforms.filter(id => connectionStatus[id] === 'success').length === 0}
              >
                Continue
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default CredentialsSetup