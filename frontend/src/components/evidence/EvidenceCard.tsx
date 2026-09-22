import React from 'react';
import { SourceEvidence } from '../../types';
import { FileText, MapPin, Bookmark, Hash } from 'lucide-react';

interface EvidenceCardProps {
  evidence: SourceEvidence;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence }) => {
  return (
    <div className="bg-white border border-slate-200/90 rounded-xl p-4 shadow-subtle space-y-3.5">
      {/* Header Info */}
      <div className="flex items-start justify-between gap-2 border-b border-slate-100 pb-3">
        <div className="flex items-center gap-2 min-w-0">
          <div className="p-1.5 rounded-lg bg-brand-50 text-brand-600 border border-brand-100 shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div className="min-w-0">
            <h4 className="text-xs font-bold text-slate-900 truncate" title={evidence.filename}>
              {evidence.filename}
            </h4>
            <div className="flex items-center gap-1.5 text-[11px] text-slate-500 mt-0.5">
              <span className="flex items-center gap-0.5 font-medium text-slate-700">
                <MapPin className="w-3 h-3 text-brand-500" />
                Page {evidence.page}
              </span>
              {typeof evidence.similarity_score === 'number' && (
                <>
                  <span>•</span>
                  <span>Match: {(evidence.similarity_score * 100).toFixed(0)}%</span>
                </>
              )}
            </div>
          </div>
        </div>

        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 shrink-0">
          {evidence.chunk_id ? evidence.chunk_id.split('-').slice(1).join('-') : '—'}
        </span>
      </div>

      {/* Section info */}
      {evidence.section && (
        <div className="flex items-center gap-1.5 text-xs font-medium text-slate-700 bg-slate-50 px-2.5 py-1.5 rounded-md border border-slate-100">
          <Bookmark className="w-3.5 h-3.5 text-slate-500 shrink-0" />
          <span className="truncate">{evidence.section}</span>
        </div>
      )}

      {/* Verified Excerpt Passage */}
      <div className="space-y-1.5">
        <div className="flex items-center justify-between text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
          <span>Verified Passage Excerpt</span>
          <span className="text-[10px] lowercase text-brand-600 font-normal">verbatim text</span>
        </div>

        <div className="p-3 bg-slate-50/70 border border-slate-200/80 rounded-lg text-xs text-slate-800 leading-relaxed font-mono whitespace-pre-line selection:bg-amber-100 selection:text-amber-900">
          {evidence.evidence}
        </div>
      </div>

      {/* Footer details */}
      <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[10px] text-slate-400">
        <span className="flex items-center gap-1">
          <Hash className="w-3 h-3" />
          <span>Chunk ID: {evidence.chunk_id || '—'}</span>
        </span>
        <span>Local ChromaDB</span>
      </div>
    </div>
  );
};
