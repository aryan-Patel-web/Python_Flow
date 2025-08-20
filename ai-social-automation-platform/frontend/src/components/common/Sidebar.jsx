import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = ({ sidebarOpen, setSidebarOpen }) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '🏠' },
    { name: 'Credentials', href: '/credentials', icon: '⚙️' },
    { name: 'Domains', href: '/domains', icon: '🎯' },
    { name: 'Content', href: '/content', icon: '📝' },
    { name: 'Analytics', href: '/analytics', icon: '📊' },
    { name: 'Automation', href: '/automation', icon: '⚡' },
    { name: 'Billing', href: '/billing', icon: '💳' },
  ];

  const classNames = (...classes) => {
    return classes.filter(Boolean).join(' ');
  };

  const SidebarContent = () => (
    <div className="flex flex-col h-0 flex-1 bg-gray-800">
      {/* Logo */}
      <div className="flex items-center h-16 flex-shrink-0 px-4 bg-gray-900">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <span className="text-2xl">🚀</span>
          </div>
          <div className="ml-3">
            <h1 className="text-white text-lg font-semibold">AI Social</h1>
            <p className="text-gray-300 text-xs">Automation Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <nav className="flex-1 px-2 py-4 space-y-1">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <Link
                key={item.name}
                to={item.href}
                className={classNames(
                  isActive
                    ? 'bg-gray-900 text-white'
                    : 'text-gray-300 hover:bg-gray-700 hover:text-white',
                  'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors duration-150'
                )}
                onClick={() => setSidebarOpen(false)}
              >
                <span className="mr-3 text-lg">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </nav>

        {/* Bottom section */}
        <div className="flex-shrink-0 p-4 border-t border-gray-700">
          <div className="bg-gray-700 rounded-lg p-3">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-lg">✨</span>
              </div>
              <div className="ml-3 flex-1">
                <p className="text-sm font-medium text-white">Pro Plan</p>
                <p className="text-xs text-gray-300">Upgrade for more features</p>
              </div>
            </div>
            <Link
              to="/billing"
              className="mt-2 w-full bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium py-1 px-3 rounded transition-colors duration-150 block text-center"
              onClick={() => setSidebarOpen(false)}
            >
              Upgrade
            </Link>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 flex z-40 md:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="relative flex-1 flex flex-col max-w-xs w-full">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                type="button"
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <span className="sr-only">Close sidebar</span>
                <svg className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <SidebarContent />
          </div>
          <div className="flex-shrink-0 w-14" />
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden md:flex md:flex-shrink-0">
        <div className="flex flex-col w-64">
          <SidebarContent />
        </div>
      </div>
    </>
  );
};

export default Sidebar;