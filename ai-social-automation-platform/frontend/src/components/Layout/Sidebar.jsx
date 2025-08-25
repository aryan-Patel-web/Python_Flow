import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  LayoutDashboard, Shield, Target, FileText, BarChart3, 
  Zap, CreditCard, Settings, Bot, Calendar, Sparkles,
  PlayCircle, Clock, Wand2
} from 'lucide-react';
import { clsx } from 'clsx';
import { useAuth } from '../../context/AuthContext';

const Sidebar = () => {
  const location = useLocation();
  const { user } = useAuth();

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      current: location.pathname === '/dashboard'
    },
    {
      name: 'Secure Platforms',
      href: '/platforms', 
      icon: Shield,
      current: location.pathname === '/platforms',
      badge: 'OAuth 2.0',
      description: 'Connect social accounts securely'
    },
    // 🔥 NEW: Auto-Posting Section
    {
      section: 'AI Auto-Posting',
      items: [
        {
          name: 'Auto-Posting Center',
          href: '/auto-posting',
          icon: PlayCircle,
          current: location.pathname === '/auto-posting',
          badge: 'NEW',
          description: 'Start/stop automation'
        },
        {
          name: 'Content Generator',
          href: '/content-generator',
          icon: Wand2,
          current: location.pathname === '/content-generator',
          description: 'Generate AI content'
        },
        {
          name: 'Posting Scheduler',
          href: '/posting-scheduler',
          icon: Clock,
          current: location.pathname === '/posting-scheduler',
          description: 'Configure posting times'
        }
      ]
    },
    // Original sections
    {
      section: 'Content Management',
      items: [
        {
          name: 'Domains',
          href: '/domains',
          icon: Target,
          current: location.pathname === '/domains',
          description: 'Content categories'
        },
        {
          name: 'Content Library',
          href: '/content',
          icon: FileText,
          current: location.pathname === '/content',
          description: 'Manage your posts'
        }
      ]
    },
    {
      section: 'Analytics & Growth',
      items: [
        {
          name: 'Analytics',
          href: '/analytics',
          icon: BarChart3,
          current: location.pathname === '/analytics',
          description: 'Performance metrics'
        },
        {
          name: 'Legacy Automation',
          href: '/automation',
          icon: Zap,
          current: location.pathname === '/automation',
          description: 'Old automation settings'
        }
      ]
    },
    {
      section: 'Account',
      items: [
        {
          name: 'Billing',
          href: '/billing',
          icon: CreditCard,
          current: location.pathname === '/billing',
          description: 'Plans & payments'
        },
        {
          name: 'Settings',
          href: '/settings',
          icon: Settings,
          current: location.pathname === '/settings',
          description: 'Account settings'
        }
      ]
    }
  ];

  const renderNavigationItem = (item) => {
    return (
      <Link
        key={item.name}
        to={item.href}
        className={clsx(
          'group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors',
          item.current
            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
            : 'text-gray-700 hover:text-gray-900 hover:bg-gray-50'
        )}
      >
        <item.icon
          className={clsx(
            'mr-3 h-5 w-5 flex-shrink-0',
            item.current ? 'text-blue-500' : 'text-gray-400 group-hover:text-gray-500'
          )}
        />
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <span className="truncate">{item.name}</span>
            {item.badge && (
              <span className={clsx(
                'ml-2 inline-block px-2 py-1 text-xs font-medium rounded-full',
                item.badge === 'NEW' ? 'bg-green-100 text-green-800' :
                item.badge === 'OAuth 2.0' ? 'bg-blue-100 text-blue-800' :
                'bg-gray-100 text-gray-800'
              )}>
                {item.badge}
              </span>
            )}
          </div>
          {item.description && (
            <p className="text-xs text-gray-500 truncate mt-0.5">
              {item.description}
            </p>
          )}
        </div>
      </Link>
    );
  };

  return (
    <div className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-64 lg:flex-col">
      <div className="flex min-h-0 flex-1 flex-col bg-white border-r border-gray-200">
        {/* Logo */}
        <div className="flex h-16 flex-shrink-0 items-center px-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-900">VelocityPost</h1>
              <p className="text-xs text-gray-500">AI Auto-Posting</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex flex-1 flex-col overflow-y-auto py-4">
          <nav className="flex-1 space-y-1 px-3">
            {navigationItems.map((item) => {
              if (item.section) {
                return (
                  <div key={item.section} className="pt-4 first:pt-0">
                    <div className="flex items-center space-x-2 px-3 pb-2">
                      <Sparkles className="w-4 h-4 text-purple-500" />
                      <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider">
                        {item.section}
                      </h3>
                    </div>
                    <div className="space-y-1">
                      {item.items.map(renderNavigationItem)}
                    </div>
                  </div>
                );
              }
              return renderNavigationItem(item);
            })}
          </nav>

          {/* User Profile */}
          <div className="flex flex-shrink-0 border-t border-gray-200 p-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">
                  {user?.name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-gray-700 truncate">
                  {user?.name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">
                  {user?.email || 'user@example.com'}
                </p>
              </div>
            </div>
          </div>

          {/* AI Status Indicator */}
          <div className="mx-4 mb-4 p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white">
            <div className="flex items-center space-x-2 mb-2">
              <Bot className="w-4 h-4" />
              <span className="text-sm font-medium">AI Status</span>
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span>Posts Generated</span>
                <span className="font-semibold">247</span>
              </div>
              <div className="flex justify-between">
                <span>Automation</span>
                <span className="font-semibold text-green-200">Active</span>
              </div>
              <div className="flex justify-between">
                <span>Next Post</span>
                <span className="font-semibold">12 min</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;