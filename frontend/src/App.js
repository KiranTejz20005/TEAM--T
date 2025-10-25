import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { HelmetProvider } from 'react-helmet-async';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import LoadingSpinner from './components/LoadingSpinner';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Analytics from './pages/Analytics';
import FAQ from './pages/FAQ';
import Settings from './pages/Settings';
import VoiceAssistant from './pages/VoiceAssistant';

// Context
import { useAppStore } from './store/appStore';

// Styles
import './index.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  const { sidebarOpen, setSidebarOpen } = useAppStore();

  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <ErrorBoundary>
          <Router>
            <div className="min-h-screen bg-gray-50">
              <Navbar />
              
              <div className="flex">
                <Sidebar />
                
                <main className={`flex-1 transition-all duration-300 ${
                  sidebarOpen ? 'ml-64' : 'ml-16'
                }`}>
                  <div className="p-6">
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/chat" element={<Chat />} />
                      <Route path="/documents" element={<Documents />} />
                      <Route path="/analytics" element={<Analytics />} />
                      <Route path="/faq" element={<FAQ />} />
                      <Route path="/voice" element={<VoiceAssistant />} />
                      <Route path="/settings" element={<Settings />} />
                    </Routes>
                  </div>
                </main>
              </div>
              
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#363636',
                    color: '#fff',
                  },
                  success: {
                    duration: 3000,
                    iconTheme: {
                      primary: '#4ade80',
                      secondary: '#fff',
                    },
                  },
                  error: {
                    duration: 5000,
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#fff',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </ErrorBoundary>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
