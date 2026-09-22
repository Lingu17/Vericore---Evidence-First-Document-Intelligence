import React from 'react';
import { HelpCircle, Search, Lightbulb } from 'lucide-react';
import { ChatMessage } from '../../types';

const UNKNOWN_ANSWER = 'Information not available in the uploaded documents.';

interface UnknownQuestionCardProps {
  message: ChatMessage;
  onAskSuggestion?: (question: string) => void;
}

export const UnknownQuestionCard: React.FC<UnknownQuestionCardProps> = ({
  message,
  onAskSuggestion,
}) => {
  return (
    <div className="rounded-xl border border-slate-200/90 bg-slate-50/70 p-5 shadow-subtle space-y-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center text-amber-700 shrink-0 mt-0.5">
          <HelpCircle className="w-4 h-4" />
        </div>

        <div className="space-y-1 flex-1">
          <div className="flex items-center gap-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700">
              Information Not Found
            </h4>
            <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-200/80 text-slate-700">
              Zero grounded evidence
            </span>
          </div>
          <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-line">
            {UNKNOWN_ANSWER}
          </p>
        </div>
      </div>

      {message.suggested_followups && message.suggested_followups.length > 0 && (
        <div className="pt-3 border-t border-slate-200/60">
          <p className="text-xs font-semibold text-slate-600 flex items-center gap-1.5 mb-2">
            <Lightbulb className="w-3.5 h-3.5 text-amber-600" />
            <span>Try asking about topics in your uploaded documents:</span>
          </p>
          <div className="flex flex-wrap gap-1.5">
            {message.suggested_followups.map((s, idx) => (
              <button
                key={idx}
                onClick={() => onAskSuggestion && onAskSuggestion(s)}
                className="text-xs text-brand-700 bg-white hover:bg-brand-50 border border-slate-200/90 hover:border-brand-300 px-2.5 py-1 rounded-md transition-all text-left flex items-center gap-1 shadow-subtle"
              >
                <Search className="w-3 h-3 opacity-60 shrink-0" />
                <span>{s}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
