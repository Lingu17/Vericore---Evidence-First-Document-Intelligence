import React, { useState, useRef, useEffect } from 'react';
import { ArrowUp, CornerDownLeft } from 'lucide-react';
import { cn } from '../../lib/utils';

interface QueryInputProps {
  onSend: (question: string) => void;
  isLoading: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export const QueryInput: React.FC<QueryInputProps> = ({
  onSend,
  isLoading,
  disabled = false,
  placeholder = 'Ask a question across your indexed documents...',
}) => {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  }, [query]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading || disabled) return;
    onSend(query);
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full relative bg-white border border-slate-200 focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-100 rounded-2xl shadow-card hover:shadow-dropdown transition-all duration-200">
      <form onSubmit={handleSubmit} className="flex items-center px-4 py-2.5">
        <textarea
          ref={textareaRef}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled || isLoading}
          rows={1}
          className="w-full resize-none outline-none text-sm text-slate-900 placeholder:text-slate-400 bg-transparent max-h-28 pr-2 disabled:cursor-not-allowed"
        />

        <div className="flex items-center gap-2 shrink-0">
          <button
            type="submit"
            disabled={!query.trim() || isLoading || disabled}
            aria-label="Send question"
            className={cn(
              'h-8 w-8 rounded-xl flex items-center justify-center transition-all duration-200',
              query.trim() && !isLoading && !disabled
                ? 'bg-brand-600 hover:bg-brand-700 text-white shadow-card hover:shadow-lift'
                : 'bg-slate-100 text-slate-400 cursor-not-allowed'
            )}
          >
            <ArrowUp className="w-4 h-4" />
          </button>
        </div>
      </form>

      <div className="flex items-center justify-between px-4 pb-2 pt-0.5 text-[11px] text-slate-400 border-t border-slate-100">
        <span className="flex items-center gap-1">
          <CornerDownLeft className="w-3 h-3 opacity-70" />
          <span>Press <strong className="text-slate-600">Enter</strong> to ask</span>
        </span>
        <span>Evidence-first verification</span>
      </div>
    </div>
  );
};