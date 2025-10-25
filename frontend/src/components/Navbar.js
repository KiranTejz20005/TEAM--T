import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  FiMenu, 
  FiX, 
  FiBell, 
  FiSettings, 
  FiUser, 
  FiLogOut,
  FiSun,
  FiMoon,
  FiMic,
  FiMicOff
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import toast from 'react-hot-toast';

const Navbar = () => {
  const location = useLocation();
  const { 
    sidebarOpen, 
    setSidebarOpen, 
    theme, 
    setTheme, 
    voiceEnabled, 
    setVoiceEnabled,
    user,
    isAuthenticated
  } = useAppStore();
  
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications, setNotifications] = useState([]);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    document.documentElement.classList.toggle('dark', newTheme === 'dark');
  };

  const toggleVoice = () => {
    setVoiceEnabled(!voiceEnabled);
    toast.success(`Voice assistant ${!voiceEnabled ? 'enabled' : 'disabled'}`);
  };

  const handleLogout = () => {
    // Implement logout logic
    toast.success('Logged out successfully');
  };

  const getPageTitle = () => {
    const path = location.pathname;
    switch (path) {
      case '/':
        return 'Dashboard';
      case '/chat':
        return 'Chat';
      case '/documents':
        return 'Documents';
      case '/analytics':
        return 'Analytics';
      case '/faq':
        return 'FAQ';
      case '/voice':
        return 'Voice Assistant';
      case '/settings':
        return 'Settings';
      default:
        return 'FinMDA-Bot';
    }
  };

  return (
    <nav className="bg-white border-b border-gray-200 px-4 py-3 flex items-center justify-between">
      {/* Left side */}
      <div className="flex items-center space-x-4">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
        >
          {sidebarOpen ? <FiX size={20} /> : <FiMenu size={20} />}
        </button>
        
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">F</span>
          </div>
          <h1 className="text-xl font-semibold text-gray-900">
            FinMDA-Bot
          </h1>
        </div>
        
        <div className="hidden md:block">
          <h2 className="text-lg font-medium text-gray-700">
            {getPageTitle()}
          </h2>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center space-x-2">
        {/* Voice Assistant Toggle */}
        <button
          onClick={toggleVoice}
          className={`p-2 rounded-lg transition-colors duration-200 ${
            voiceEnabled 
              ? 'bg-primary-500 text-white' 
              : 'hover:bg-gray-100 text-gray-600'
          }`}
          title={voiceEnabled ? 'Disable Voice Assistant' : 'Enable Voice Assistant'}
        >
          {voiceEnabled ? <FiMic size={20} /> : <FiMicOff size={20} />}
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
        >
          {theme === 'light' ? <FiMoon size={20} /> : <FiSun size={20} />}
        </button>

        {/* Notifications */}
        <div className="relative">
          <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200 relative">
            <FiBell size={20} />
            {notifications.length > 0 && (
              <span className="absolute -top-1 -right-1 bg-error-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {notifications.length}
              </span>
            )}
          </button>
        </div>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
              <FiUser size={16} />
            </div>
            <span className="hidden md:block text-sm font-medium text-gray-700">
              {user?.name || 'User'}
            </span>
          </button>

          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
              <Link
                to="/settings"
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                onClick={() => setShowUserMenu(false)}
              >
                <FiSettings size={16} />
                <span>Settings</span>
              </Link>
              
              <button
                onClick={() => {
                  handleLogout();
                  setShowUserMenu(false);
                }}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 w-full text-left"
              >
                <FiLogOut size={16} />
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Mobile menu overlay */}
      {showUserMenu && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowUserMenu(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;
