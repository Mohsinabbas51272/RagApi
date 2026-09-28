import React, { useState } from 'react';
import { X, RefreshCw, Database, CheckCircle2, AlertTriangle, Play, Globe } from 'lucide-react';
import { triggerIngest, triggerRebuildIndex } from '../services/api';

export default function AdminModal({ isOpen, onClose, onRefreshData, websites }) {
  const [isIngesting, setIsIngesting] = useState(false);
  const [isRebuilding, setIsRebuilding] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);
  const [selectedTargetSite, setSelectedTargetSite] = useState('all');

  if (!isOpen) return null;

  const handleIngest = async () => {
    setIsIngesting(true);
    setStatusMsg(null);
    try {
      const targets = selectedTargetSite === 'all' ? null : [selectedTargetSite];
      const res = await triggerIngest(targets);
      setStatusMsg({
        type: 'success',
        text: `Successfully crawled & ingested ${res.total_pages_scraped} pages (${res.total_chunks_created} vector chunks) across [${res.websites_processed.join(', ')}] in ${res.duration_seconds}s!`
      });
      onRefreshData();
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Ingestion pipeline error. Ensure backend is running.' });
    } finally {
      setIsIngesting(false);
    }
  };

  const handleRebuild = async () => {
    setIsRebuilding(true);
    setStatusMsg(null);
    try {
      const res = await triggerRebuildIndex();
      setStatusMsg({ type: 'success', text: res.message });
      onRefreshData();
    } catch (err) {
      setStatusMsg({ type: 'error', text: 'Rebuild index error.' });
    } finally {
      setIsRebuilding(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm animate-fadeIn">
      <div className="w-full max-w-lg rounded-2xl bg-white border border-slate-200 p-6 shadow-2xl relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2.5 rounded-xl bg-brand-50 text-brand-700 border border-brand-200">
            <RefreshCw className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-slate-900">Crawler & Data Pipeline Admin</h3>
            <p className="text-xs text-slate-500">Live Web Crawler & Vector Ingestion Controls</p>
          </div>
        </div>

        {/* Target Site Selector */}
        <div className="mb-4 bg-slate-50 p-3 rounded-xl border border-slate-200">
          <label className="text-xs font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
            <Globe className="w-3.5 h-3.5 text-brand-600" />
            <span>Select Crawl Target:</span>
          </label>
          <select
            value={selectedTargetSite}
            onChange={(e) => setSelectedTargetSite(e.target.value)}
            disabled={isIngesting || isRebuilding}
            className="w-full bg-white border border-slate-300 rounded-lg px-3 py-2 text-xs text-slate-900 focus:outline-none focus:border-brand-500"
          >
            <option value="all">All 7 Brillanz Entities (Full Group Ingest)</option>
            {websites && websites.map((site) => (
              <option key={site.id} value={site.id}>
                {site.name} ({site.url})
              </option>
            ))}
          </select>
        </div>

        {/* Action Cards */}
        <div className="space-y-3.5 my-5">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
                <Play className="w-4 h-4 text-emerald-600" />
                <span>POST /ingest (Live Crawler)</span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Visit target domains, extract clean text, and update database.
              </p>
            </div>
            <button
              onClick={handleIngest}
              disabled={isIngesting || isRebuilding}
              className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all shrink-0 ml-3 ${
                isIngesting
                  ? 'bg-slate-200 text-slate-500 cursor-wait'
                  : 'bg-emerald-600 hover:bg-emerald-700 text-white shadow-sm'
              }`}
            >
              {isIngesting ? 'Crawling...' : 'Run Crawler'}
            </button>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
            <div>
              <div className="text-sm font-semibold text-slate-900 flex items-center gap-1.5">
                <Database className="w-4 h-4 text-brand-600" />
                <span>POST /rebuild-index</span>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">
                Re-chunk and update vector embeddings in ChromaDB.
              </p>
            </div>
            <button
              onClick={handleRebuild}
              disabled={isIngesting || isRebuilding}
              className={`px-3.5 py-2 rounded-lg text-xs font-semibold transition-all shrink-0 ml-3 ${
                isRebuilding
                  ? 'bg-slate-200 text-slate-500 cursor-wait'
                  : 'bg-brand-600 hover:bg-brand-700 text-white shadow-sm'
              }`}
            >
              {isRebuilding ? 'Rebuilding...' : 'Rebuild Index'}
            </button>
          </div>
        </div>

        {/* Status Message */}
        {statusMsg && (
          <div
            className={`p-3 rounded-xl mb-4 text-xs flex items-start space-x-2 border leading-relaxed ${
              statusMsg.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                : 'bg-rose-50 text-rose-800 border-rose-200'
            }`}
          >
            {statusMsg.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 shrink-0 mt-0.5 text-emerald-600" />
            ) : (
              <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600" />
            )}
            <span>{statusMsg.text}</span>
          </div>
        )}

        <div className="flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>

      </div>
    </div>
  );
}
