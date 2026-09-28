import React from 'react';
import { Link2, ExternalLink } from 'lucide-react';

export default function SourceCard({ sources }) {
  if (!sources || sources.length === 0) return null;

  // Deduplicate sources by URL
  const seenUrls = new Set();
  const uniqueSources = [];
  sources.forEach((src) => {
    if (!seenUrls.has(src.url)) {
      seenUrls.add(src.url);
      uniqueSources.push(src);
    }
  });

  return (
    <div className="mt-4 pt-3 border-t border-slate-100">
      <div className="text-xs font-semibold text-slate-700 mb-2 flex items-center gap-1.5">
        <span>Sources:</span>
      </div>

      <div className="flex flex-col space-y-1.5 pl-0.5">
        {uniqueSources.map((src, idx) => {
          // Format clean display URL (e.g. softoo.co)
          const cleanUrl = src.url.replace(/^https?:\/\/(www\.)?/, '');
          return (
            <a
              key={idx}
              href={src.url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center space-x-2 text-xs text-brand-600 hover:text-brand-800 hover:underline transition-colors w-fit group"
            >
              <Link2 className="w-3.5 h-3.5 text-slate-400 group-hover:text-brand-600 transition-colors shrink-0" />
              <span className="font-mono font-medium">{cleanUrl}</span>
              <span className="text-slate-400 text-[11px] font-sans">({src.website_name})</span>
              <ExternalLink className="w-3 h-3 text-slate-300 group-hover:text-brand-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </a>
          );
        })}
      </div>
    </div>
  );
}
