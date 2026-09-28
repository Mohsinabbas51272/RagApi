import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ChatInterface from './components/ChatInterface';
import ChunkExplorer from './components/ChunkExplorer';
import StatsDashboard from './components/StatsDashboard';
import AdminModal from './components/AdminModal';
import { checkHealth, fetchWebsites, fetchStats, queryRAG } from './services/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('chat'); // 'chat' | 'chunks' | 'analytics'
  const [backendStatus, setBackendStatus] = useState('connecting');
  const [websites, setWebsites] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedFilter, setSelectedFilter] = useState(null);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load initial data
  const loadInitialData = async () => {
    const health = await checkHealth();
    setBackendStatus(health.status === 'healthy' ? 'online' : 'offline');

    const sitesRes = await fetchWebsites();
    if (sitesRes && sitesRes.websites) {
      setWebsites(sitesRes.websites);
    }

    const statsRes = await fetchStats();
    if (statsRes) {
      setStats(statsRes);
    }
  };

  useEffect(() => {
    loadInitialData();
    const interval = setInterval(loadInitialData, 15000);
    return () => clearInterval(interval);
  }, []);

  const handleSendMessage = async (userText) => {
    // 1. Add user message
    const userMessage = {
      sender: 'user',
      text: userText,
      timestamp: new Date().toISOString()
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 2. Call FastAPI backend
      const response = await queryRAG(userText, selectedFilter);
      
      const assistantMessage = {
        sender: 'assistant',
        text: response.answer,
        sources: response.sources || [],
        processingTime: response.processing_time_ms,
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        sender: 'assistant',
        text: "I am having trouble connecting to the Brillanz RAG backend. Please verify that the FastAPI backend server is running on port 8000.",
        sources: [],
        timestamp: new Date().toISOString()
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectWebsiteFromDashboard = (websiteId) => {
    setSelectedFilter(websiteId);
    setActiveTab('chat');
  };

  const handleAskAboutChunk = (snippet, websiteId) => {
    setSelectedFilter(websiteId || null);
    setActiveTab('chat');
    handleSendMessage(`Tell me more about this: "${snippet}..."`);
  };

  const handleClearMessages = () => {
    setMessages([]);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-brand-600 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        backendStatus={backendStatus}
        onOpenAdmin={() => setIsAdminOpen(true)}
        selectedFilter={selectedFilter}
        setSelectedFilter={setSelectedFilter}
        websites={websites}
      />

      {/* Main Content Area */}
      <main className="flex-1">
        {activeTab === 'chat' && (
          <ChatInterface
            messages={messages}
            onSendMessage={handleSendMessage}
            isLoading={isLoading}
            selectedFilter={selectedFilter}
            onClearMessages={handleClearMessages}
          />
        )}

        {activeTab === 'chunks' && (
          <ChunkExplorer
            websites={websites}
            onAskAboutChunk={handleAskAboutChunk}
          />
        )}

        {activeTab === 'analytics' && (
          <StatsDashboard
            stats={stats}
            websites={websites}
            onSelectWebsite={handleSelectWebsiteFromDashboard}
            onGoToChunks={() => setActiveTab('chunks')}
          />
        )}
      </main>

      {/* Admin Controls Modal */}
      <AdminModal
        isOpen={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
        onRefreshData={loadInitialData}
        websites={websites}
      />
    </div>
  );
}
