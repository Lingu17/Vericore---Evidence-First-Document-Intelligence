import React from 'react';
import { DocumentItem } from '../../types';
import { DocumentUpload } from '../documents/DocumentUpload';
import { DocumentList } from '../documents/DocumentList';
import { Layers, Database, Shield } from 'lucide-react';

interface SidebarProps {
  documents: DocumentItem[];
  selectedDocId: string | null;
  onSelectDoc: (docId: string | null) => void;
  onDeleteDoc: (docId: string) => void;
  onClearAll: () => void;
  onUpload: (file: File) => Promise<{ success: boolean; message: string }>;
  isUploading: boolean;
  uploadProgress: string | null;
}

export const Sidebar: React.FC<SidebarProps> = ({
  documents,
  selectedDocId,
  onSelectDoc,
  onDeleteDoc,
  onClearAll,
  onUpload,
  isUploading,
  uploadProgress,
}) => {
  const totalPages = documents.reduce((acc, d) => acc + d.pages, 0);
  const totalChunks = documents.reduce((acc, d) => acc + d.chunks, 0);

  return (
    <aside className="w-72 lg:w-80 border-r border-slate-200/90 bg-white flex flex-col h-full shrink-0 shadow-subtle select-none">
      {/* Workspace Header */}
      <div className="p-4 border-b border-slate-200/90 flex items-center justify-between bg-slate-50/50">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-brand-600" />
          <h2 className="text-xs font-bold uppercase tracking-wider text-slate-800">
            Knowledge Workspace
          </h2>
        </div>
        <span className="text-[11px] font-medium text-slate-500">
          {documents.length} {documents.length === 1 ? 'doc' : 'docs'}
        </span>
      </div>

      {/* Sidebar Content (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5">
        {/* Upload Zone */}
        <DocumentUpload
          onUpload={onUpload}
          isUploading={isUploading}
          uploadProgress={uploadProgress}
        />

        {/* Document List */}
        <DocumentList
          documents={documents}
          selectedDocId={selectedDocId}
          onSelectDoc={onSelectDoc}
          onDeleteDoc={onDeleteDoc}
          onClearAll={onClearAll}
        />
      </div>

      {/* Workspace Footer Stats */}
      <div className="p-3.5 border-t border-slate-200/90 bg-slate-50/70 text-[11px] text-slate-600 space-y-2">
        <div className="flex items-center justify-between font-medium">
          <span className="flex items-center gap-1 text-slate-500">
            <Database className="w-3.5 h-3.5 text-brand-600" />
            Indexed Knowledge
          </span>
          <span className="font-mono text-slate-800 font-semibold">
            {totalPages}p • {totalChunks} chunks
          </span>
        </div>

        <div className="flex items-center gap-1 text-[10px] text-slate-400">
          <Shield className="w-3 h-3 text-emerald-600" />
          <span>Local ChromaDB persistence</span>
        </div>
      </div>
    </aside>
  );
};
