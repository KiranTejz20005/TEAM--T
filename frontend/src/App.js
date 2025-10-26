import React from 'react';
import { Routes, Route } from 'react-router-dom';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import ErrorBoundary from './components/ErrorBoundary';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Documents from './pages/Documents';
import Analytics from './pages/Analytics';
import FAQ from './pages/FAQ';
import Settings from './pages/Settings';
import VoiceAssistant from './pages/VoiceAssistant';
import MDAGenerator from './pages/MDAGenerator';

// Context
import { useAppStore } from './store/appStore';

// Styles
import './index.css';

function App() {
  const { sidebarOpen } = useAppStore();

  return (
    <ErrorBoundary>
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
                <Route path="/mda" element={<MDAGenerator />} />
                <Route path="/faq" element={<FAQ />} />
                <Route path="/voice" element={<VoiceAssistant />} />
                <Route path="/settings" element={<Settings />} />
              </Routes>
            </div>
          </main>
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
