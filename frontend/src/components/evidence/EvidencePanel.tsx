import React from 'react';
import { SourceEvidence } from '../../types';
import { EvidenceCard } from './EvidenceCard';
import { ShieldCheck, X, FileSearch } from 'lucide-react';

interface EvidencePanelProps {
  selectedEvidence: SourceEvidence | null;
  onClose: () => void;
  isOpen: boolean;
}

export const EvidencePanel: React.FC<EvidencePanelProps> = ({
  selectedEvidence,
  onClose,
  isOpen,
}) => {
  if (!isOpen) return null;

  return (
    <aside className="w-88 xl:w-96 border-l border-slate-200 bg-white flex flex-col h-full shrink-0 shadow-card z-10 transition-all">
      {/* Panel Header */}
      <div className="h-14 px-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-brand-600" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Evidence Trail
          </h3>
        </div>

        <button
          onClick={onClose}
          className="p-1.5 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
          title="Close Evidence Panel"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      {/* Panel Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {selectedEvidence ? (
          <div className="space-y-4">
            <div className="text-xs text-slate-500 leading-relaxed bg-brand-50 border border-brand-200 rounded-lg p-3">
              <strong className="text-brand-900">Evidence-First Guarantee:</strong> Every cited fact is extracted directly from the page and section below.
            </div>

            <EvidenceCard evidence={selectedEvidence} />
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-3 select-none">
            <div className="w-12 h-12 rounded-full bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400">
              <FileSearch className="w-6 h-6" />
            </div>
            <div className="space-y-1">
              <p className="text-xs font-semibold text-slate-700">No source selected</p>
              <p className="text-[11px] text-slate-500 leading-relaxed">
                Click <strong className="text-slate-700">[View evidence]</strong> on any answer source card to inspect page-level evidence snippets.
              </p>
            </div>
          </div>
        )}
      </div>
    </aside>
  );
};