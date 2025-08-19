import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import LoadingSpinner from './components/common/LoadingSpinner'

// Import pages
import Login from './pages/auth/Login'
import Register from './pages/auth/Register'
import Dashboard from './pages/dashboard/Dashboard'
import CredentialsPage from './pages/credentials/CredentialsPage'
import DomainsPage from './pages/domains/DomainsPage'
import ContentLibrary from './pages/content/ContentLibrary'
import AnalyticsPage from './pages/analytics/AnalyticsPage'
import BillingPage from './pages/billing/BillingPage'
import SettingsPage from './pages/settings/SettingsPage'

// Import layout components
import Header from './components/common/Header'
import Sidebar from './components/common/Sidebar'

function App() {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="*" element={<Navigate to="/login" replace />} />
        </Routes>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="flex">
        <Sidebar />
        <main className="flex-1 ml-64 p-8">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/credentials" element={<CredentialsPage />} />
            <Route path="/domains" element={<DomainsPage />} />
            <Route path="/content" element={<ContentLibrary />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/billing" element={<BillingPage />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
