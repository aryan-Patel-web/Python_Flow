import React, { useState } from 'react';
import { Eye, EyeOff, Save, TestTube, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useToast } from '../common/Toast';

const CredentialForm = ({ platform, existingCredentials = null, onSave, onCancel }) => {
  const [credentials, setCredentials] = useState(existingCredentials || {});
  const [showPasswords, setShowPasswords] = useState({});
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testResult, setTestResult] = useState(null);
  const [errors, setErrors] = useState({});
  const { toast } = useToast();

  const platformConfigs = {
    instagram: {
      name: 'Instagram',
      icon: '📷',
      color: 'pink',
      fields: [
        { 
          key: 'username', 
          label: 'Username', 
          type: 'text', 
          required: true, 
          placeholder: 'your_username',
          help: 'Your Instagram username without the @ symbol'
        },
        { 
          key: 'password', 
          label: 'Password', 
          type: 'password', 
          required: true, 
          placeholder: 'Your Instagram password',
          help: 'Your Instagram account password'
        },
        { 
          key: 'email', 
          label: 'Email (Optional)', 
          type: 'email', 
          required: false, 
          placeholder: 'your@email.com',
          help: 'Email associated with your Instagram account'
        }
      ]
    },
    facebook: {
      name: 'Facebook',
      icon: '👥',
      color: 'blue',
      fields: [
        { 
          key: 'email', 
          label: 'Email', 
          type: 'email', 
          required: true, 
          placeholder: 'your@email.com',
          help: 'Your Facebook login email'
        },
        { 
          key: 'password', 
          label: 'Password', 
          type: 'password', 
          required: true, 
          placeholder: 'Your Facebook password',
          help: 'Your Facebook account password'
        },
        { 
          key: 'page_id', 
          label: 'Page ID (Optional)', 
          type: 'text', 
          required: false, 
          placeholder: '123456789',
          help: 'Facebook Page ID for posting to pages instead of profile'
        }
      ]
    },
    youtube: {
      name: 'YouTube',
      icon: '📹',
      color: 'red',
      fields: [
        { 
          key: 'email', 
          label: 'Google Email', 
          type: 'email', 
          required: true, 
          placeholder: 'your@gmail.com',
          help: 'Your Google/YouTube account email'
        },
        { 
          key: 'password', 
          label: 'Password', 
          type: 'password', 
          required: true, 
          placeholder: 'Your Google password',
          help: 'Your Google account password'
        },
        { 
          key: 'channel_id', 
          label: 'Channel ID (Optional)', 
          type: 'text', 
          required: false, 
          placeholder: 'UCxxxxxxxxxxxxxxxxx',
          help: 'Your YouTube channel ID (found in YouTube Studio)'
        }
      ]
    },
    twitter: {
      name: 'Twitter',
      icon: '🐦',
      color: 'sky',
      fields: [
        { 
          key: 'username', 
          label: 'Username', 
          type: 'text', 
          required: true, 
          placeholder: 'your_handle',
          help: 'Your Twitter username without the @ symbol'
        },
        { 
          key: 'password', 
          label: 'Password', 
          type: 'password', 
          required: true, 
          placeholder: 'Your Twitter password',
          help: 'Your Twitter account password'
        }
      ]
    },
    linkedin: {
      name: 'LinkedIn',
      icon: '💼',
      color: 'indigo',
      fields: [
        { 
          key: 'email', 
          label: 'Email', 
          type: 'email', 
          required: true, 
          placeholder: 'your@email.com',
          help: 'Your LinkedIn account email'
        },
        { 
          key: 'password', 
          label: 'Password', 
          type: 'password', 
          required: true, 
          placeholder: 'Your LinkedIn password',
          help: 'Your LinkedIn account password'
        },
        { 
          key: 'company_page_id', 
          label: 'Company Page (Optional)', 
          type: 'text', 
          required: false, 
          placeholder: 'company-name',
          help: 'Company page identifier for business posting'
        }
      ]
    }
  };

  const config = platformConfigs[platform] || {};

  const handleInputChange = (key, value) => {
    setCredentials(prev => ({
      ...prev,
      [key]: value
    }));
    
    // Clear field error when user starts typing
    if (errors[key]) {
      setErrors(prev => ({
        ...prev,
        [key]: null
      }));
    }
    
    // Clear test result when credentials change
    if (testResult) {
      setTestResult(null);
    }
  };

  const togglePasswordVisibility = (fieldKey) => {
    setShowPasswords(prev => ({
      ...prev,
      [fieldKey]: !prev[fieldKey]
    }));
  };

  const validateForm = () => {
    const newErrors = {};
    const requiredFields = config.fields?.filter(field => field.required) || [];
    
    requiredFields.forEach(field => {
      if (!credentials[field.key]?.trim()) {
        newErrors[field.key] = `${field.label} is required`;
      }
    });

    // Email validation
    const emailFields = config.fields?.filter(field => field.type === 'email') || [];
    emailFields.forEach(field => {
      const value = credentials[field.key];
      if (value && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) {
        newErrors[field.key] = 'Please enter a valid email address';
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const testConnection = async () => {
    if (!validateForm()) {
      toast.error('Please fix the form errors before testing');
      return;
    }

    try {
      setTesting(true);
      setTestResult(null);

      const response = await fetch('/api/credentials/test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          platform,
          credentials
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        setTestResult({
          success: true,
          message: 'Connection successful!',
          accountInfo: data.account_info
        });
        toast.success('Credentials verified successfully!');
      } else {
        setTestResult({
          success: false,
          message: data.error || 'Connection failed'
        });
        toast.error('Connection test failed');
      }
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Network error occurred'
      });
      toast.error('Failed to test connection');
    } finally {
      setTesting(false);
    }
  };

  const handleSave = async () => {
    if (!validateForm()) {
      toast.error('Please fix the form errors before saving');
      return;
    }

    try {
      setSaving(true);

      const response = await fetch('/api/credentials', {
        method: existingCredentials ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          platform,
          credentials,
          account_name: credentials.username || credentials.email || `${config.name} Account`
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        toast.success(`${config.name} credentials saved successfully!`);
        onSave?.(data);
      } else {
        toast.error(data.error || 'Failed to save credentials');
      }
    } catch (error) {
      toast.error('Failed to save credentials');
    } finally {
      setSaving(false);
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      pink: 'border-pink-300 focus:border-pink-500 focus:ring-pink-500',
      blue: 'border-blue-300 focus:border-blue-500 focus:ring-blue-500',
      red: 'border-red-300 focus:border-red-500 focus:ring-red-500',
      sky: 'border-sky-300 focus:border-sky-500 focus:ring-sky-500',
      indigo: 'border-indigo-300 focus:border-indigo-500 focus:ring-indigo-500'
    };
    return colors[color] || colors.blue;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <div className={`w-16 h-16 mx-auto rounded-full bg-${config.color}-50 border border-${config.color}-200 flex items-center justify-center text-2xl mb-4`}>
          {config.icon}
        </div>
        <h2 className="text-2xl font-bold text-gray-900">{config.name} Credentials</h2>
        <p className="text-gray-600 mt-2">
          {existingCredentials ? 'Update your' : 'Enter your'} {config.name} account details
        </p>
      </div>

      {/* Form Fields */}
      <div className="space-y-4">
        {config.fields?.map((field) => (
          <div key={field.key}>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {field.label}
              {field.required && <span className="text-red-500 ml-1">*</span>}
            </label>
            
            <div className="relative">
              <input
                type={field.type === 'password' && !showPasswords[field.key] ? 'password' : 'text'}
                placeholder={field.placeholder}
                value={credentials[field.key] || ''}
                onChange={(e) => handleInputChange(field.key, e.target.value)}
                className={`
                  w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-opacity-50
                  ${errors[field.key] 
                    ? 'border-red-300 focus:border-red-500 focus:ring-red-500' 
                    : getColorClasses(config.color)
                  }
                `}
                required={field.required}
              />
              
              {field.type === 'password' && (
                <button
                  type="button"
                  onClick={() => togglePasswordVisibility(field.key)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPasswords[field.key] ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              )}
            </div>

            {errors[field.key] && (
              <p className="text-red-500 text-sm mt-1 flex items-center">
                <AlertCircle className="w-4 h-4 mr-1" />
                {errors[field.key]}
              </p>
            )}

            {field.help && !errors[field.key] && (
              <p className="text-gray-500 text-sm mt-1">{field.help}</p>
            )}
          </div>
        ))}
      </div>

      {/* Test Result */}
      {testResult && (
        <div className={`p-4 rounded-lg border ${
          testResult.success 
            ? 'bg-green-50 border-green-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-start">
            {testResult.success ? (
              <CheckCircle className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500 mr-2 mt-0.5" />
            )}
            <div>
              <p className={`text-sm font-medium ${
                testResult.success ? 'text-green-800' : 'text-red-800'
              }`}>
                {testResult.message}
              </p>
              {testResult.success && testResult.accountInfo && (
                <div className="mt-2 text-sm text-green-700">
                  <p>✓ Account verified successfully</p>
                  {testResult.accountInfo.username && (
                    <p>✓ Username: {testResult.accountInfo.username}</p>
                  )}
                  {testResult.accountInfo.email && (
                    <p>✓ Email: {testResult.accountInfo.email}</p>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Security Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="w-5 h-5 text-blue-500 mr-2 mt-0.5" />
          <div className="text-sm text-blue-800">
            <p className="font-medium mb-1">🔒 Security Notice</p>
            <p>Your credentials are encrypted using AES-256 encryption and stored securely. We never store passwords in plain text and use industry-standard security practices.</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-3 pt-4">
        <button
          onClick={onCancel}
          className="flex-1 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
        
        <button
          onClick={testConnection}
          disabled={testing || Object.keys(errors).length > 0}
          className={`flex-1 px-4 py-2 text-sm font-medium rounded-md transition-colors flex items-center justify-center
            ${testing 
              ? 'bg-gray-400 text-white cursor-not-allowed' 
              : `text-${config.color}-700 bg-${config.color}-50 border border-${config.color}-200 hover:bg-${config.color}-100`
            }`}
        >
          {testing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Testing...
            </>
          ) : (
            <>
              <TestTube className="w-4 h-4 mr-2" />
              Test Connection
            </>
          )}
        </button>
        
        <button
          onClick={handleSave}
          disabled={saving || Object.keys(errors).length > 0}
          className={`flex-1 px-4 py-2 text-sm font-medium text-white rounded-md transition-colors flex items-center justify-center
            ${saving 
              ? 'bg-gray-400 cursor-not-allowed' 
              : `bg-${config.color}-600 hover:bg-${config.color}-700`
            }`}
        >
          {saving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-2" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              {existingCredentials ? 'Update' : 'Save'} Credentials
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default CredentialForm;