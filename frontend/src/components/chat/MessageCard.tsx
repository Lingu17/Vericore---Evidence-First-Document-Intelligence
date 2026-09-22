import React from 'react';
import { ChatMessage, SourceEvidence } from '../../types';
import { ConfidenceBadge } from '../common/ConfidenceBadge';
import { UnknownQuestionCard } from './UnknownQuestionCard';
import { FileText, ExternalLink, User, Bot, CheckCircle2 } from 'lucide-react';

interface MessageCardProps {
  message: ChatMessage;
  onSelectEvidence: (evidence: SourceEvidence) => void;
  onAskSuggestion?: (question: string) => void;
}

export const MessageCard: React.FC<MessageCardProps> = ({
  message,
  onSelectEvidence,
  onAskSuggestion,
}) => {
  if (message.role === 'user') {
    return (
      <div className="flex items-start gap-3 justify-end my-4">
        <div className="max-w-2xl bg-slate-900 text-white px-4 py-3 rounded-2xl rounded-tr-sm shadow-subtle">
          <p className="text-sm font-normal leading-relaxed">{message.content}</p>
        </div>
        <div className="w-8 h-8 rounded-full bg-slate-200 border border-slate-300 flex items-center justify-center text-slate-700 shrink-0 mt-0.5">
          <User className="w-4 h-4" />
        </div>
      </div>
    );
  }

  // If assistant response is NOT_FOUND
  if (message.status === 'not_found') {
    return <UnknownQuestionCard message={message} onAskSuggestion={onAskSuggestion} />;
  }

  const sources = message.sources || [];

  return (
    <div className="flex items-start gap-3.5 my-5">
      <div className="w-8 h-8 rounded-full bg-brand-600 border border-brand-700 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-sm">
        <Bot className="w-4.5 h-4.5" />
      </div>

      <div className="flex-1 max-w-3xl space-y-4">
        {/* Answer Container Card */}
        <div className="bg-white border border-slate-200/90 rounded-2xl p-5 shadow-subtle space-y-4">
          <div className="flex items-center justify-between pb-2 border-b border-slate-100">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                Grounded Answer
              </span>
              <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                Verified
              </span>
            </div>

            <ConfidenceBadge confidence={message.confidence} />
          </div>

          {/* Answer text */}
          <div className="text-sm text-slate-800 leading-relaxed whitespace-pre-line font-normal">
            {message.content}
          </div>

          {/* Source Attribution list */}
          {sources.length > 0 && (
            <div className="pt-4 border-t border-slate-100 space-y-2.5">
              <div className="flex items-center justify-between">
                <p className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
                  Sources ({sources.length})
                </p>
                <span className="text-[11px] text-slate-400">
                  Click to inspect full page excerpt
                </span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                {sources.map((src, idx) => (
                  <div
                    key={idx}
                    onClick={() => onSelectEvidence(src)}
                    className="group flex flex-col justify-between p-3 rounded-xl border border-slate-200/80 bg-slate-50/60 hover:bg-brand-50/50 hover:border-brand-300 transition-all cursor-pointer shadow-subtle select-none"
                  >
                    <div>
                      <div className="flex items-center justify-between gap-1.5 mb-1">
                        <div className="flex items-center gap-1.5 min-w-0">
                          <FileText className="w-3.5 h-3.5 text-brand-600 shrink-0" />
                          <span className="text-xs font-semibold text-slate-900 truncate" title={src.filename}>
                            {src.filename}
                          </span>
                        </div>
                        <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-slate-200/90 text-slate-700 shrink-0">
                          Page {src.page}
                        </span>
                      </div>

                      {src.section && (
                        <p className="text-[11px] font-medium text-slate-600 truncate mb-1">
                          {src.section}
                        </p>
                      )}

                      <p className="text-xs text-slate-600 line-clamp-2 italic leading-snug">
                        "{src.evidence}"
                      </p>
                    </div>

                    <div className="mt-2 pt-1.5 border-t border-slate-200/40 flex items-center justify-between text-[11px] text-brand-600 font-medium group-hover:text-brand-700">
                      <span>View evidence</span>
                      <ExternalLink className="w-3 h-3 group-hover:translate-x-0.5 transition-transform" />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
