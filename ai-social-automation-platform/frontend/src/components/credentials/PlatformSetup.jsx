import { useState } from 'react'
import { X, Plus, Settings, AlertCircle, CheckCircle } from 'lucide-react'
import Button from '../common/Button'
import Input from '../common/Input'
import Modal from '../common/Modal'
import { PLATFORMS } from '../../utils/constants'

const PlatformSetup = ({ isOpen, onClose, platform, onSave }) => {
  const [credentials, setCredentials] = useState({
    apiKey: '',
    apiSecret: '',
    accessToken: '',
    accessTokenSecret: '',
    pageId: '',
    appId: '',
    appSecret: ''
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [connectionStatus, setConnectionStatus] = useState(null)
  
  const platformConfig = PLATFORMS.find(p => p.id === platform?.id)
  
  const handleInputChange = (field, value) => {
    setCredentials(prev => ({
      ...prev,
      [field]: value
    }))
  }
  
  const testConnection = async () => {
    setIsLoading(true)
    setConnectionStatus(null)
    
    try {
      // Simulate API call to test connection
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      // Mock validation
      const hasRequiredFields = platformConfig?.requiredFields.every(
        field => credentials[field]?.trim()
      )
      
      if (hasRequiredFields) {
        setConnectionStatus({ success: true, message: 'Connection successful!' })
      } else {
        setConnectionStatus({ 
          success: false, 
          message: 'Please fill all required fields' 
        })
      }
    } catch (error) {
      setConnectionStatus({ 
        success: false, 
        message: 'Connection failed. Please check your credentials.' 
      })
    }
    
    setIsLoading(false)
  }
  
  const handleSave = async () => {
    if (!connectionStatus?.success) {
      await testConnection()
      return
    }
    
    const platformData = {
      ...platform,
      credentials,
      isConnected: true,
      lastUpdated: new Date().toISOString()
    }
    
    onSave(platformData)
    onClose()
  }
  
  const renderCredentialField = (field) => {
    const fieldConfig = {
      apiKey: { label: 'API Key', type: 'password', placeholder: 'Enter your API key' },
      apiSecret: { label: 'API Secret', type: 'password', placeholder: 'Enter your API secret' },
      accessToken: { label: 'Access Token', type: 'password', placeholder: 'Enter access token' },
      accessTokenSecret: { label: 'Access Token Secret', type: 'password', placeholder: 'Enter token secret' },
      pageId: { label: 'Page ID', type: 'text', placeholder: 'Enter page/channel ID' },
      appId: { label: 'App ID', type: 'text', placeholder: 'Enter application ID' },
      appSecret: { label: 'App Secret', type: 'password', placeholder: 'Enter app secret' }
    }
    
    const config = fieldConfig[field]
    if (!config) return null
    
    return (
      <div key={field} className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          {config.label}
          {platformConfig?.requiredFields.includes(field) && (
            <span className="text-red-500 ml-1">*</span>
          )}
        </label>
        <Input
          type={config.type}
          placeholder={config.placeholder}
          value={credentials[field]}
          onChange={(e) => handleInputChange(field, e.target.value)}
          className="w-full"
        />
      </div>
    )
  }
  
  if (!platform || !platformConfig) return null
  
  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Setup ${platform.name}`}>
      <div className="space-y-6">
        {/* Platform Info */}
        <div className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
          <platform.icon className="w-12 h-12" style={{ color: platform.color }} />
          <div>
            <h3 className="font-semibold text-gray-900">{platform.name}</h3>
            <p className="text-sm text-gray-600">{platformConfig.description}</p>
          </div>
        </div>
        
        {/* Setup Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">Setup Instructions:</h4>
          <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
            {platformConfig.instructions.map((instruction, index) => (
              <li key={index}>{instruction}</li>
            ))}
          </ol>
        </div>
        
        {/* Credential Fields */}
        <div className="space-y-4">
          <h4 className="font-medium text-gray-900">Enter Your Credentials</h4>
          {platformConfig.requiredFields.map(renderCredentialField)}
        </div>
        
        {/* Connection Status */}
        {connectionStatus && (
          <div className={`flex items-center space-x-2 p-3 rounded-lg ${
            connectionStatus.success 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            {connectionStatus.success ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <span className={`text-sm ${
              connectionStatus.success ? 'text-green-800' : 'text-red-800'
            }`}>
              {connectionStatus.message}
            </span>
          </div>
        )}
        
        {/* Action Buttons */}
        <div className="flex space-x-3 pt-4 border-t">
          <Button
            variant="outline"
            onClick={testConnection}
            disabled={isLoading}
            className="flex-1"
          >
            {isLoading ? 'Testing...' : 'Test Connection'}
          </Button>
          <Button
            onClick={handleSave}
            disabled={isLoading || !connectionStatus?.success}
            className="flex-1"
          >
            Save Platform
          </Button>
        </div>
      </div>
    </Modal>
  )
}

export default PlatformSetup