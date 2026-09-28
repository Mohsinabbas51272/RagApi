import React, { useState, useEffect } from 'react';
import { Database, Search, Filter, ExternalLink, Bookmark, Layers, FileText, CheckCircle } from 'lucide-react';
import { fetchChunks } from '../services/api';

export default function ChunkExplorer({ websites, onAskAboutChunk }) {
  const [chunks, setChunks] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [selectedSite, setSelectedSite] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const loadChunks = async () => {
    setIsLoading(true);
    try {
      const data = await fetchChunks(selectedSite || null, 60);
      setChunks(data.chunks || []);
      setTotalCount(data.total_chunks || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadChunks();
  }, [selectedSite]);

  const filteredChunks = chunks.filter((ch) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    return (
      ch.text.toLowerCase().includes(q) ||
      ch.metadata?.title?.toLowerCase().includes(q) ||
      ch.metadata?.website_name?.toLowerCase().includes(q) ||
      ch.chunk_id.toLowerCase().includes(q)
    );
  });

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      
      {/* Top Header Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="w-12 h-12 rounded-xl bg-brand-50 border border-brand-200 flex items-center justify-center shadow-sm">
            <Database className="w-6 h-6 text-brand-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
              <span>Knowledge Base Chunk Explorer</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                {totalCount} Active Vectors
              </span>
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Inspect semantic text windows and metadata stored in the vector database
            </p>
          </div>
        </div>

        {/* Filter & Search Bar */}
        <div className="flex flex-col sm:flex-row items-center gap-3">
          {/* Site Filter Dropdown */}
          <div className="relative w-full sm:w-48">
            <select
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-xl px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-brand-500 focus:bg-white appearance-none pr-8 cursor-pointer font-medium"
            >
              <option value="">All Companies (7)</option>
              {websites.map((w) => (
                <option key={w.id} value={w.id}>{w.name}</option>
              ))}
            </select>
            <Filter className="w-3.5 h-3.5 text-slate-400 absolute right-3 top-2.5 pointer-events-none" />
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search in chunks..."
              className="w-full bg-slate-50 border border-slate-300 rounded-xl pl-8 pr-3 py-2 text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:border-brand-500 focus:bg-white"
            />
          </div>
        </div>
      </div>

      {/* Chunks Grid */}
      {isLoading ? (
        <div className="flex items-center justify-center py-20 text-slate-500 text-xs">
          <div className="animate-spin w-6 h-6 border-2 border-brand-600 border-t-transparent rounded-full mr-3"></div>
          Loading vector index chunks...
        </div>
      ) : filteredChunks.length === 0 ? (
        <div className="bg-white p-12 text-center rounded-2xl border border-slate-200">
          <FileText className="w-10 h-10 text-slate-400 mx-auto mb-3 opacity-60" />
          <p className="text-sm font-semibold text-slate-700">No matching chunks found</p>
          <p className="text-xs text-slate-500 mt-1">Try adjusting your search query or company filter</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredChunks.map((ch) => (
            <div
              key={ch.chunk_id}
              className="p-5 rounded-2xl bg-white border border-slate-200 hover:border-brand-400 transition-all flex flex-col justify-between group shadow-sm hover:shadow"
            >
              <div>
                {/* Chunk Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <span className="text-[11px] font-bold px-2 py-0.5 rounded-md bg-brand-50 text-brand-700 border border-brand-200">
                      {ch.metadata?.website_name || 'Brillanz'}
                    </span>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {ch.chunk_id}
                    </span>
                  </div>

                  <a
                    href={ch.metadata?.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 rounded text-slate-400 hover:text-slate-800 hover:bg-slate-100 transition-colors"
                    title="Open Source URL"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                {/* Page Title */}
                <h4 className="text-xs font-semibold text-slate-900 group-hover:text-brand-700 transition-colors mb-2">
                  {ch.metadata?.title}
                </h4>

                {/* Chunk Text */}
                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-200 font-sans line-clamp-4">
                  "{ch.text}"
                </p>
              </div>

              {/* Chunk Footer */}
              <div className="mt-3 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <div className="flex items-center space-x-3">
                  <span>{ch.character_count} chars</span>
                  <span>•</span>
                  <span>Category: {ch.metadata?.category || 'General'}</span>
                </div>

                <button
                  onClick={() => onAskAboutChunk(ch.text.slice(0, 80), ch.metadata?.website_id)}
                  className="text-brand-600 hover:text-brand-800 font-semibold transition-colors"
                >
                  Ask AI About This →
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
