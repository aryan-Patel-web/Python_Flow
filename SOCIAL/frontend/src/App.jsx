import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
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

function App() {
  return (
    <ErrorBoundary>
      <Router>
        <div className="App">
          <nav className="navbar">
            <div className="nav-brand">
              <Link to="/" className="brand-link">
                Social Media Platform
              </Link>
            </div>
            <div className="nav-links">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/reddit-auto" className="nav-link">Reddit Automation</Link>
            </div>
          </nav>

          <main className="main-content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/reddit-auto" element={<RedditAUTO />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ErrorBoundary>
  );
}

// HomePage component with OAuth redirect handling
const HomePage = () => {
  useEffect(() => {
    // Check if this is an OAuth redirect from Reddit
    const urlParams = new URLSearchParams(window.location.search);
    const redditConnected = urlParams.get('reddit_connected');
    const error = urlParams.get('error');
    
    if (redditConnected === 'true' || error) {
      // Redirect to reddit-auto page with all parameters preserved
      const currentParams = window.location.search;
      console.log('OAuth redirect detected, redirecting to /reddit-auto', currentParams);
      window.location.href = `/reddit-auto${currentParams}`;
      return;
    }
  }, []);

  return (
    <div className="home-page">
      <div className="hero-section">
        <h1>Welcome to Social Media Platform</h1>
        <p className="hero-subtitle">
          Automate your social media presence with AI-powered content generation
        </p>
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
          <Link to="/reddit-auto" className="feature-link">
            Get Started →
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h2>Analytics & Insights</h2>
          <p>
            Track your posting performance, engagement rates, and audience growth 
            with detailed analytics and insights.
          </p>
          <Link to="/reddit-auto" className="feature-link secondary">
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
          <Link to="/reddit-auto" className="feature-link secondary">
            Coming Soon
          </Link>
        </div>
      </div>

      <div className="quick-start">
        <h3>Quick Start Guide</h3>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-content">
              <h4>Connect Reddit</h4>
              <p>Securely connect your Reddit account using OAuth</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-content">
              <h4>Configure Profile</h4>
              <p>Set up your business domain and content preferences</p>
            </div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-content">
              <h4>Start Automating</h4>
              <p>Schedule posts and let AI generate engaging content</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;