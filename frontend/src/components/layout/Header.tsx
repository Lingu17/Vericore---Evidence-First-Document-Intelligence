import React from 'react';
import { PanelRight, Trash2, Cpu } from 'lucide-react';
import { HealthResponse } from '../../types';

interface HeaderProps {
  health: HealthResponse | null;
  onToggleEvidence: () => void;
  isEvidenceOpen: boolean;
  onClearChat: () => void;
  hasMessages: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onToggleEvidence,
  isEvidenceOpen,
  onClearChat,
  hasMessages,
}) => {
  return (
    <header className="h-14 border-b border-slate-200/90 bg-white px-4 lg:px-6 flex items-center justify-between shrink-0 shadow-xs z-20">
      {/* Brand & Tagline */}
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white shadow-sm font-bold text-base">
          D
        </div>
        <div className="flex items-baseline gap-2.5">
          <h1 className="text-sm font-bold text-slate-900 tracking-tight">
            DocuPilot
          </h1>
          <span className="hidden sm:inline-block text-xs text-slate-500 font-medium">
            Evidence-First Document Intelligence
          </span>
        </div>
      </div>

      {/* System Status & Actions */}
      <div className="flex items-center gap-3">
        {/* System Health Status */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200/80 text-[11px] text-slate-600">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Local Embeddings: MiniLM-L6-v2</span>
          <span>•</span>
          <span className="flex items-center gap-1 text-slate-500">
            <Cpu className="w-3 h-3 text-brand-600" />
            {health?.llm_provider || 'Groq Engine'}
          </span>
        </div>

        {hasMessages && (
          <button
            onClick={onClearChat}
            className="text-xs text-slate-500 hover:text-slate-800 px-2.5 py-1.5 rounded-lg hover:bg-slate-100 transition-colors flex items-center gap-1.5"
            title="Reset conversation"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Reset chat</span>
          </button>
        )}

        {/* Evidence Panel Toggle */}
        <button
          onClick={onToggleEvidence}
          className={`p-2 rounded-lg border transition-all text-xs font-medium flex items-center gap-1.5 ${
            isEvidenceOpen
              ? 'bg-brand-50 border-brand-300 text-brand-700'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
          }`}
          title="Toggle Evidence Trail Panel"
        >
          <PanelRight className="w-4 h-4" />
          <span className="hidden sm:inline">Evidence Trail</span>
        </button>
      </div>
    </header>
  );
};
