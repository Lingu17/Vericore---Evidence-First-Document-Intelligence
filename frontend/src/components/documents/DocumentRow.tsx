import React from 'react';
import { DocumentItem } from '../../types';
import { FileText, Trash2, CheckCircle2 } from 'lucide-react';
import { cn } from '../../lib/utils';

interface DocumentRowProps {
  document: DocumentItem;
  isSelected: boolean;
  onSelect: (docId: string) => void;
  onDelete: (docId: string) => void;
}

export const DocumentRow: React.FC<DocumentRowProps> = ({
  document,
  isSelected,
  onSelect,
  onDelete,
}) => {
  const isPdf = document.file_type === 'pdf' || document.filename.endsWith('.pdf');

  return (
    <div
      onClick={() => onSelect(document.document_id)}
      className={cn(
        'group relative flex items-start gap-2.5 p-2.5 rounded-lg border transition-all duration-200 cursor-pointer select-none shadow-subtle hover:-translate-y-px',
        isSelected
          ? 'bg-brand-50/80 border-brand-300 ring-1 ring-brand-200 shadow-card'
          : 'bg-white border-slate-200 hover:border-brand-300 hover:bg-brand-50/40 hover:shadow-card'
      )}
    >
      {/* File type badge icon */}
      <div
        className={cn(
          'p-1.5 rounded-md shrink-0 flex items-center justify-center',
          isPdf ? 'bg-rose-50 text-rose-600 border border-rose-200' : 'bg-sky-50 text-sky-600 border border-sky-200'
        )}
      >
        <FileText className="w-4 h-4" />
      </div>

      <div className="flex-1 min-w-0 pr-6">
        <p className="text-xs font-semibold text-slate-800 truncate leading-tight" title={document.filename}>
          {document.filename}
        </p>
        <div className="flex items-center gap-1.5 mt-1 text-[11px] text-slate-500">
          <span>{document.pages} {document.pages === 1 ? 'page' : 'pages'}</span>
          <span>•</span>
          <span>{document.chunks} chunks</span>
        </div>
        <div className="flex items-center gap-1 mt-1 text-[10px] text-emerald-700 font-medium">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span>Indexed</span>
        </div>
      </div>

      {/* Delete button */}
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete(document.document_id);
        }}
        title="Remove document"
        className="opacity-0 group-hover:opacity-100 focus:opacity-100 absolute top-2 right-2 p-1 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded transition-all"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};