import React from 'react';
import { AlertCircle, CheckCircle2, Info, X } from 'lucide-react';
import { cn } from '../../lib/utils';

interface ToastProps {
  type?: 'success' | 'error' | 'info';
  message: string;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({
  type = 'info',
  message,
  onClose,
}) => {
  const styles = {
    success: 'bg-emerald-50 border-emerald-300 text-emerald-900',
    error: 'bg-rose-50 border-rose-300 text-rose-900',
    info: 'bg-brand-50 border-brand-300 text-brand-900',
  };

  const icons = {
    success: <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />,
    error: <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />,
    info: <Info className="w-4 h-4 text-brand-600 shrink-0" />,
  };

  return (
    <div
      className={cn(
        'flex items-center justify-between gap-3 px-4 py-2.5 rounded-lg border shadow-md text-xs sm:text-sm font-medium transition-all',
        styles[type]
      )}
    >
      <div className="flex items-center gap-2">
        {icons[type]}
        <span>{message}</span>
      </div>
      <button
        onClick={onClose}
        className="p-1 hover:bg-black/5 rounded transition-colors text-slate-500 hover:text-slate-800"
      >
        <X className="w-3.5 h-3.5" />
      </button>
    </div>
  );
};
