import React, { useState, useEffect } from 'react';
import { 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Clock, 
  Globe, 
  Key, 
  Database,
  Download,
  Trash2,
  Save,
  RefreshCw,
  Moon,
  Sun,
  Monitor,
  Mail,
  Smartphone,
  Eye,
  EyeOff
} from 'lucide-react';
import { useToast } from '../../components/common/Toast';
import Button from '../../components/common/Button';
import Input from '../../components/common/Input';

const SettingsPage = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [settings, setSettings] = useState({
    profile: {
      full_name: '',
      email: '',
      username: '',
      bio: '',
      timezone: 'America/New_York',
      language: 'en'
    },
    notifications: {
      email_notifications: true,
      push_notifications: true,
      post_success: true,
      post_failure: true,
      weekly_reports: true,
      marketing_emails: false
    },
    privacy: {
      profile_visibility: 'private',
      analytics_sharing: false,
      data_retention: '12_months'
    },
    appearance: {
      theme: 'system',
      sidebar_collapsed: false,
      density: 'comfortable'
    },
    automation: {
      auto_scheduling: true,
      optimal_timing: true,
      auto_hashtags: true,
      content_approval: 'manual'
    }
  });
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const { toast } = useToast();

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/user/settings', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSettings(prev => ({
          ...prev,
          ...data.settings
        }));
      }
    } catch (error) {
      console.error('Error fetching settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = async (section, newSettings) => {
    try {
      const response = await fetch('/api/user/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          section,
          settings: newSettings
        })
      });

      if (response.ok) {
        setSettings(prev => ({
          ...prev,
          [section]: newSettings
        }));
        toast.success('Settings updated successfully!');
      } else {
        throw new Error('Failed to update settings');
      }
    } catch (error) {
      toast.error('Failed to update settings');
    }
  };

  const changePassword = async () => {
    if (passwordForm.new_password !== passwordForm.confirm_password) {
      toast.error('New passwords do not match');
      return;
    }

    if (passwordForm.new_password.length < 8) {
      toast.error('Password must be at least 8 characters long');
      return;
    }

    try {
      const response = await fetch('/api/user/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(passwordForm)
      });

      if (response.ok) {
        toast.success('Password changed successfully!');
        setPasswordForm({
          current_password: '',
          new_password: '',
          confirm_password: ''
        });
      } else {
        const data = await response.json();
        toast.error(data.error || 'Failed to change password');
      }
    } catch (error) {
      toast.error('Failed to change password');
    }
  };

  const exportData = async () => {
    try {
      const response = await fetch('/api/user/export-data', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'my-data-export.json';
        a.click();
        window.URL.revokeObjectURL(url);
        toast.success('Data exported successfully!');
      }
    } catch (error) {
      toast.error('Failed to export data');
    }
  };

  const deleteAccount = async () => {
    const confirmed = window.confirm(
      'Are you sure you want to delete your account? This action cannot be undone.'
    );
    
    if (!confirmed) return;

    const doubleConfirm = window.prompt(
      'Type "DELETE" to confirm account deletion:'
    );

    if (doubleConfirm !== 'DELETE') {
      toast.error('Account deletion cancelled');
      return;
    }

    try {
      const response = await fetch('/api/user/delete-account', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        toast.success('Account deleted successfully');
        localStorage.removeItem('token');
        window.location.href = '/';
      }
    } catch (error) {
      toast.error('Failed to delete account');
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy & Security', icon: Shield },
    { id: 'appearance', label: 'Appearance', icon: Palette },
    { id: 'automation', label: 'Automation', icon: Clock },
    { id: 'data', label: 'Data & Export', icon: Database }
  ];

  const renderProfileSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Full Name"
            value={settings.profile.full_name}
            onChange={(e) => setSettings(prev => ({
              ...prev,
              profile: { ...prev.profile, full_name: e.target.value }
            }))}
            placeholder="Enter your full name"
          />
          <Input
            label="Email"
            type="email"
            value={settings.profile.email}
            onChange={(e) => setSettings(prev => ({
              ...prev,
              profile: { ...prev.profile, email: e.target.value }
            }))}
            placeholder="Enter your email"
          />
          <Input
            label="Username"
            value={settings.profile.username}
            onChange={(e) => setSettings(prev => ({
              ...prev,
              profile: { ...prev.profile, username: e.target.value }
            }))}
            placeholder="Enter your username"
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Timezone</label>
            <select
              value={settings.profile.timezone}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                profile: { ...prev.profile, timezone: e.target.value }
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="America/New_York">Eastern Time (UTC-5)</option>
              <option value="America/Chicago">Central Time (UTC-6)</option>
              <option value="America/Denver">Mountain Time (UTC-7)</option>
              <option value="America/Los_Angeles">Pacific Time (UTC-8)</option>
              <option value="Europe/London">London (UTC+0)</option>
              <option value="Europe/Paris">Paris (UTC+1)</option>
              <option value="Asia/Tokyo">Tokyo (UTC+9)</option>
            </select>
          </div>
        </div>
        <div className="mt-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
          <textarea
            value={settings.profile.bio}
            onChange={(e) => setSettings(prev => ({
              ...prev,
              profile: { ...prev.profile, bio: e.target.value }
            }))}
            placeholder="Tell us about yourself..."
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div className="mt-4">
          <Button
            onClick={() => updateSettings('profile', settings.profile)}
            leftIcon={<Save />}
          >
            Save Profile
          </Button>
        </div>
      </div>

      {/* Password Change */}
      <div className="border-t pt-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
        <div className="space-y-4 max-w-md">
          <div className="relative">
            <Input
              label="Current Password"
              type={showCurrentPassword ? 'text' : 'password'}
              value={passwordForm.current_password}
              onChange={(e) => setPasswordForm(prev => ({
                ...prev,
                current_password: e.target.value
              }))}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                  className="pr-3 flex items-center"
                >
                  {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
            />
          </div>
          <div className="relative">
            <Input
              label="New Password"
              type={showNewPassword ? 'text' : 'password'}
              value={passwordForm.new_password}
              onChange={(e) => setPasswordForm(prev => ({
                ...prev,
                new_password: e.target.value
              }))}
              rightElement={
                <button
                  type="button"
                  onClick={() => setShowNewPassword(!showNewPassword)}
                  className="pr-3 flex items-center"
                >
                  {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              }
            />
          </div>
          <Input
            label="Confirm New Password"
            type="password"
            value={passwordForm.confirm_password}
            onChange={(e) => setPasswordForm(prev => ({
              ...prev,
              confirm_password: e.target.value
            }))}
          />
          <Button
            onClick={changePassword}
            leftIcon={<Key />}
            disabled={!passwordForm.current_password || !passwordForm.new_password || !passwordForm.confirm_password}
          >
            Change Password
          </Button>
        </div>
      </div>
    </div>
  );

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
        <div className="space-y-4">
          {[
            { key: 'email_notifications', label: 'Email Notifications', description: 'Receive notifications via email', icon: Mail },
            { key: 'push_notifications', label: 'Push Notifications', description: 'Receive push notifications', icon: Smartphone },
            { key: 'post_success', label: 'Post Success', description: 'Notify when posts are published successfully', icon: Bell },
            { key: 'post_failure', label: 'Post Failures', description: 'Notify when posts fail to publish', icon: Bell },
            { key: 'weekly_reports', label: 'Weekly Reports', description: 'Receive weekly analytics reports', icon: Bell },
            { key: 'marketing_emails', label: 'Marketing Emails', description: 'Receive product updates and tips', icon: Mail }
          ].map((notification) => {
            const Icon = notification.icon;
            return (
              <div key={notification.key} className="flex items-center justify-between py-3 border-b border-gray-200">
                <div className="flex items-center space-x-3">
                  <Icon className="w-5 h-5 text-gray-400" />
                  <div>
                    <div className="font-medium text-gray-900">{notification.label}</div>
                    <div className="text-sm text-gray-500">{notification.description}</div>
                  </div>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.notifications[notification.key]}
                    onChange={(e) => setSettings(prev => ({
                      ...prev,
                      notifications: {
                        ...prev.notifications,
                        [notification.key]: e.target.checked
                      }
                    }))}
                    className="sr-only peer"
                  />
                  