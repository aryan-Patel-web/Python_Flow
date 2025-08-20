// frontend/src/components/common/Sidebar.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Settings, 
  Users, 
  FileText, 
  BarChart3, 
  CreditCard,
  Globe,
  Zap,
  Target
} from 'lucide-react';
import { useAuth } from '../../hooks/useAuth'; // FIXED IMPORT

const Sidebar = () => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return null;
  }

  const navigationItems = [
    {
      name: 'Dashboard',
      href: '/dashboard',
      icon: LayoutDashboard,
      current: false,
    },
    {
      name: 'Credentials',
      href: '/credentials', 
      icon: Settings,
      current: false,
    },
    {
      name: 'Domains',
      href: '/domains',
      icon: Target,
      current: false,
    },
    {
      name: 'Content',
      href: '/content',
      icon: FileText,
      current: false,
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: BarChart3,
      current: false,
    },
    {
      name: 'Automation',
      href: '/automation',
      icon: Zap,
      current: false,
    },
    {
      name: 'Billing',
      href: '/billing',
      icon: CreditCard,
      current: false,
    },
  ];

  return (
    <div className="flex flex-col w-64 bg-white border-r border-gray-200">
      <div className="flex flex-col flex-1 pt-5 pb-4 overflow-y-auto">
        <div className="flex items-center flex-shrink-0 px-4">
          <Globe className="h-8 w-8 text-blue-600" />
          <span className="ml-2 text-lg font-semibold text-gray-900">
            Social AI
          </span>
        </div>
        
        <nav className="mt-8 flex-1 px-2 space-y-1">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.name}
                to={item.href}
                className={({ isActive }) =>
                  `group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-150 ${
                    isActive
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`
                }
              >
                <Icon
                  className="mr-3 h-5 w-5 flex-shrink-0"
                  aria-hidden="true"
                />
                {item.name}
              </NavLink>
            );
          })}
        </nav>

        {/* User info at bottom */}
        <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
          <div className="flex items-center">
            <div>
              <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                <Users className="h-5 w-5 text-white" />
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700 group-hover:text-gray-900">
                {user?.name || 'User'}
              </p>
              <p className="text-xs font-medium text-gray-500 group-hover:text-gray-700">
                {user?.subscription?.plan || 'Free Plan'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;