import React from 'react';
import { DocumentItem } from '../../types';
import { DocumentRow } from './DocumentRow';
import { Layers, Trash2 } from 'lucide-react';

interface DocumentListProps {
  documents: DocumentItem[];
  selectedDocId: string | null;
  onSelectDoc: (docId: string | null) => void;
  onDeleteDoc: (docId: string) => void;
  onClearAll: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onDeleteDoc,
  onClearAll,
}) => {
  if (documents.length === 0) {
    return (
      <div className="py-6 px-3 text-center border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
        <Layers className="w-6 h-6 text-slate-400 mx-auto mb-1.5" />
        <p className="text-xs font-semibold text-slate-700">No documents indexed</p>
        <p className="text-[11px] text-slate-500 mt-0.5">
          Upload PDF or TXT files above to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-2.5">
      <div className="flex items-center justify-between px-0.5">
        <div className="flex items-center gap-1.5">
          <span className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
            Documents
          </span>
          <span className="px-1.5 py-0.2 rounded-full bg-slate-100 text-[10px] font-bold text-slate-600">
            {documents.length}
          </span>
        </div>

        {documents.length > 0 && (
          <button
            onClick={onClearAll}
            title="Clear all indexed documents"
            className="text-[11px] text-slate-500 hover:text-rose-600 flex items-center gap-1 transition-colors"
          >
            <Trash2 className="w-3 h-3" />
            <span>Clear all</span>
          </button>
        )}
      </div>

      {/* Filter indicator */}
      {selectedDocId && (
        <div className="flex items-center justify-between px-2.5 py-1.5 bg-brand-50 border border-brand-200 rounded-md text-xs text-brand-900">
          <span className="truncate font-medium">
            Filtering by selected document
          </span>
          <button
            onClick={() => onSelectDoc(null)}
            className="text-[11px] font-semibold text-brand-600 hover:underline shrink-0 ml-2"
          >
            View all
          </button>
        </div>
      )}

      {/* Documents items */}
      <div className="space-y-2 max-h-[380px] overflow-y-auto pr-0.5">
        {documents.map((doc) => (
          <DocumentRow
            key={doc.document_id}
            document={doc}
            isSelected={selectedDocId === doc.document_id}
            onSelect={(id) => onSelectDoc(selectedDocId === id ? null : id)}
            onDelete={onDeleteDoc}
          />
        ))}
      </div>
    </div>
  );
};
