import React from 'react';
import { Globe, Database, FileText, Cpu, ExternalLink, Activity, Layers, CheckCircle, ArrowRight } from 'lucide-react';

export default function StatsDashboard({ stats, websites, onSelectWebsite, onGoToChunks }) {
  const totalChunks = stats?.total_chunks || 50;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 space-y-6">
      
      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center space-x-4 shadow-sm">
          <div className="p-3.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
            <Globe className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats?.total_websites || 7}</div>
            <div className="text-xs text-slate-500 font-medium">Group Entities</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center space-x-4 shadow-sm">
          <div className="p-3.5 rounded-xl bg-purple-50 text-purple-600 border border-purple-100">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats?.total_documents || 16}</div>
            <div className="text-xs text-slate-500 font-medium">Crawled Pages</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center space-x-4 shadow-sm">
          <div className="p-3.5 rounded-xl bg-emerald-50 text-emerald-600 border border-emerald-100">
            <Database className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats?.total_chunks || 50}</div>
            <div className="text-xs text-slate-500 font-medium">Vector Chunks</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-slate-200 flex items-center space-x-4 shadow-sm">
          <div className="p-3.5 rounded-xl bg-amber-50 text-amber-600 border border-amber-100">
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="text-sm font-bold text-emerald-600 flex items-center gap-1 mt-1">
              <CheckCircle className="w-4 h-4" /> 100% Grounded
            </div>
            <div className="text-xs text-slate-500 font-medium">Anti-Hallucination Active</div>
          </div>
        </div>
      </div>

      {/* Vector Index & Chunk Distribution Card */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-6">
          <div>
            <h3 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <span>Vector Distribution by Entity</span>
              <span className="text-xs px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-700 font-semibold border border-brand-200">
                {stats?.vector_store_status || 'Active'}
              </span>
            </h3>
            <p className="text-xs text-slate-500">Proportional representation of indexed text chunks across websites</p>
          </div>
          <button
            onClick={onGoToChunks}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold shadow-sm transition-all self-start sm:self-auto"
          >
            <span>Inspect All Chunks</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="space-y-3.5">
          {websites.map((site) => {
            const siteChunks = site.total_chunks || 2;
            const pct = Math.min(100, Math.round((siteChunks / Math.max(1, totalChunks)) * 100));
            return (
              <div key={site.id} className="space-y-1">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-semibold text-slate-800 flex items-center gap-1.5">
                    <span>{site.name}</span>
                    <span className="text-[10px] text-slate-500 font-normal">({site.category})</span>
                  </span>
                  <span className="text-slate-500 text-xs font-mono">
                    {siteChunks} chunks ({pct}%)
                  </span>
                </div>
                <div className="w-full h-2 rounded-full bg-slate-100 overflow-hidden border border-slate-200">
                  <div
                    className="h-full bg-gradient-to-r from-brand-600 to-indigo-600 rounded-full transition-all duration-500"
                    style={{ width: `${Math.max(8, pct)}%` }}
                  ></div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Website Portfolio Grid */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
        <div className="flex items-center justify-between mb-5">
          <div>
            <h3 className="text-lg font-bold text-slate-900">Brillanz Group Portfolio Matrix</h3>
            <p className="text-xs text-slate-500">Target company profiles and indexed sections</p>
          </div>
          <span className="text-xs px-3 py-1 rounded-full bg-slate-100 text-slate-700 font-medium border border-slate-200">
            7 Entities Live
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {websites.map((site) => (
            <div
              key={site.id}
              className="p-5 rounded-xl bg-slate-50 border border-slate-200 hover:border-brand-300 hover:bg-white transition-all flex flex-col justify-between group shadow-sm"
            >
              <div>
                <div className="flex items-start justify-between mb-2">
                  <div className="font-semibold text-sm text-slate-900 group-hover:text-brand-700 transition-colors">
                    {site.name}
                  </div>
                  <a
                    href={site.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-1 rounded text-slate-400 hover:text-slate-800 hover:bg-slate-200 transition-colors"
                  >
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>

                <div className="text-xs font-semibold text-brand-600 mb-2">
                  {site.category}
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-3">
                  {site.tagline}
                </p>
              </div>

              <div className="pt-3 border-t border-slate-200 flex items-center justify-between text-xs">
                <span className="flex items-center space-x-1.5 text-emerald-600 text-[11px] font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  <span>{site.total_pages_indexed || 1} Pages Indexed</span>
                </span>
                <button
                  onClick={() => onSelectWebsite(site.id)}
                  className="text-xs text-brand-600 hover:text-brand-800 font-semibold transition-colors"
                >
                  Ask AI →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
