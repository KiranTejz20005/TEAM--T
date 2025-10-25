import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { 
  FiSearch, 
  FiHelpCircle, 
  FiChevronDown, 
  FiChevronUp,
  FiExternalLink,
  FiMessageSquare,
  FiBookOpen
} from 'react-icons/fi';
import { faqAPI } from '../services/api';
import toast from 'react-hot-toast';

const FAQ = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [expandedItems, setExpandedItems] = useState(new Set());
  const [suggestedQuestions, setSuggestedQuestions] = useState([]);

  // Fetch FAQ categories
  const { data: categories } = useQuery(
    'faq-categories',
    () => faqAPI.getCategories(),
    { retry: 1 }
  );

  // Fetch FAQ search results
  const { data: searchResults, isLoading: searchLoading } = useQuery(
    ['faq-search', searchQuery, selectedCategory],
    () => faqAPI.search(searchQuery, selectedCategory, 10),
    { 
      retry: 1,
      enabled: searchQuery.length > 0
    }
  );

  // Fetch suggested questions
  const { data: suggestions } = useQuery(
    'faq-suggestions',
    () => faqAPI.getSuggestions(''),
    { retry: 1 }
  );

  // Fetch all FAQs if no search
  const { data: allFAQs, isLoading: allFAQsLoading } = useQuery(
    'faq-all',
    () => faqAPI.getAll(),
    { 
      retry: 1,
      enabled: searchQuery.length === 0
    }
  );

  useEffect(() => {
    if (suggestions?.suggestions) {
      setSuggestedQuestions(suggestions.suggestions);
    }
  }, [suggestions]);

  const toggleExpanded = (itemId) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(itemId)) {
      newExpanded.delete(itemId);
    } else {
      newExpanded.add(itemId);
    }
    setExpandedItems(newExpanded);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // Search is handled by the query
      toast.success(`Searching for: ${searchQuery}`);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setSearchQuery(suggestion);
    toast.success(`Searching for: ${suggestion}`);
  };

  const faqItems = searchQuery.length > 0 ? searchResults?.results : allFAQs?.faqs || [];

  const quickStartGuide = [
    {
      step: 1,
      title: 'Upload Your Documents',
      description: 'Upload PDF, Excel, or CSV files containing your financial data',
      icon: '📄'
    },
    {
      step: 2,
      title: 'Ask Questions',
      description: 'Use natural language to ask questions about your financial data',
      icon: '💬'
    },
    {
      step: 3,
      title: 'Get Insights',
      description: 'Receive detailed analysis, ratios, and forecasts',
      icon: '📊'
    },
    {
      step: 4,
      title: 'Use Voice Assistant',
      description: 'Speak your questions using the voice assistant feature',
      icon: '🎤'
    }
  ];

  const commonQuestions = [
    'What is FinMDA-Bot?',
    'How do I upload documents?',
    'What financial ratios can you calculate?',
    'Can you predict future performance?',
    'How do I use the voice assistant?',
    'Is my data secure?',
    'What file formats are supported?',
    'How accurate are the financial calculations?'
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">Help & FAQ</h1>
        <p className="text-gray-600 mt-2">Find answers to common questions about FinMDA-Bot</p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSearch} className="flex items-center space-x-4">
          <div className="flex-1 relative">
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search for help topics..."
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="">All Categories</option>
            {categories?.categories?.map((category) => (
              <option key={category.value} value={category.value}>
                {category.name}
              </option>
            ))}
          </select>
          <button
            type="submit"
            className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors duration-200"
          >
            Search
          </button>
        </form>
      </div>

      {/* Quick Start Guide */}
      <div className="bg-gradient-to-r from-primary-500 to-primary-600 rounded-lg p-6 text-white">
        <div className="flex items-center space-x-3 mb-4">
          <FiBookOpen size={24} />
          <h2 className="text-xl font-semibold">Quick Start Guide</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {quickStartGuide.map((step) => (
            <div key={step.step} className="bg-white bg-opacity-20 rounded-lg p-4">
              <div className="flex items-center space-x-3 mb-2">
                <span className="text-2xl">{step.icon}</span>
                <span className="font-semibold">Step {step.step}</span>
              </div>
              <h3 className="font-medium mb-1">{step.title}</h3>
              <p className="text-sm text-primary-100">{step.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Suggested Questions */}
      {suggestedQuestions.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Popular Questions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {suggestedQuestions.slice(0, 8).map((question, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(question)}
                className="text-left p-3 rounded-lg border border-gray-200 hover:border-primary-300 hover:bg-primary-50 transition-colors duration-200"
              >
                <p className="text-sm font-medium text-gray-900">{question}</p>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* FAQ Results */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">
            {searchQuery ? `Search Results for "${searchQuery}"` : 'Frequently Asked Questions'}
          </h2>
          {searchQuery && (
            <p className="text-sm text-gray-600 mt-1">
              {searchResults?.count || 0} results found
            </p>
          )}
        </div>

        {searchLoading || allFAQsLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          </div>
        ) : faqItems.length === 0 ? (
          <div className="text-center py-12">
            <FiHelpCircle size={48} className="text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery ? 'Try different search terms or browse all FAQs' : 'No FAQs available'}
            </p>
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="text-primary-600 hover:text-primary-700 font-medium"
              >
                Clear search and view all FAQs
              </button>
            )}
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {faqItems.map((faq) => (
              <div key={faq.id} className="p-6">
                <button
                  onClick={() => toggleExpanded(faq.id)}
                  className="w-full flex items-center justify-between text-left"
                >
                  <div className="flex-1">
                    <h3 className="text-lg font-medium text-gray-900 mb-1">
                      {faq.question}
                    </h3>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span className="capitalize">{faq.category}</span>
                      <span className="capitalize">{faq.difficulty}</span>
                      {faq.score && (
                        <span>Relevance: {(faq.score * 100).toFixed(0)}%</span>
                      )}
                    </div>
                  </div>
                  <div className="ml-4">
                    {expandedItems.has(faq.id) ? (
                      <FiChevronUp size={20} className="text-gray-400" />
                    ) : (
                      <FiChevronDown size={20} className="text-gray-400" />
                    )}
                  </div>
                </button>

                {expandedItems.has(faq.id) && (
                  <div className="mt-4 pl-0">
                    <div className="prose prose-sm max-w-none">
                      <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                    </div>
                    
                    {faq.examples && faq.examples.length > 0 && (
                      <div className="mt-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Examples:</h4>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {faq.examples.map((example, index) => (
                            <li key={index}>{example}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    <div className="mt-4 flex items-center space-x-4">
                      <button className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 text-sm font-medium">
                        <FiMessageSquare size={16} />
                        <span>Ask a follow-up question</span>
                      </button>
                      <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-700 text-sm font-medium">
                        <FiExternalLink size={16} />
                        <span>Learn more</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Contact Support */}
      <div className="bg-gray-50 rounded-lg p-6">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Still need help?</h3>
          <p className="text-gray-600 mb-4">
            Can't find what you're looking for? Our support team is here to help.
          </p>
          <div className="flex justify-center space-x-4">
            <button className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors duration-200">
              Contact Support
            </button>
            <button className="px-6 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors duration-200">
              Submit Feedback
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FAQ;
