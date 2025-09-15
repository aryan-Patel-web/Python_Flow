import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RedditAUTO from './pages/RedditAUTO'; // Your existing Reddit automation component
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

// Simple HomePage component
const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Welcome to Social Media Platform</h1>
      <div className="feature-cards">
        <div className="feature-card">
          <h2>Reddit Automation</h2>
          <p>Automate your Reddit posting and replies with AI-powered content generation.</p>
          <Link to="/reddit-auto" className="feature-link">
            Get Started →
          </Link>
        </div>
      </div>
    </div>
  );
};

export default App;