import React from 'react';
import { Bot, Layers, BarChart3, RefreshCw, Globe, Database } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, backendStatus, onOpenAdmin, selectedFilter, setSelectedFilter, websites }) {
  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 glass-panel shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('chat')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center glow-brand shadow-md">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-slate-900">Brillanz</span>
                <span className="text-xs px-2 py-0.5 rounded-full font-semibold bg-brand-50 text-brand-700 border border-brand-200">
                  RAG Core
                </span>
              </div>
              <p className="text-xs text-slate-500 font-medium">Multi-Website Enterprise Intelligence</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <div className="flex items-center space-x-1 bg-slate-100/90 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'chat'
                  ? 'bg-white text-brand-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              <Bot className="w-3.5 h-3.5" />
              <span>Grounded Chat</span>
            </button>

            <button
              onClick={() => setActiveTab('chunks')}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'chunks'
                  ? 'bg-white text-brand-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              <span>Chunk Explorer</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                activeTab === 'analytics'
                  ? 'bg-white text-brand-700 shadow-sm border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-200/60'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Entities & Stats</span>
            </button>
          </div>

          {/* Status & Admin Action */}
          <div className="flex items-center space-x-3">
            <div className="hidden sm:flex items-center space-x-2 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200 text-xs">
              <span className="relative flex h-2 w-2">
                <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${
                  backendStatus === 'online' ? 'bg-emerald-400' : 'bg-amber-400'
                }`}></span>
                <span className={`relative inline-flex rounded-full h-2 w-2 ${
                  backendStatus === 'online' ? 'bg-emerald-500' : 'bg-amber-500'
                }`}></span>
              </span>
              <span className="text-slate-700 font-medium capitalize">{backendStatus === 'online' ? 'FastAPI Ready' : 'Connecting API'}</span>
            </div>

            <button
              onClick={onOpenAdmin}
              className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs font-medium transition-all hover:border-brand-300 shadow-sm"
              title="Admin Ingestion & Index Controls"
            >
              <RefreshCw className="w-3.5 h-3.5 text-brand-600" />
              <span className="hidden md:inline">Admin Controls</span>
            </button>
          </div>
        </div>

        {/* Company Filter Chips Bar */}
        {activeTab === 'chat' && (
          <div className="py-2.5 flex items-center space-x-2 overflow-x-auto border-t border-slate-200/80 text-xs scrollbar-none">
            <span className="text-slate-500 text-[11px] font-semibold uppercase tracking-wider pl-1 pr-1 flex items-center gap-1">
              <Globe className="w-3 h-3 text-slate-400" /> Filter:
            </span>
            <button
              onClick={() => setSelectedFilter(null)}
              className={`px-3 py-1 rounded-full whitespace-nowrap transition-all text-xs font-medium ${
                selectedFilter === null
                  ? 'bg-brand-600 text-white font-semibold shadow-sm'
                  : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200'
              }`}
            >
              All Brillanz (7)
            </button>
            {websites.map((site) => (
              <button
                key={site.id}
                onClick={() => setSelectedFilter(selectedFilter === site.id ? null : site.id)}
                className={`px-3 py-1 rounded-full whitespace-nowrap transition-all text-xs font-medium flex items-center space-x-1.5 ${
                  selectedFilter === site.id
                    ? 'bg-brand-600 text-white font-semibold shadow-sm'
                    : 'bg-white text-slate-600 hover:text-slate-900 hover:bg-slate-100 border border-slate-200'
                }`}
              >
                <span>{site.name}</span>
              </button>
            ))}
          </div>
        )}

      </div>
    </header>
  );
}
