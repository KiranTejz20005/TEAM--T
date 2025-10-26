import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  FiTrendingUp, 
  FiDollarSign, 
  FiFileText, 
  FiBarChart2,
  FiUpload,
  FiMessageSquare,
  FiMic,
  FiHelpCircle
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import { documentAPI, analyticsAPI, faqAPI } from '../services/api';
import toast from 'react-hot-toast';

const Dashboard = () => {
  const { documents, chatSessions, voiceEnabled } = useAppStore();
  const [stats, setStats] = useState({
    totalDocuments: 0,
    totalChats: 0,
    totalAnalytics: 0,
    voiceInteractions: 0
  });

  // Fetch dashboard data
  const { data: documentsData, isLoading: documentsLoading } = useQuery(
    'documents',
    () => documentAPI.getAll(),
    { retry: 1 }
  );

  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    'analytics',
    () => analyticsAPI.getKPIs({}),
    { retry: 1 }
  );

  const { data: faqData, isLoading: faqLoading } = useQuery(
    'faq-suggestions',
    () => faqAPI.getSuggestions('dashboard'),
    { retry: 1 }
  );

  useEffect(() => {
    if (documentsData) {
      setStats(prev => ({
        ...prev,
        totalDocuments: documentsData.count || 0
      }));
    }
  }, [documentsData]);

  const quickActions = [
    {
      title: 'Upload Document',
      description: 'Upload PDF, Excel, or CSV files',
      icon: FiUpload,
      color: 'bg-primary-500',
      href: '/documents',
      action: () => toast.success('Navigate to Documents page')
    },
    {
      title: 'Start Chat',
      description: 'Ask questions about your data',
      icon: FiMessageSquare,
      color: 'bg-success-500',
      href: '/chat',
      action: () => toast.success('Navigate to Chat page')
    },
    {
      title: 'View Analytics',
      description: 'Financial analysis and insights',
      icon: FiBarChart2,
      color: 'bg-warning-500',
      href: '/analytics',
      action: () => toast.success('Navigate to Analytics page')
    },
    {
      title: 'Voice Assistant',
      description: 'Speak your questions',
      icon: FiMic,
      color: 'bg-error-500',
      href: '/voice',
      action: () => toast.success('Navigate to Voice Assistant')
    }
  ];

  const recentActivities = [
    {
      type: 'document',
      title: 'Financial Statement Q3 2024.pdf',
      timestamp: '2 hours ago',
      status: 'processed'
    },
    {
      type: 'chat',
      title: 'What is the revenue trend?',
      timestamp: '1 hour ago',
      status: 'completed'
    },
    {
      type: 'analytics',
      title: 'Ratio Analysis Report',
      timestamp: '30 minutes ago',
      status: 'generated'
    }
  ];

  const metricCards = [
    {
      title: 'Total Documents',
      value: stats.totalDocuments,
      change: '+12%',
      changeType: 'positive',
      icon: FiFileText,
      color: 'text-primary-500'
    },
    {
      title: 'Chat Sessions',
      value: stats.totalChats,
      change: '+8%',
      changeType: 'positive',
      icon: FiMessageSquare,
      color: 'text-success-500'
    },
    {
      title: 'Analytics Reports',
      value: stats.totalAnalytics,
      change: '+15%',
      changeType: 'positive',
      icon: FiBarChart2,
      color: 'text-warning-500'
    },
    {
      title: 'Voice Interactions',
      value: stats.voiceInteractions,
      change: '+25%',
      changeType: 'positive',
      icon: FiMic,
      color: 'text-error-500'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome to FinMDA-Bot - Your Financial AI Assistant</p>
        </div>
        <div className="flex items-center space-x-4">
          {voiceEnabled && (
            <div className="flex items-center space-x-2 bg-primary-100 text-primary-700 px-3 py-2 rounded-lg">
              <FiMic size={16} />
              <span className="text-sm font-medium">Voice Active</span>
            </div>
          )}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900">{card.value}</p>
                </div>
                <div className={`p-3 rounded-lg ${card.color.replace('text-', 'bg-').replace('-500', '-100')}`}>
                  <Icon size={24} className={card.color} />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                <span className={`text-sm font-medium ${
                  card.changeType === 'positive' ? 'text-success-600' : 'text-error-600'
                }`}>
                  {card.change}
                </span>
                <span className="text-sm text-gray-500 ml-2">from last month</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickActions.map((action, index) => {
            const Icon = action.icon;
            return (
              <button
                key={index}
                onClick={action.action}
                className="flex items-center space-x-3 p-4 rounded-lg border border-gray-200 hover:border-gray-300 hover:shadow-sm transition-all duration-200 text-left"
              >
                <div className={`p-2 rounded-lg ${action.color}`}>
                  <Icon size={20} className="text-white" />
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{action.title}</h3>
                  <p className="text-sm text-gray-500">{action.description}</p>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            {recentActivities.map((activity, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className={`w-2 h-2 rounded-full ${
                  activity.status === 'processed' ? 'bg-success-500' :
                  activity.status === 'completed' ? 'bg-primary-500' :
                  'bg-warning-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                  <p className="text-xs text-gray-500">{activity.timestamp}</p>
                </div>
                <span className={`text-xs px-2 py-1 rounded-full ${
                  activity.status === 'processed' ? 'bg-success-100 text-success-700' :
                  activity.status === 'completed' ? 'bg-primary-100 text-primary-700' :
                  'bg-warning-100 text-warning-700'
                }`}>
                  {activity.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* FAQ Suggestions */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Help</h2>
          <div className="space-y-3">
            {faqData?.suggestions?.slice(0, 5).map((suggestion, index) => (
              <button
                key={index}
                className="w-full text-left p-3 rounded-lg border border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-colors duration-200"
              >
                <p className="text-sm font-medium text-gray-900">{suggestion}</p>
              </button>
            ))}
          </div>
          <div className="mt-4">
            <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
              View all FAQs →
            </button>
          </div>
        </div>
      </div>

      {/* Getting Started */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-6 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold mb-2">Getting Started with FinMDA-Bot</h2>
            <p className="text-primary-100 mb-4">
              Upload your financial documents and start asking questions to get AI-powered insights.
            </p>
            <div className="flex space-x-4">
              <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-primary-50 transition-colors duration-200">
                Upload Document
              </button>
              <button className="border border-white text-white px-4 py-2 rounded-lg font-medium hover:bg-white hover:text-primary-600 transition-colors duration-200">
                Learn More
              </button>
            </div>
          </div>
          <div className="hidden md:block">
            <div className="w-32 h-32 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
              <FiTrendingUp size={48} className="text-white" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
