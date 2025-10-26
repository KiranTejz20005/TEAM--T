import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  FiTrendingUp, 
  FiTrendingDown, 
  FiDollarSign, 
  FiBarChart2,
  FiPieChart,
  FiDownload,
  FiRefreshCw,
  FiFilter
} from 'react-icons/fi';
import { useAppStore } from '../store/appStore';
import { analyticsAPI } from '../services/api';
import Plot from 'react-plotly.js';

const Analytics = () => {
  const { analyticsData, setAnalyticsData } = useAppStore();
  const [selectedMetrics, setSelectedMetrics] = useState([]);
  const [timeRange, setTimeRange] = useState('12m');
  const [chartType, setChartType] = useState('line');

  // Fetch analytics data
  const { data: analytics, isLoading, error } = useQuery(
    ['analytics', timeRange],
    () => analyticsAPI.getKPIs({ time_range: timeRange }),
    { retry: 1 }
  );

  // Fetch ratios
  const { data: ratios } = useQuery(
    'ratios',
    () => analyticsAPI.getRatios({}),
    { retry: 1 }
  );

  // Fetch trends
  const { data: trends } = useQuery(
    'trends',
    () => analyticsAPI.getTrends({}),
    { retry: 1 }
  );

  useEffect(() => {
    if (analytics) {
      setAnalyticsData(analytics);
    }
  }, [analytics, setAnalyticsData]);

  const kpiCards = [
    {
      title: 'Revenue',
      value: analytics?.revenue || 0,
      change: '+12.5%',
      changeType: 'positive',
      icon: FiDollarSign,
      color: 'text-success-500'
    },
    {
      title: 'Net Income',
      value: analytics?.net_income || 0,
      change: '+8.3%',
      changeType: 'positive',
      icon: FiTrendingUp,
      color: 'text-primary-500'
    },
    {
      title: 'Total Assets',
      value: analytics?.total_assets || 0,
      change: '+5.7%',
      changeType: 'positive',
      icon: FiBarChart2,
      color: 'text-warning-500'
    },
    {
      title: 'Debt Ratio',
      value: analytics?.debt_ratio || 0,
      change: '-2.1%',
      changeType: 'negative',
      icon: FiTrendingDown,
      color: 'text-error-500'
    }
  ];

  const ratioCategories = [
    {
      name: 'Liquidity Ratios',
      ratios: [
        { name: 'Current Ratio', value: 2.1, benchmark: 2.0, status: 'good' },
        { name: 'Quick Ratio', value: 1.5, benchmark: 1.0, status: 'good' },
        { name: 'Cash Ratio', value: 0.8, benchmark: 0.5, status: 'good' }
      ]
    },
    {
      name: 'Profitability Ratios',
      ratios: [
        { name: 'Gross Margin', value: 0.35, benchmark: 0.30, status: 'good' },
        { name: 'Net Margin', value: 0.12, benchmark: 0.10, status: 'good' },
        { name: 'ROE', value: 0.18, benchmark: 0.15, status: 'good' }
      ]
    },
    {
      name: 'Leverage Ratios',
      ratios: [
        { name: 'Debt-to-Equity', value: 0.45, benchmark: 0.50, status: 'good' },
        { name: 'Interest Coverage', value: 4.2, benchmark: 3.0, status: 'good' },
        { name: 'Debt Ratio', value: 0.31, benchmark: 0.40, status: 'good' }
      ]
    }
  ];

  const generateChartData = () => {
    // Sample data for demonstration
    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const revenue = [100, 120, 110, 130, 140, 150, 160, 170, 180, 190, 200, 210];
    const expenses = [80, 90, 85, 95, 100, 105, 110, 115, 120, 125, 130, 135];
    const profit = revenue.map((r, i) => r - expenses[i]);

    return {
      x: months,
      revenue,
      expenses,
      profit
    };
  };

  const chartData = generateChartData();

  const plotlyConfig = {
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
  };

  const plotlyLayout = {
    title: 'Financial Performance Trends',
    xaxis: { title: 'Month' },
    yaxis: { title: 'Amount ($)' },
    hovermode: 'closest',
    showlegend: true,
    margin: { t: 40, r: 30, b: 40, l: 50 }
  };

  const plotlyData = [
    {
      x: chartData.x,
      y: chartData.revenue,
      type: chartType,
      name: 'Revenue',
      line: { color: '#10B981' }
    },
    {
      x: chartData.x,
      y: chartData.expenses,
      type: chartType,
      name: 'Expenses',
      line: { color: '#EF4444' }
    },
    {
      x: chartData.x,
      y: chartData.profit,
      type: chartType,
      name: 'Net Profit',
      line: { color: '#3B82F6' }
    }
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <FiBarChart2 size={48} className="text-error-500 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Error Loading Analytics</h3>
        <p className="text-gray-600">Failed to load analytics data. Please try again.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Financial insights and performance metrics</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="3m">Last 3 months</option>
            <option value="6m">Last 6 months</option>
            <option value="12m">Last 12 months</option>
            <option value="24m">Last 24 months</option>
          </select>
          <button className="flex items-center space-x-2 px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors duration-200">
            <FiDownload size={16} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpiCards.map((card, index) => {
          const Icon = card.icon;
          return (
            <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-900">
                    {typeof card.value === 'number' ? `$${card.value.toLocaleString()}` : card.value}
                  </p>
                </div>
                <div className={`p-3 rounded-lg ${
                  card.color === 'text-success-500' ? 'bg-success-100' :
                  card.color === 'text-primary-500' ? 'bg-primary-100' :
                  card.color === 'text-warning-500' ? 'bg-warning-100' :
                  'bg-error-100'
                }`}>
                  <Icon size={24} className={card.color} />
                </div>
              </div>
              <div className="mt-4 flex items-center">
                <span className={`text-sm font-medium ${
                  card.changeType === 'positive' ? 'text-success-600' : 'text-error-600'
                }`}>
                  {card.change}
                </span>
                <span className="text-sm text-gray-500 ml-2">vs last period</span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance Chart */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Performance Trends</h2>
            <div className="flex items-center space-x-2">
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value)}
                className="text-sm border border-gray-300 rounded px-2 py-1"
              >
                <option value="line">Line</option>
                <option value="bar">Bar</option>
                <option value="scatter">Scatter</option>
              </select>
            </div>
          </div>
          <div className="h-80">
            <Plot
              data={plotlyData}
              layout={plotlyLayout}
              config={plotlyConfig}
              style={{ width: '100%', height: '100%' }}
            />
          </div>
        </div>

        {/* Ratio Analysis */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Ratio Analysis</h2>
          <div className="space-y-4">
            {ratioCategories.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                <h3 className="text-sm font-medium text-gray-700 mb-2">{category.name}</h3>
                <div className="space-y-2">
                  {category.ratios.map((ratio, ratioIndex) => (
                    <div key={ratioIndex} className="flex items-center justify-between">
                      <span className="text-sm text-gray-600">{ratio.name}</span>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium">
                          {typeof ratio.value === 'number' ? (ratio.value * 100).toFixed(1) + '%' : ratio.value}
                        </span>
                        <span className={`text-xs px-2 py-1 rounded-full ${
                          ratio.status === 'good' ? 'bg-success-100 text-success-700' :
                          ratio.status === 'warning' ? 'bg-warning-100 text-warning-700' :
                          'bg-error-100 text-error-700'
                        }`}>
                          {ratio.status}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Detailed Analysis */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Detailed Analysis</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Key Insights</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Revenue growth of 12.5% indicates strong market performance</li>
              <li>• Improved operational efficiency with better expense management</li>
              <li>• Healthy liquidity position with current ratio above industry average</li>
              <li>• Debt levels are well-managed and within acceptable limits</li>
            </ul>
          </div>
          <div>
            <h3 className="text-sm font-medium text-gray-700 mb-3">Recommendations</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Consider increasing investment in growth opportunities</li>
              <li>• Monitor cash flow trends for seasonal variations</li>
              <li>• Evaluate cost reduction strategies for non-essential expenses</li>
              <li>• Review debt structure for optimal capital allocation</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-gray-50 rounded-lg p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-900">Export Analytics Report</h3>
            <p className="text-sm text-gray-600">Download comprehensive financial analysis</p>
          </div>
          <div className="flex space-x-2">
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              PDF Report
            </button>
            <button className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors duration-200">
              Excel Data
            </button>
            <button className="px-4 py-2 bg-primary-500 text-white rounded-lg text-sm font-medium hover:bg-primary-600 transition-colors duration-200">
              Full Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
