import React from 'react';
import { Link } from 'react-router-dom';
import { PanelRight, Trash2, Cpu, Menu } from 'lucide-react';
import { HealthResponse } from '../../types';
import { cn } from '../../lib/utils';

interface HeaderProps {
  health: HealthResponse | null;
  onToggleSidebar: () => void;
  onToggleEvidence: () => void;
  isEvidenceOpen: boolean;
  onClearChat: () => void;
  hasMessages: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  health,
  onToggleSidebar,
  onToggleEvidence,
  isEvidenceOpen,
  onClearChat,
  hasMessages,
}) => {
  return (
    <header className="h-14 border-b border-slate-200 bg-white px-4 lg:px-6 flex items-center justify-between shrink-0 z-20">
      {/* Brand & Tagline */}
      <div className="flex items-center gap-3">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 -ml-1 text-slate-500 hover:bg-slate-100 hover:text-slate-700 rounded-lg transition-colors"
          title="Toggle Knowledge Workspace"
        >
          <Menu className="w-4 h-4" />
        </button>
        <Link
          to="/"
          aria-label="Go to Vericore home"
          className="flex items-center gap-2.5 -m-1 p-1 rounded-lg cursor-pointer transition-colors duration-150 hover:bg-slate-100 group"
        >
          <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center text-white shadow-card font-bold text-base transition-colors duration-150 group-hover:bg-brand-700">
            V
          </div>
          <div className="flex items-baseline gap-2.5">
            <h1 className="text-base font-bold text-slate-900 tracking-tight">
              Vericore
            </h1>
            <span className="hidden sm:inline-block text-xs text-slate-500 font-medium">
              Evidence-First Document Intelligence
            </span>
          </div>
        </Link>
      </div>

      {/* System Status & Actions */}
      <div className="flex items-center gap-3">
        {/* System Health Status */}
        <div className="hidden md:flex items-center gap-2 px-2.5 py-1 rounded-full bg-slate-50 border border-slate-200 text-[11px] text-slate-600 shadow-subtle">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          <span>Local Embeddings: MiniLM-L6-v2</span>
          <span className="text-slate-300">•</span>
          <span className="flex items-center gap-1 text-slate-600">
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
          className={cn(
            'p-2 rounded-lg border transition-all duration-200 text-xs font-medium flex items-center gap-1.5 shadow-subtle',
            isEvidenceOpen
              ? 'bg-brand-50 border-brand-300 text-brand-700 shadow-card'
              : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 hover:text-slate-800'
          )}
          title="Toggle Evidence Trail Panel"
        >
          <PanelRight className="w-4 h-4" />
          <span className="hidden sm:inline">Evidence Trail</span>
        </button>
      </div>
    </header>
  );
};