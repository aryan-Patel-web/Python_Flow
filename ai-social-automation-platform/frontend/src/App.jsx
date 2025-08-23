import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import PublicRoute from './components/auth/PublicRoute';
import Layout from './components/Layout/Layout';

// Landing Page
import LandingPage from './pages/LandingPage';

// Auth Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';

// 🔥 NEW: OAuth Callback Handler for Auto-Posting Authentication
import OAuthCallback from './components/auth/OAuthCallback';

// Main App Pages
import Dashboard from './pages/dashboard/Dashboard';
import CredentialsPage from './pages/credentials/CredentialsPage';
import DomainsPage from './pages/domains/DomainsPage';
import ContentLibrary from './pages/content/ContentLibrary';
import AnalyticsPage from './pages/analytics/AnalyticsPage';
import AutomationPage from './pages/automation/AutomationPage';
import BillingPage from './pages/billing/BillingPage';
import SettingsPage from './pages/settings/SettingsPage';

// 🔥 NEW: Secure Platforms Page for OAuth Auto-Posting (Replaces insecure credential forms)
import Platforms from './pages/platforms/Platforms';

// 🔥 NEW: Auto-Posting Management Pages
import AutoPostingCenter from './pages/autoposting/AutoPostingCenter';
import PostingScheduler from './pages/autoposting/PostingScheduler';
import ContentGenerator from './pages/autoposting/ContentGenerator';

// Error Pages
import NotFound from './pages/error/NotFound';

function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          {/* 🔥 NEW: Landing Page - Public Route */}
          <Route path="/" element={
            <PublicRoute>
              <LandingPage />
            </PublicRoute>
          } />

          {/* Public Routes (redirect to dashboard if authenticated) */}
          <Route path="/login" element={
            <PublicRoute>
              <Login />
            </PublicRoute>
          } />
          <Route path="/register" element={
            <PublicRoute>
              <Register />
            </PublicRoute>
          } />
          <Route path="/forgot-password" element={
            <PublicRoute>
              <ForgotPassword />
            </PublicRoute>
          } />

          {/* 🔥 NEW: OAuth Callback Routes - Secure Social Media Authentication for Auto-Posting */}
          <Route path="/auth/callback/facebook" element={<OAuthCallback platform="facebook" />} />
          <Route path="/auth/callback/instagram" element={<OAuthCallback platform="instagram" />} />
          <Route path="/auth/callback/twitter" element={<OAuthCallback platform="twitter" />} />
          <Route path="/auth/callback/linkedin" element={<OAuthCallback platform="linkedin" />} />
          <Route path="/auth/callback/youtube" element={<OAuthCallback platform="youtube" />} />
          <Route path="/auth/callback/tiktok" element={<OAuthCallback platform="tiktok" />} />
          <Route path="/auth/callback/pinterest" element={<OAuthCallback platform="pinterest" />} />

          {/* Protected Routes (require authentication) */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Layout>
                <Dashboard />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/credentials" element={
            <ProtectedRoute>
              <Layout>
                <CredentialsPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/domains" element={
            <ProtectedRoute>
              <Layout>
                <DomainsPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/content" element={
            <ProtectedRoute>
              <Layout>
                <ContentLibrary />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/analytics" element={
            <ProtectedRoute>
              <Layout>
                <AnalyticsPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/automation" element={
            <ProtectedRoute>
              <Layout>
                <AutomationPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/billing" element={
            <ProtectedRoute>
              <Layout>
                <BillingPage />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/settings" element={
            <ProtectedRoute>
              <Layout>
                <SettingsPage />
              </Layout>
            </ProtectedRoute>
          } />

          {/* 🔥 NEW: Secure Platforms Page - OAuth Only Authentication for Auto-Posting */}
          <Route path="/platforms" element={
            <ProtectedRoute>
              <Layout>
                <Platforms />
              </Layout>
            </ProtectedRoute>
          } />

          {/* 🔥 NEW: Auto-Posting Management Routes */}
          <Route path="/auto-posting" element={
            <ProtectedRoute>
              <Layout>
                <AutoPostingCenter />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/posting-scheduler" element={
            <ProtectedRoute>
              <Layout>
                <PostingScheduler />
              </Layout>
            </ProtectedRoute>
          } />
          
          <Route path="/content-generator" element={
            <ProtectedRoute>
              <Layout>
                <ContentGenerator />
              </Layout>
            </ProtectedRoute>
          } />

          {/* 404 Page */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}

export default App;