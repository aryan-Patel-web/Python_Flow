import React, { useState, useEffect } from 'react';
import { useAuth } from '../../hooks/useAuth';
import StatsOverview from '../../components/dashboard/StatsOverview';
import RecentPosts from '../../components/dashboard/RecentPosts';
import PlatformStatus from '../../components/dashboard/PlatformStatus';
import QuickActions from '../../components/dashboard/QuickActions';
import api from '../../services/api';
import LoadingSpinner from '../../components/common/LoadingSpinner';

const Dashboard = () => {
  const { user } = useAuth();
  const [automationStatus, setAutomationStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAutomationStatus();
  }, []);

  const fetchAutomationStatus = async () => {
    try {
      const response = await api.get('/automation/status');
      setAutomationStatus(response.data);
    } catch (error) {
      console.error('Failed to fetch automation status:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome back, {user?.name}!
        </h1>
        <p className="text-gray-600">
          Your AI social media automation is {automationStatus?.automation_active ? 'active' : 'paused'}
        </p>
      </div>

      {/* Stats Overview */}
      <StatsOverview automationStatus={automationStatus} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <RecentPosts />
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <PlatformStatus />
          <QuickActions />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
