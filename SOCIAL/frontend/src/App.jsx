import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RedditAUTO from './pages/RedditAUTO';
import './App.css';

function App() {
  return (
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
  );
}

// Simple HomePage component - keep this in the same file
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