import React, { useState } from 'react';
import { 
  Calendar, 
  Zap, 
  TrendingUp, 
  Users, 
  Plus,
  Settings,
  Play,
  Pause,
  BarChart3,
  FileText
} from 'lucide-react';

const QuickActions = ({ onActionClick }) => {
  const [automationStatus, setAutomationStatus] = useState('inactive');
  const [loading, setLoading] = useState(false);

  const toggleAutomation = async () => {
    try {
      setLoading(true);
      const newStatus = automationStatus === 'active' ? 'inactive' : 'active';
      
      const response = await fetch('/api/automation/toggle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ status: newStatus })
      });
      
      if (response.ok) {
        setAutomationStatus(newStatus);
        onActionClick?.('automation_toggled', { status: newStatus });
      }
    } catch (error) {
      console.error('Error toggling automation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleQuickAction = (action, data = {}) => {
    onActionClick?.(action, data);
  };

  const quickActions = [
    {
      id: 'schedule_post',
      title: 'Schedule Post',
      description: 'Create and schedule new content',
      icon: Calendar,
      color: 'blue',
      action: () => handleQuickAction('schedule_post')
    },
    {
      id: 'generate_content',
      title: 'Generate Content',
      description: 'AI-powered content creation',
      icon: Zap,
      color: 'green',
      action: () => handleQuickAction('generate_content')
    },
    {
      id: 'view_analytics',
      title: 'View Analytics',
      description: 'Check performance metrics',
      icon: TrendingUp,
      color: 'purple',
      action: () => handleQuickAction('view_analytics')
    },
    {
      id: 'manage_accounts',
      title: 'Manage Accounts',
      description: 'Connect social platforms',
      icon: Users,
      color: 'orange',
      action: () => handleQuickAction('manage_accounts')
    }
  ];

  const automationActions = [
    {
      id: 'toggle_automation',
      title: automationStatus === 'active' ? 'Pause Automation' : 'Start Automation',
      description: automationStatus === 'active' ? 'Stop automated posting' : 'Begin automated posting',
      icon: automationStatus === 'active' ? Pause : Play,
      color: automationStatus === 'active' ? 'red' : 'green',
      action: toggleAutomation,
      loading: loading
    },
    {
      id: 'automation_settings',
      title: 'Automation Settings',
      description: 'Configure posting schedule',
      icon: Settings,
      color: 'gray',
      action: () => handleQuickAction('automation_settings')
    }
  ];

  const contentActions = [
    {
      id: 'content_library',
      title: 'Content Library',
      description: 'Browse saved content',
      icon: FileText,
      color: 'indigo',
      action: () => handleQuickAction('content_library')
    },
    {
      id: 'create_template',
      title: 'Create Template',
      description: 'Save reusable content',
      icon: Plus,
      color: 'teal',
      action: () => handleQuickAction('create_template')
    }
  ];

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200',
      green: 'bg-green-50 text-green-700 hover:bg-green-100 border-green-200',
      purple: 'bg-purple-50 text-purple-700 hover:bg-purple-100 border-purple-200',
      orange: 'bg-orange-50 text-orange-700 hover:bg-orange-100 border-orange-200',
      red: 'bg-red-50 text-red-700 hover:bg-red-100 border-red-200',
      gray: 'bg-gray-50 text-gray-700 hover:bg-gray-100 border-gray-200',
      indigo: 'bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border-indigo-200',
      teal: 'bg-teal-50 text-teal-700 hover:bg-teal-100 border-teal-200'
    };
    return colors[color] || colors.gray;
  };

  const ActionButton = ({ action, size = 'normal' }) => {
    const Icon = action.icon;
    const isCompact = size === 'compact';
    
    return (
      <button
        onClick={action.action}
        disabled={action.loading}
        className={`
          ${isCompact ? 'p-3' : 'p-4'} 
          border rounded-lg transition-all duration-200 
          ${getColorClasses(action.color)}
          ${action.loading ? 'opacity-50 cursor-not-allowed' : 'hover:shadow-md'}
          group
        `}
      >
        <div className={`flex ${isCompact ? 'flex-col items-center space-y-1' : 'items-start space-y-2'}`}>
          <div className={`flex items-center ${isCompact ? 'justify-center' : 'justify-between w-full'}`}>
            <Icon className={`${isCompact ? 'w-5 h-5' : 'w-6 h-6'} ${action.loading ? 'animate-spin' : ''}`} />
            {!isCompact && (
              <div className="w-2 h-2 rounded-full bg-current opacity-0 group-hover:opacity-100 transition-opacity" />
            )}
          </div>
          <div className={`${isCompact ? 'text-center' : 'text-left'}`}>
            <h4 className={`${isCompact ? 'text-xs' : 'text-sm'} font-medium`}>
              {action.title}
            </h4>
            {!isCompact && (
              <p className="text-xs opacity-75 mt-1">
                {action.description}
              </p>
            )}
          </div>
        </div>
      </button>
    );
  };

  return (
    <div className="space-y-6">
      {/* Main Quick Actions */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action) => (
            <ActionButton key={action.id} action={action} />
          ))}
        </div>
      </div>

      {/* Automation Controls */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Automation</h3>
          <div className={`px-2 py-1 rounded-full text-xs font-medium ${
            automationStatus === 'active' 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {automationStatus === 'active' ? 'Running' : 'Stopped'}
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {automationActions.map((action) => (
            <ActionButton key={action.id} action={action} />
          ))}
        </div>
      </div>

      {/* Content Management */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Content</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {contentActions.map((action) => (
            <ActionButton key={action.id} action={action} />
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Today's Activity</h4>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">12</div>
            <div className="text-xs text-gray-500">Posts Scheduled</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">3.2K</div>
            <div className="text-xs text-gray-500">Total Engagement</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">5</div>
            <div className="text-xs text-gray-500">Platforms Active</div>
          </div>
        </div>
      </div>

      {/* Quick Tips */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
        <h4 className="text-sm font-medium text-blue-900 mb-2">💡 Quick Tip</h4>
        <p className="text-sm text-blue-800">
          Schedule your posts during peak engagement hours (7-9 PM) for better reach and interaction.
        </p>
      </div>
    </div>
  );
};

export default QuickActions;