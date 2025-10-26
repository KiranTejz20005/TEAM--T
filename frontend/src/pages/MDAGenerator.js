import React, { useState } from 'react';
import { useMutation } from 'react-query';
import { FiFileText, FiDownload, FiRefreshCw } from 'react-icons/fi';
import axios from 'axios';
import toast from 'react-hot-toast';
import ReactMarkdown from 'react-markdown';

const MDAGenerator = () => {
  const [period, setPeriod] = useState('Q3 2024');
  const [mdaReport, setMdaReport] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const generateMutation = useMutation(
    async () => {
      const response = await axios.post(
        `http://localhost:8000/api/v1/mda/generate?period=${encodeURIComponent(period)}`
      );
      return response.data;
    },
    {
      onSuccess: (data) => {
        setMdaReport(data);
        setIsGenerating(false);
        toast.success('MD&A report generated successfully!');
      },
      onError: (error) => {
        setIsGenerating(false);
        toast.error('Failed to generate MD&A report');
        console.error('Error:', error);
      }
    }
  );

  const handleGenerate = () => {
    setIsGenerating(true);
    generateMutation.mutate();
  };

  const handleDownload = () => {
    if (!mdaReport) return;

    const blob = new Blob([mdaReport.md_a_draft], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `MDA_Report_${period.replace(/\s+/g, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          MD&A Report Generator
        </h1>
        <p className="text-gray-600">
          Automatically generate Management Discussion & Analysis reports from financial data
        </p>
      </div>

      {/* Input Section */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Reporting Period
            </label>
            <input
              type="text"
              value={period}
              onChange={(e) => setPeriod(e.target.value)}
              placeholder="e.g., Q3 2024"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="px-6 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            {isGenerating ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                <span>Generating...</span>
              </>
            ) : (
              <>
                <FiFileText />
                <span>Generate MD&A Report</span>
              </>
            )}
          </button>
        </div>

        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">What gets generated:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✓ Executive Summary</li>
            <li>✓ Results of Operations</li>
            <li>✓ Liquidity and Capital Resources</li>
            <li>✓ Risk Factors</li>
            <li>✓ Key Financial Metrics & KPIs</li>
            <li>✓ YoY/QoQ Analysis</li>
            <li>✓ Citations to Source Data</li>
          </ul>
        </div>
      </div>

      {/* Results Section */}
      {mdaReport && (
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Report Header */}
          <div className="flex items-center justify-between mb-6 pb-4 border-b">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">
                MD&A Report - {period}
              </h2>
              <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                <span>
                  Confidence: {(mdaReport.confidence * 100).toFixed(0)}%
                </span>
                <span>•</span>
                <span>
                  Generated in {mdaReport.generation_time.toFixed(2)}s
                </span>
                <span>•</span>
                <span>
                  {mdaReport.key_metrics?.length || 0} Key Metrics
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleDownload}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
              >
                <FiDownload />
                <span>Download</span>
              </button>
              <button
                onClick={handleGenerate}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 flex items-center space-x-2"
              >
                <FiRefreshCw />
                <span>Regenerate</span>
              </button>
            </div>
          </div>

          {/* Key Metrics */}
          {mdaReport.key_metrics && mdaReport.key_metrics.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Key Financial Metrics
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {mdaReport.key_metrics.slice(0, 6).map((metric, index) => (
                  <div key={index} className="p-4 bg-gray-50 rounded-lg">
                    <div className="text-sm text-gray-600">{metric.name}</div>
                    <div className="text-2xl font-bold text-gray-900">
                      ${metric.current_value?.toLocaleString() || 'N/A'}
                    </div>
                    <div className={`text-sm ${
                      metric.change_percent > 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {metric.change_percent > 0 ? '↑' : '↓'}{' '}
                      {Math.abs(metric.change_percent).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* MD&A Content */}
          <div className="prose max-w-none">
            <ReactMarkdown>{mdaReport.md_a_draft}</ReactMarkdown>
          </div>

          {/* Citations */}
          {mdaReport.citations && mdaReport.citations.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">
                Citations & Sources
              </h3>
              <div className="text-sm text-gray-600">
                {mdaReport.citations.length} source(s) referenced
              </div>
            </div>
          )}
        </div>
      )}

      {/* Empty State */}
      {!mdaReport && !isGenerating && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <FiFileText size={32} className="text-primary-500" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            No Report Generated Yet
          </h3>
          <p className="text-gray-600 mb-6">
            Click "Generate MD&A Report" to create a comprehensive financial analysis report
          </p>
          <div className="text-sm text-gray-500">
            <p>The system will automatically:</p>
            <p>• Extract financial data from uploaded documents</p>
            <p>• Calculate key performance indicators</p>
            <p>• Generate SEC-compliant narrative sections</p>
            <p>• Provide citations to source data</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MDAGenerator;



