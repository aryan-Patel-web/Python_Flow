import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AuthProvider, useAuth } from './quickpage/AuthContext';
import ProtectedRoute from './quickpage/ProtectedRoute';
import Login from './quickpage/Login';
import Register from './quickpage/Register';
import RedditAUTO from './pages/RedditAUTO';
import './App.css';

// Error Boundary Component
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

// Navigation Component
const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to="/" className="brand-link">
          Reddit Automation Platform
        </Link>
      </div>
      <div className="nav-links">
        <Link to="/" className="nav-link">Home</Link>
        {isAuthenticated ? (
          <>
            <Link to="/reddit-auto" className="nav-link">Dashboard</Link>
            <div className="user-menu">
              <span className="user-name">Welcome, {user?.name}</span>
              <button onClick={logout} className="logout-btn">
                Logout
              </button>
            </div>
          </>
        ) : (
          <>
            <Link to="/login" className="nav-link">Login</Link>
            <Link to="/register" className="nav-link register-btn">
              Get Started
            </Link>
          </>
        )}
      </div>
    </nav>
  );
};

// HomePage component with OAuth redirect handling
const HomePage = () => {
  const { isAuthenticated } = useAuth();

  useEffect(() => {
    // Handle Reddit OAuth redirect for authenticated users
    const urlParams = new URLSearchParams(window.location.search);
    const redditConnected = urlParams.get('reddit_connected');
    const error = urlParams.get('error');
    
    if (isAuthenticated && (redditConnected === 'true' || error)) {
      // Redirect authenticated users to dashboard with OAuth parameters
      const currentParams = window.location.search;
      console.log('OAuth redirect detected for authenticated user, redirecting to dashboard');
      window.location.href = `/reddit-auto${currentParams}`;
      return;
    }
  }, [isAuthenticated]);

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Automate Your Reddit Presence</h1>
        <p className="hero-subtitle">
          AI-powered content generation and scheduling for Reddit automation
        </p>
        <div className="hero-buttons">
          {isAuthenticated ? (
            <Link to="/reddit-auto" className="cta-button primary">
              Go to Dashboard
            </Link>
          ) : (
            <>
              <Link to="/register" className="cta-button primary">
                Start Free Trial
              </Link>
              <Link to="/login" className="cta-button secondary">
                Sign In
              </Link>
            </>
          )}
        </div>
      </div>
      
      <div className="feature-cards">
        <div className="feature-card">
          <div className="feature-icon">🤖</div>
          <h2>Reddit Automation</h2>
          <p>
            Automate your Reddit posting and replies with AI-powered content generation. 
            Schedule posts, generate engaging content, and grow your presence effortlessly.
          </p>
          <div className="feature-stats">
            <div className="stat">
              <strong>Real AI</strong>
              <span>Mistral & Groq</span>
            </div>
            <div className="stat">
              <strong>Auto Schedule</strong>
              <span>24/7 Posting</span>
            </div>
            <div className="stat">
              <strong>Safe Subreddits</strong>
              <span>High Success Rate</span>
            </div>
          </div>
          {isAuthenticated ? (
            <Link to="/reddit-auto" className="feature-link">
              Go to Dashboard →
            </Link>
          ) : (
            <Link to="/register" className="feature-link">
              Get Started →
            </Link>
          )}
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h2>Analytics & Insights</h2>
          <p>
            Track your posting performance, engagement rates, and audience growth 
            with detailed analytics and insights.
          </p>
          <Link to="/register" className="feature-link secondary">
            Coming Soon
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">🎯</div>
          <h2>Smart Targeting</h2>
          <p>
            AI-powered audience targeting and optimal posting times to maximize 
            your reach and engagement across different communities.
          </p>
          <Link to="/register" className="feature-link secondary">
            Coming Soon
          </Link>
        </div>
      </div>

      <div className="quick-start">
        <h3>How It Works</h3>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Create Account</h4>
              <p>Sign up with your email and secure your account</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Connect Reddit</h4>
              <p>One-time Reddit connection using OAuth</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Start Automating</h4>
              <p>Configure your profile and let AI generate content</p>
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
          <div className="App">
            <Navbar />
            <main className="main-content">
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
              </Routes>
            </main>
          </div>
        </Router>
      </AuthProvider>
    </ErrorBoundary>
  );
}

export default App;