import React from 'react';
import { Sparkles } from 'lucide-react';

interface SuggestedQuestionsProps {
  questions: string[];
  onSelect: (question: string) => void;
  disabled?: boolean;
}

export const SuggestedQuestions: React.FC<SuggestedQuestionsProps> = ({
  questions,
  onSelect,
  disabled = false,
}) => {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600">
        <Sparkles className="w-3.5 h-3.5 text-brand-600" />
        <span>Suggested questions from your documents</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            disabled={disabled}
            className="text-left text-xs bg-white hover:bg-brand-50/70 text-slate-700 hover:text-slate-900 border border-slate-200 hover:border-brand-300 px-3 py-1.5 rounded-full shadow-subtle hover:shadow-card transition-all duration-200 hover:-translate-y-px disabled:opacity-50 disabled:cursor-not-allowed group flex items-center gap-1.5"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-brand-500 group-hover:scale-125 transition-transform shrink-0" />
            <span className="truncate max-w-md">{q}</span>
          </button>
        ))}
      </div>
    </div>
  );
};