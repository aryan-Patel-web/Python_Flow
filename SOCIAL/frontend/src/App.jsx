import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import RedditAUTO from './pages/RedditAUTO';
import SocialMediaAutomation from './pages/Fb';
import InstagramAutomation from './pages/INSTA';
import './App.css';

// Enhanced Error Boundary
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught:', error, errorInfo);
    this.setState({ error, errorInfo });
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', padding: '20px' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', maxWidth: '500px', textAlign: 'center', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#dc2626', marginBottom: '16px' }}>Application Error</h2>
            <p style={{ color: '#666', marginBottom: '20px' }}>Something went wrong with the social media automation platform.</p>
            <details style={{ textAlign: 'left', marginBottom: '20px', background: '#f8f9fa', padding: '12px', borderRadius: '8px', fontSize: '12px' }}>
              <summary style={{ cursor: 'pointer', fontWeight: '600' }}>Error Details</summary>
              <pre style={{ marginTop: '8px', fontSize: '11px', overflow: 'auto' }}>{this.state.error && this.state.error.toString()}</pre>
            </details>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })} style={{ padding: '12px 24px', background: '#667eea', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Try Again</button>
              <button onClick={() => window.location.reload()} style={{ padding: '12px 24px', background: '#6b7280', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Reload Page</button>
            </div>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

// Enhanced Navigation Component
const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav style={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', padding: '12px 0', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', position: 'sticky', top: 0, zIndex: 1000 }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0 20px' }}>
        <Link to="/" style={{ fontSize: '24px', fontWeight: '700', color: '#667eea', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span>🚀</span>
          Social Auto Platform
        </Link>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <Link to="/" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px' }}>Home</Link>
          
          {isAuthenticated ? (
            <>
              <Link to="/reddit-auto" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>🔴</span>Reddit
              </Link>
              <Link to="/facebook-instagram" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📘</span>Facebook
              </Link>
              <Link to="/instagram" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <span>📸</span>Instagram
              </Link>
              
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginLeft: '20px', padding: '8px 16px', background: 'rgba(102, 126, 234, 0.1)', borderRadius: '20px' }}>
                <span style={{ fontSize: '14px', color: '#667eea', fontWeight: '600' }}>Welcome, {user?.name}</span>
                <button onClick={logout} style={{ padding: '6px 12px', background: '#ef4444', color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', fontWeight: '600', cursor: 'pointer' }}>Logout</button>
              </div>
            </>
          ) : (
            <>
              <Link to="/login" style={{ color: '#374151', textDecoration: 'none', fontWeight: '500', fontSize: '16px' }}>Login</Link>
              <Link to="/register" style={{ padding: '10px 20px', background: 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600', fontSize: '14px' }}>Get Started</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

// Enhanced HomePage with Multi-Platform Features
const HomePage = () => {
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Handle OAuth redirects for all platforms
    const urlParams = new URLSearchParams(window.location.search);
    const platform = urlParams.get('platform');
    const connected = urlParams.get('connected');
    const error = urlParams.get('error');
    
    if (isAuthenticated && connected === 'true' && platform) {
      // Redirect to appropriate platform dashboard
      const routes = {
        'reddit': '/reddit-auto',
        'facebook': '/facebook-instagram',
        'instagram': '/instagram'
      };
      const targetRoute = routes[platform] || '/facebook-instagram';
      window.location.href = `${targetRoute}${window.location.search}`;
      return;
    }
    
    if (isAuthenticated && error) {
      console.error(`${platform || 'Platform'} connection error:`, error);
    }
  }, [isAuthenticated]);

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      {/* Hero Section */}
      <div style={{ padding: '80px 20px', textAlign: 'center', color: 'white' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '20px', textShadow: '0 2px 4px rgba(0, 0, 0, 0.2)' }}>
            Multi-Platform Social Media Automation
          </h1>
          <p style={{ fontSize: '20px', marginBottom: '40px', opacity: 0.9, lineHeight: 1.6 }}>
            AI-powered content generation and automation for Reddit, Facebook, and Instagram. 
            Grow your presence across all major platforms with intelligent scheduling and authentic content.
          </p>
          
          <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', flexWrap: 'wrap' }}>
            {isAuthenticated ? (
              <>
                <Link to="/facebook-instagram" style={{ padding: '16px 32px', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(10px)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontWeight: '600', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                  <span>📘</span>Facebook Dashboard
                </Link>
                <Link to="/instagram" style={{ padding: '16px 32px', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(10px)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontWeight: '600', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                  <span>📸</span>Instagram Dashboard
                </Link>
                <Link to="/reddit-auto" style={{ padding: '16px 32px', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(10px)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontWeight: '600', fontSize: '16px', display: 'flex', alignItems: 'center', gap: '8px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                  <span>🔴</span>Reddit Dashboard
                </Link>
              </>
            ) : (
              <>
                <Link to="/register" style={{ padding: '16px 32px', background: 'white', color: '#667eea', textDecoration: 'none', borderRadius: '12px', fontWeight: '700', fontSize: '16px', boxShadow: '0 4px 20px rgba(0, 0, 0, 0.2)' }}>
                  Start Free Trial
                </Link>
                <Link to="/login" style={{ padding: '16px 32px', background: 'rgba(255, 255, 255, 0.2)', backdropFilter: 'blur(10px)', color: 'white', textDecoration: 'none', borderRadius: '12px', fontWeight: '600', fontSize: '16px', border: '1px solid rgba(255, 255, 255, 0.3)' }}>
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Platform Features */}
      <div style={{ padding: '60px 20px', background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <h2 style={{ textAlign: 'center', fontSize: '36px', fontWeight: '700', color: 'white', marginBottom: '50px' }}>
            Automate All Your Social Platforms
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '30px' }}>
            {/* Facebook Card */}
            <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '30px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', border: '2px solid #4267B2' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <span style={{ fontSize: '32px' }}>📘</span>
                <h3 style={{ margin: 0, color: '#4267B2', fontSize: '24px', fontWeight: '700' }}>Facebook Automation</h3>
              </div>
              <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '20px' }}>
                Automate your Facebook page posts with AI-generated content. Connect multiple pages, 
                schedule posts, and grow your business presence with authentic, engaging content.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#4267B2' }}>AI Content</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Human-like posts</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#4267B2' }}>Multi-Page</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>All your pages</div>
                </div>
              </div>
              {isAuthenticated ? (
                <Link to="/facebook-instagram" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#4267B2', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Go to Facebook Dashboard →
                </Link>
              ) : (
                <Link to="/register" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#4267B2', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Get Started →
                </Link>
              )}
            </div>

            {/* Instagram Card */}
            <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '30px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', border: '2px solid #E4405F' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <span style={{ fontSize: '32px' }}>📸</span>
                <h3 style={{ margin: 0, color: '#E4405F', fontSize: '24px', fontWeight: '700' }}>Instagram Automation</h3>
              </div>
              <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '20px' }}>
                Create stunning Instagram posts with AI-generated images and captions. Perfect hashtags, 
                optimal timing, and engaging visual content that grows your followers.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#E4405F' }}>AI Images</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Auto-generated</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#E4405F' }}>Smart Tags</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Perfect hashtags</div>
                </div>
              </div>
              {isAuthenticated ? (
                <Link to="/instagram" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#E4405F', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Go to Instagram Dashboard →
                </Link>
              ) : (
                <Link to="/register" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#E4405F', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Get Started →
                </Link>
              )}
            </div>

            {/* Reddit Card */}
            <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '30px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', border: '2px solid #FF4500' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <span style={{ fontSize: '32px' }}>🔴</span>
                <h3 style={{ margin: 0, color: '#FF4500', fontSize: '24px', fontWeight: '700' }}>Reddit Automation</h3>
              </div>
              <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '20px' }}>
                Engage with Reddit communities through authentic, AI-generated posts and comments. 
                Build reputation, drive traffic, and grow your brand presence organically.
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '20px' }}>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#FF4500' }}>Auto Post</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Smart timing</div>
                </div>
                <div style={{ textAlign: 'center', padding: '12px', background: '#f8f9fa', borderRadius: '8px' }}>
                  <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#FF4500' }}>Auto Reply</div>
                  <div style={{ fontSize: '12px', color: '#666' }}>Engage users</div>
                </div>
              </div>
              {isAuthenticated ? (
                <Link to="/reddit-auto" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#FF4500', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Go to Reddit Dashboard →
                </Link>
              ) : (
                <Link to="/register" style={{ display: 'block', textAlign: 'center', padding: '12px 24px', background: '#FF4500', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
                  Get Started →
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div style={{ padding: '60px 20px' }}>
        <div style={{ maxWidth: '1000px', margin: '0 auto', textAlign: 'center' }}>
          <h2 style={{ fontSize: '36px', fontWeight: '700', color: 'white', marginBottom: '50px' }}>
            How Multi-Platform Automation Works
          </h2>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '40px' }}>
            <div style={{ color: 'white' }}>
              <div style={{ width: '60px', height: '60px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', fontSize: '24px', fontWeight: 'bold' }}>1</div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>Create Account</h3>
              <p style={{ opacity: 0.9, lineHeight: 1.6 }}>Sign up once and access all platform automations from a single dashboard.</p>
            </div>
            
            <div style={{ color: 'white' }}>
              <div style={{ width: '60px', height: '60px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', fontSize: '24px', fontWeight: 'bold' }}>2</div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>Connect Platforms</h3>
              <p style={{ opacity: 0.9, lineHeight: 1.6 }}>One-time OAuth connection to Reddit, Facebook, and Instagram accounts.</p>
            </div>
            
            <div style={{ color: 'white' }}>
              <div style={{ width: '60px', height: '60px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', fontSize: '24px', fontWeight: 'bold' }}>3</div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>Configure AI</h3>
              <p style={{ opacity: 0.9, lineHeight: 1.6 }}>Set your business type, target audience, and content style for each platform.</p>
            </div>
            
            <div style={{ color: 'white' }}>
              <div style={{ width: '60px', height: '60px', background: 'rgba(255, 255, 255, 0.2)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 20px', fontSize: '24px', fontWeight: 'bold' }}>4</div>
              <h3 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '12px' }}>Automate & Grow</h3>
              <p style={{ opacity: 0.9, lineHeight: 1.6 }}>AI generates and posts content 24/7 while you focus on your business.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <Router>
          <div className="App" style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <Navbar />
            <main>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route 
                  path="/reddit-auto" 
                  element={
                    <ProtectedRoute>
                      <RedditAUTO />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/facebook-instagram" 
                  element={
                    <ProtectedRoute>
                      <SocialMediaAutomation />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/instagram" 
                  element={
                    <ProtectedRoute>
                      <InstagramAutomation />
                    </ProtectedRoute>
                  } 
                />
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;