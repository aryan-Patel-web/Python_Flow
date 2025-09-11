import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RedditAUTO from './pages/RedditAUTO';
import './App.css';

// Import your other page components here
// import HomePage from './pages/HomePage';
// import OtherPage from './pages/OtherPage';

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
            {/* Add other navigation links here */}
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/reddit-auto" element={<RedditAUTO />} />
            {/* Add other routes here */}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

// Simple HomePage component (replace with your actual component)
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
        {/* Add more feature cards as needed */}
      </div>
    </div>
  );
};

export default App;