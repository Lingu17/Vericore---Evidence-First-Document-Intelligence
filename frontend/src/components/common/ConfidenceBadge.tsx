import React from 'react';
import { ConfidenceLevel } from '../../types';
import { cn } from '../../lib/utils';
import { ShieldCheck, ShieldAlert, ShieldX } from 'lucide-react';

interface ConfidenceBadgeProps {
  confidence?: ConfidenceLevel;
  className?: string;
  showIcon?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  confidence = 'low',
  className,
  showIcon = true,
}) => {
  const configs = {
    high: {
      label: 'High evidence match',
      bg: 'bg-emerald-50 text-emerald-800 border-emerald-200',
      dot: 'bg-emerald-500',
      icon: ShieldCheck,
    },
    medium: {
      label: 'Moderate evidence match',
      bg: 'bg-amber-50 text-amber-800 border-amber-200',
      dot: 'bg-amber-500',
      icon: ShieldAlert,
    },
    low: {
      label: 'Low / Insufficient evidence',
      bg: 'bg-slate-100 text-slate-700 border-slate-200',
      dot: 'bg-slate-400',
      icon: ShieldX,
    },
  };

  const current = configs[confidence] || configs.low;
  const IconComponent = current.icon;

  return (
    <div
      className={cn(
        'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md border text-xs font-medium tracking-wide',
        current.bg,
        className
      )}
      title={`Calculated from semantic retrieval relevance`}
    >
      <span className={cn('h-2 w-2 rounded-full animate-pulse', current.dot)} />
      {showIcon && <IconComponent className="w-3.5 h-3.5 opacity-80" />}
      <span>
        <strong className="font-semibold">Evidence confidence:</strong> {confidence.toUpperCase()}
      </span>
    </div>
  );
};
