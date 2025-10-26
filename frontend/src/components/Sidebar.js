import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  FiHome, 
  FiMessageSquare, 
  FiFileText, 
  FiBarChart2, 
  FiHelpCircle, 
  FiMic, 
  FiSettings,
  FiTrendingUp,
  FiPieChart,
  FiDollarSign
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';

const Sidebar = () => {
  const location = useLocation();
  const { sidebarOpen, voiceEnabled } = useAppStore();

  const navigation = [
    {
      name: 'Dashboard',
      href: '/',
      icon: FiHome,
      description: 'Overview and insights'
    },
    {
      name: 'Chat',
      href: '/chat',
      icon: FiMessageSquare,
      description: 'AI conversation'
    },
    {
      name: 'Documents',
      href: '/documents',
      icon: FiFileText,
      description: 'Upload and manage files'
    },
    {
      name: 'Analytics',
      href: '/analytics',
      icon: FiBarChart2,
      description: 'Financial analysis'
    },
    {
      name: 'Voice Assistant',
      href: '/voice',
      icon: FiMic,
      description: 'Voice interactions',
      badge: voiceEnabled ? 'Active' : null
    },
    {
      name: 'FAQ',
      href: '/faq',
      icon: FiHelpCircle,
      description: 'Help and support'
    },
    {
      name: 'Settings',
      href: '/settings',
      icon: FiSettings,
      description: 'Preferences'
    }
  ];

  const quickActions = [
    {
      name: 'Upload Document',
      href: '/documents',
      icon: FiFileText,
      color: 'text-primary-500'
    },
    {
      name: 'Start Chat',
      href: '/chat',
      icon: FiMessageSquare,
      color: 'text-success-500'
    },
    {
      name: 'View Analytics',
      href: '/analytics',
      icon: FiTrendingUp,
      color: 'text-warning-500'
    }
  ];

  const isActive = (href) => {
    if (href === '/') {
      return location.pathname === '/';
    }
    return location.pathname.startsWith(href);
  };

  return (
    <div className={`fixed left-0 top-16 h-screen bg-white border-r border-gray-200 transition-all duration-300 z-30 ${
      sidebarOpen ? 'w-64' : 'w-16'
    }`}>
      <div className="flex flex-col h-full">
        {/* Navigation */}
        <div className="flex-1 overflow-y-auto">
          <nav className="p-4 space-y-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const active = isActive(item.href);
              
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors duration-200 group ${
                    active
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  title={sidebarOpen ? '' : item.description}
                >
                  <Icon size={20} className="flex-shrink-0" />
                  {sidebarOpen && (
                    <>
                      <span className="font-medium">{item.name}</span>
                      {item.badge && (
                        <span className="ml-auto px-2 py-1 text-xs bg-success-500 text-white rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </Link>
              );
            })}
          </nav>

          {/* Quick Actions */}
          {sidebarOpen && (
            <div className="px-4 py-2">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">
                Quick Actions
              </h3>
              <div className="space-y-1">
                {quickActions.map((action) => {
                  const Icon = action.icon;
                  return (
                    <Link
                      key={action.name}
                      to={action.href}
                      className="flex items-center space-x-3 px-3 py-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors duration-200"
                    >
                      <Icon size={16} className={`flex-shrink-0 ${action.color}`} />
                      <span className="text-sm">{action.name}</span>
                    </Link>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {sidebarOpen && (
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500 text-center">
              <p>FinMDA-Bot v1.0.0</p>
              <p className="mt-1">Financial AI Assistant</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
