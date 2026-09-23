import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';

interface DocumentUploadProps {
  onUpload: (file: File) => Promise<{ success: boolean; message: string }>;
  isUploading: boolean;
  uploadProgress: string | null;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUpload,
  isUploading,
  uploadProgress,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = async (file: File) => {
    setFeedback(null);
    const res = await onUpload(file);
    setFeedback({
      type: res.success ? 'success' : 'error',
      message: res.message,
    });
    setTimeout(() => {
      setFeedback(null);
    }, 4500);
  };

  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      await processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await processFile(e.target.files[0]);
      e.target.value = '';
    }
  };

  return (
    <div className="w-full">
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !isUploading && fileInputRef.current?.click()}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-4 transition-all duration-200 text-center cursor-pointer flex flex-col items-center justify-center gap-2 select-none bg-slate-50 hover:-translate-y-0.5',
          isDragging
            ? 'border-brand-500 bg-brand-50 scale-[0.99] shadow-card'
            : 'border-slate-200 bg-slate-50 hover:border-brand-400 hover:bg-brand-50/50 hover:shadow-glow-blue',
          isUploading && 'opacity-80 cursor-wait pointer-events-none'
        )}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          onChange={handleFileChange}
          className="hidden"
          disabled={isUploading}
        />

        <div className="w-10 h-10 rounded-full bg-brand-50 border border-brand-200 flex items-center justify-center text-brand-600 mb-0.5 transition-colors">
          <UploadCloud className="w-5 h-5" />
        </div>

        <div>
          <p className="text-xs font-semibold text-slate-800">
            {isUploading ? 'Processing document...' : 'Upload business documents'}
          </p>
          <p className="text-[11px] text-slate-500 mt-0.5">
            Drag & drop PDF or TXT (Max 10MB)
          </p>
        </div>

        {isUploading && (
          <div className="w-full mt-2">
            <div className="flex items-center justify-center gap-2 text-xs text-brand-700 font-medium animate-pulse mb-1.5">
              <FileText className="w-3.5 h-3.5" />
              <span>{uploadProgress || 'Extracting pages & local embeddings...'}</span>
            </div>
            <div className="w-full h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-brand-600 rounded-full animate-indeterminate" />
            </div>
          </div>
        )}
      </div>

      {feedback && (
        <div
          className={cn(
            'mt-2.5 px-3 py-2 rounded-lg border text-xs flex items-center gap-2 transition-all',
            feedback.type === 'success'
              ? 'bg-emerald-50 border-emerald-200 text-emerald-800'
              : 'bg-rose-50 border-rose-200 text-rose-800'
          )}
        >
          {feedback.type === 'success' ? (
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
          ) : (
            <AlertCircle className="w-3.5 h-3.5 text-rose-600 shrink-0" />
          )}
          <span className="truncate">{feedback.message}</span>
        </div>
      )}
    </div>
  );
};