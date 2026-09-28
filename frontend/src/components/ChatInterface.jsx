import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles, Clock, Copy, Check, ArrowRight, Trash2, Download, ShieldCheck } from 'lucide-react';
import SourceCard from './SourceCard';

const SAMPLE_QUESTIONS = [
  "What services does Softoo provide for engineering teams?",
  "How does OKO Insights use AI computer vision for crowd intelligence?",
  "What can YaniPro autonomous AI agents do for compliance workflows?",
  "What smart city & theft resistance solutions does Cratus offer in the UK?",
  "How does Thunder Energy AI optimize battery storage and grid renewables?",
  "What cybersecurity & penetration testing services does Scorpbit provide?"
];

// Rich Markdown / Text Formatter for clean display without raw asterisks
function FormattedMessage({ text }) {
  if (!text) return null;

  // Clean out any inline bracket numbers like [1], [2], [1, 2]
  const cleanText = text.replace(/\s*\[\d+(?:,\s*\d+)*\]/g, '');
  const lines = cleanText.split('\n');

  const renderInline = (str) => {
    // Parse bold: **text**
    const parts = [];
    const boldRegex = /\*\*(.*?)\*\*/g;
    let lastIndex = 0;
    let match;

    while ((match = boldRegex.exec(str)) !== null) {
      if (match.index > lastIndex) {
        parts.push(str.substring(lastIndex, match.index));
      }
      parts.push(
        <strong key={`bold-${match.index}`} className="font-semibold text-slate-900">
          {match[1]}
        </strong>
      );
      lastIndex = match.index + match[0].length;
    }
    if (lastIndex < str.length) {
      parts.push(str.substring(lastIndex));
    }

    return parts;
  };

  return (
    <div className="space-y-2 text-sm leading-relaxed text-slate-800">
      {lines.map((line, idx) => {
        const trimmed = line.trim();
        if (!trimmed) {
          return <div key={idx} className="h-1.5" />;
        }

        // Check if line is a bullet item (starts with * , - , • )
        const bulletMatch = trimmed.match(/^[\*\-\•]\s*(.*)$/);
        if (bulletMatch) {
          const content = bulletMatch[1];
          return (
            <div key={idx} className="flex items-start space-x-2 pl-1 my-1">
              <span className="text-brand-600 font-bold text-base leading-none select-none mt-0.5">•</span>
              <div className="flex-1 leading-relaxed">{renderInline(content)}</div>
            </div>
          );
        }

        return (
          <p key={idx} className="leading-relaxed">
            {renderInline(line)}
          </p>
        );
      })}
    </div>
  );
}

export default function ChatInterface({ messages, onSendMessage, isLoading, selectedFilter, onClearMessages }) {
  const [input, setInput] = useState('');
  const [copiedIdx, setCopiedIdx] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSendMessage(input.trim());
    setInput('');
  };

  const handleQuickQuestion = (q) => {
    onSendMessage(q);
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedIdx(idx);
    setTimeout(() => setCopiedIdx(null), 2000);
  };

  const exportConversation = () => {
    if (messages.length === 0) return;
    let md = "# Brillanz Group Intelligence - Conversation Log\n\n";
    messages.forEach((m) => {
      const sender = m.sender === 'user' ? '### User' : '### Brillanz AI Assistant';
      md += `${sender}\n${m.text}\n\n`;
      if (m.sources && m.sources.length > 0) {
        md += "**Sources:**\n";
        m.sources.forEach((s) => {
          md += `- [${s.website_name} - ${s.title}](${s.url})\n`;
        });
        md += "\n";
      }
    });
    const blob = new Blob([md], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `brillanz-chat-${new Date().toISOString().slice(0,10)}.md`;
    a.click();
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8.5rem)] max-w-5xl mx-auto px-4 sm:px-6 py-4">
      
      {/* Top Header Actions (Clear / Export) */}
      {messages.length > 0 && (
        <div className="flex items-center justify-between pb-2 mb-2 border-b border-slate-200 text-xs text-slate-500">
          <span className="flex items-center gap-1.5 font-semibold text-slate-700">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            <span>Grounded Dialogue ({messages.length} messages)</span>
          </span>
          <div className="flex items-center space-x-2">
            <button
              onClick={exportConversation}
              className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white hover:bg-slate-100 text-slate-700 transition-colors border border-slate-200 text-[11px] font-medium shadow-sm"
              title="Export to Markdown"
            >
              <Download className="w-3 h-3 text-slate-500" />
              <span>Export</span>
            </button>
            <button
              onClick={onClearMessages}
              className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-white hover:bg-rose-50 text-slate-600 hover:text-rose-600 transition-colors border border-slate-200 text-[11px] font-medium shadow-sm"
              title="Clear Conversation"
            >
              <Trash2 className="w-3 h-3" />
              <span>Clear</span>
            </button>
          </div>
        </div>
      )}

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto space-y-6 pr-2 mb-4 scrollbar-thin">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center max-w-2xl mx-auto py-8">
            <div className="w-14 h-14 rounded-2xl bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center mb-4 shadow-xl glow-brand">
              <Sparkles className="w-7 h-7 text-white" />
            </div>
            <h2 className="text-2xl font-bold text-slate-900 mb-2">Brillanz Enterprise AI Assistant</h2>
            <p className="text-slate-600 text-sm mb-6 leading-relaxed">
              Ask any question across our 7 portfolio companies: <span className="text-slate-900 font-semibold">Softoo, OKO Insights, YaniPro, Cratus, SC Tech Global, Thunder Energy AI, and Scorpbit</span>.
            </p>

            {/* Quick Prompts */}
            <div className="w-full text-left">
              <div className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-brand-600" /> Suggested Inquiries:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {SAMPLE_QUESTIONS.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => handleQuickQuestion(q)}
                    className="p-3.5 rounded-xl bg-white hover:bg-brand-50/50 border border-slate-200 hover:border-brand-400 text-left text-xs font-medium text-slate-700 hover:text-brand-900 transition-all flex items-center justify-between group shadow-sm hover:shadow"
                  >
                    <span>{q}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-brand-600 transition-colors shrink-0 ml-2" />
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex items-start space-x-3.5 ${
                msg.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.sender === 'assistant' && (
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center shrink-0 shadow-md">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-2xl p-4 transition-all ${
                  msg.sender === 'user'
                    ? 'bg-brand-600 text-white shadow-md'
                    : 'bg-white text-slate-800 border border-slate-200 shadow-sm'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-2 pb-1.5 border-b border-slate-100">
                  <div className="flex items-center space-x-2">
                    <span className={`font-semibold flex items-center space-x-1.5 ${
                      msg.sender === 'user' ? 'text-white/90 text-xs' : 'text-slate-900 text-sm font-bold'
                    }`}>
                      {msg.sender === 'user'
                        ? 'You'
                        : (msg.sources && msg.sources.length > 0 ? msg.sources[0].website_name : 'Brillanz Intelligence')
                      }
                    </span>
                    {msg.sender === 'assistant' && msg.sources && msg.sources.length > 0 && (
                      <span className="text-[10px] px-2 py-0.5 rounded-full bg-brand-50 text-brand-700 font-semibold border border-brand-200">
                        Portfolio Entity
                      </span>
                    )}
                  </div>
                  {msg.processingTime && (
                    <span className={`text-[11px] flex items-center space-x-1 ${
                      msg.sender === 'user' ? 'text-white/75' : 'text-slate-500'
                    }`}>
                      <Clock className="w-3 h-3" />
                      <span>{msg.processingTime} ms</span>
                    </span>
                  )}
                </div>

                {msg.sender === 'user' ? (
                  <div className="text-sm leading-relaxed whitespace-pre-wrap">
                    {msg.text}
                  </div>
                ) : (
                  <FormattedMessage text={msg.text} />
                )}

                {/* Grounded Source References */}
                {msg.sources && msg.sources.length > 0 && (
                  <SourceCard sources={msg.sources} />
                )}

                {msg.sender === 'assistant' && (
                  <div className="mt-3 pt-2 flex items-center justify-end space-x-2 border-t border-slate-100">
                    <button
                      onClick={() => copyToClipboard(msg.text, idx)}
                      className="p-1 px-2 rounded text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors text-xs flex items-center space-x-1"
                      title="Copy response"
                    >
                      {copiedIdx === idx ? (
                        <>
                          <Check className="w-3.5 h-3.5 text-emerald-600" />
                          <span className="text-[11px] text-emerald-600 font-medium">Copied</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-3.5 h-3.5" />
                          <span className="text-[11px]">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
              </div>

              {msg.sender === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-700 flex items-center justify-center shrink-0 shadow-md">
                  <User className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          ))
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex items-start space-x-3.5 justify-start">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-600 flex items-center justify-center shrink-0 animate-pulse shadow-md">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-white p-4 rounded-2xl border border-slate-200 flex items-center space-x-3 text-xs text-slate-600 shadow-sm">
              <div className="flex space-x-1">
                <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 rounded-full bg-brand-600 animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
              <span className="font-medium">Searching vector database & generating response...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center bg-white rounded-2xl border border-slate-300 focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-100 shadow-sm transition-all">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              selectedFilter
                ? `Ask about ${selectedFilter.toUpperCase()}...`
                : "Ask anything about Brillanz Group (Softoo, OKO Insights, YaniPro, Cratus...)"
            }
            disabled={isLoading}
            className="w-full bg-transparent px-4 py-3.5 text-sm text-slate-900 placeholder-slate-400 focus:outline-none rounded-2xl pr-14"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`absolute right-2 p-2.5 rounded-xl transition-all ${
              input.trim() && !isLoading
                ? 'bg-brand-600 text-white shadow-md hover:bg-brand-700 cursor-pointer'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <div className="flex items-center justify-between text-[11px] text-slate-500 px-2 mt-1.5">
          <span>Grounding Engine: Gemini AI + Vector Store</span>
          <span>Press Enter ↵ to send</span>
        </div>
      </form>

    </div>
  );
}
