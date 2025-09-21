import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [networkError, setNetworkError] = useState(false);
  const [debugInfo, setDebugInfo] = useState('');

  const { login, isAuthenticated, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Platform routes mapping
  const platformRoutes = {
    whatsapp: '/whatsapp',
    facebook: '/facebook', 
    instagram: '/instagram',
    youtube: '/youtube',
    reddit: '/reddit-auto',
    default: '/whatsapp'
  };

  // Get the platform from URL or default
  const getPlatformFromPath = () => {
    const path = location.state?.from?.pathname || location.pathname;
    for (const [platform, route] of Object.entries(platformRoutes)) {
      if (path.includes(platform) || path === route) {
        return route;
      }
    }
    return platformRoutes.default;
  };

  const targetPlatform = getPlatformFromPath();

  // If already authenticated, redirect
  useEffect(() => {
    if (isAuthenticated && user) {
      navigate(targetPlatform, { replace: true });
    }
  }, [isAuthenticated, user, navigate, targetPlatform]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear errors when user starts typing
    if (error) setError('');
    if (networkError) setNetworkError(false);
    if (debugInfo) setDebugInfo('');
  };

  const validateForm = () => {
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      return false;
    }

    if (!formData.email.includes('@')) {
      setError('Please enter a valid email address');
      return false;
    }

    if (formData.password.length < 3) {
      setError('Password must be at least 3 characters long');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setNetworkError(false);
    setDebugInfo('');

    if (!validateForm()) {
      setLoading(false);
      return;
    }

    try {
      console.log('=== LOGIN ATTEMPT START ===');
      console.log('Email:', formData.email);
      console.log('Target Platform:', targetPlatform);
      
      const result = await login(formData.email, formData.password);
      
      console.log('=== LOGIN RESULT ANALYSIS ===');
      console.log('Raw result:', result);
      console.log('result.success:', result.success);
      console.log('result.success type:', typeof result.success);
      console.log('result.user exists:', !!result.user);
      console.log('result.error:', result.error);
      console.log('=== END ANALYSIS ===');

      // Force success check - be very explicit
      const isSuccessful = result && result.success === true && result.user;
      
      if (isSuccessful) {
        console.log('✅ LOGIN SUCCESS - Redirecting to:', targetPlatform);
        setDebugInfo(`Login successful! Redirecting to ${targetPlatform}...`);
        
        // Small delay to ensure state is properly set
        setTimeout(() => {
          navigate(targetPlatform, { replace: true });
        }, 500);
        
      } else {
        console.log('❌ LOGIN FAILED - Processing error');
        handleLoginError(result);
      }

    } catch (error) {
      console.error('LOGIN EXCEPTION:', error);
      setNetworkError(true);
      setError('An unexpected error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoginError = (result) => {
    const errorMessage = result?.error || result?.message || 'Login failed';
    
    if (errorMessage.includes('Network error') || errorMessage.includes('fetch')) {
      setNetworkError(true);
      setError('Cannot connect to server. Please check your internet connection.');
    } else if (errorMessage.includes('401') || errorMessage.includes('Invalid credentials') || errorMessage.includes('invalid')) {
      setError('Invalid email or password. Please try again.');
    } else if (errorMessage.includes('404')) {
      setError('Account not found. Please register first or check your email.');
    } else if (errorMessage.includes('500')) {
      setError('Server error. Please try again later.');
    } else if (errorMessage.includes('timeout')) {
      setError('Request timed out. Please try again.');
    } else {
      setError(errorMessage);
    }
  };

  const testConnection = async () => {
    try {
      setDebugInfo('Testing connection...');
      const API_BASE = 'https://agentic-u5lx.onrender.com';
      
      const response = await fetch(`${API_BASE}/api/test-route`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDebugInfo(`✅ Backend connection successful: ${data.message}`);
      } else {
        setDebugInfo(`❌ Backend responded with status: ${response.status}`);
      }
    } catch (error) {
      console.error('Connection test failed:', error);
      setDebugInfo(`❌ Connection failed: ${error.message}`);
    }
  };

  const quickLogin = async (email, password) => {
    setFormData({ email, password });
    // Trigger form submission
    setTimeout(() => {
      document.getElementById('login-form').requestSubmit();
    }, 100);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div style={{
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderRadius: '20px',
        padding: '40px',
        width: '100%',
        maxWidth: '450px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{
            width: '60px',
            height: '60px',
            background: 'linear-gradient(135deg, #667eea, #764ba2)',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px',
            fontSize: '24px'
          }}>
            🚀
          </div>
          <h1 style={{
            fontSize: '28px',
            fontWeight: '700',
            color: '#333',
            marginBottom: '8px'
          }}>
            Welcome Back
          </h1>
          <p style={{
            fontSize: '16px',
            color: '#666',
            margin: 0
          }}>
            Sign in to access {targetPlatform.replace('/', '').toUpperCase()} automation
          </p>
        </div>

        {/* Network Error Banner */}
        {networkError && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '16px',
            color: '#dc2626',
            fontSize: '14px'
          }}>
            🔴 Network connection issue detected.{' '}
            <button 
              onClick={testConnection}
              style={{
                background: 'none',
                border: 'none',
                color: '#dc2626',
                textDecoration: 'underline',
                cursor: 'pointer',
                fontSize: '14px'
              }}
            >
              Test Connection
            </button>
          </div>
        )}

        {/* Debug Info */}
        {debugInfo && (
          <div style={{
            background: 'rgba(59, 130, 246, 0.1)',
            border: '1px solid rgba(59, 130, 246, 0.3)',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '16px',
            color: '#1d4ed8',
            fontSize: '14px'
          }}>
            {debugInfo}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div style={{
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.3)',
            borderRadius: '8px',
            padding: '12px 16px',
            marginBottom: '24px',
            color: '#dc2626',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Quick Test Accounts */}
        <div style={{
          background: 'rgba(34, 197, 94, 0.1)',
          border: '1px solid rgba(34, 197, 94, 0.3)',
          borderRadius: '8px',
          padding: '16px',
          marginBottom: '24px'
        }}>
          <div style={{ fontSize: '14px', fontWeight: '600', color: '#059669', marginBottom: '12px' }}>
            Quick Test Login:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            <button
              onClick={() => quickLogin('aryan@gmail.com', 'test123')}
              disabled={loading}
              style={{
                padding: '6px 12px',
                background: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              aryan@gmail.com
            </button>
            <button
              onClick={() => quickLogin('aryanpatel7746@gmail.com', 'test123')}
              disabled={loading}
              style={{
                padding: '6px 12px',
                background: '#059669',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '12px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            >
              aryanpatel7746@gmail.com
            </button>
          </div>
        </div>

        {/* Login Form */}
        <form id="login-form" onSubmit={handleSubmit}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '10px',
                fontSize: '16px',
                background: 'white',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '600',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              style={{
                width: '100%',
                padding: '12px 16px',
                border: '2px solid rgba(0, 0, 0, 0.1)',
                borderRadius: '10px',
                fontSize: '16px',
                background: 'white',
                boxSizing: 'border-box'
              }}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              padding: '14px',
              background: loading ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              border: 'none',
              borderRadius: '10px',
              fontSize: '16px',
              fontWeight: '600',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            {loading ? (
              <>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid transparent',
                  borderTop: '2px solid white',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                Signing In...
              </>
            ) : (
              `Sign In to ${targetPlatform.replace('/', '').toUpperCase()}`
            )}
          </button>
        </form>

        {/* Platform Navigation */}
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: 'rgba(99, 102, 241, 0.1)',
          borderRadius: '8px'
        }}>
          <div style={{ fontSize: '14px', fontWeight: '600', color: '#4338ca', marginBottom: '8px' }}>
            Available Platforms:
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {Object.entries(platformRoutes).filter(([key]) => key !== 'default').map(([platform, route]) => (
              <Link
                key={platform}
                to={route}
                style={{
                  padding: '4px 8px',
                  background: targetPlatform === route ? '#4338ca' : 'transparent',
                  color: targetPlatform === route ? 'white' : '#4338ca',
                  border: '1px solid #4338ca',
                  borderRadius: '4px',
                  textDecoration: 'none',
                  fontSize: '12px',
                  textTransform: 'capitalize'
                }}
              >
                {platform}
              </Link>
            ))}
          </div>
        </div>

        {/* Register Link */}
        <div style={{
          textAlign: 'center',
          marginTop: '24px',
          paddingTop: '24px',
          borderTop: '1px solid rgba(0, 0, 0, 0.1)'
        }}>
          <p style={{ fontSize: '14px', color: '#666', margin: 0 }}>
            Don't have an account?{' '}
            <Link
              to="/register"
              style={{
                color: '#667eea',
                textDecoration: 'none',
                fontWeight: '600'
              }}
            >
              Create Account
            </Link>
          </p>
        </div>

        {/* Back to Home */}
        <div style={{ textAlign: 'center', marginTop: '16px' }}>
          <Link
            to="/"
            style={{
              color: '#666',
              textDecoration: 'none',
              fontSize: '14px'
            }}
          >
            ← Back to Home
          </Link>
        </div>
      </div>

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default Login;