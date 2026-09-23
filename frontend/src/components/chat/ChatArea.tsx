import React, { useRef, useEffect } from 'react';
import { ChatMessage, SourceEvidence } from '../../types';
import { MessageCard } from './MessageCard';
import { Bot, Loader2, Sparkles, ShieldCheck, FileCheck, HelpCircle } from 'lucide-react';

interface ChatAreaProps {
  messages: ChatMessage[];
  isQuerying: boolean;
  queryStep: string | null;
  hasDocuments: boolean;
  onSelectEvidence: (evidence: SourceEvidence) => void;
  onAskQuestion: (question: string) => void;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  isQuerying,
  queryStep,
  hasDocuments,
  onSelectEvidence,
  onAskQuestion,
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isQuerying, queryStep]);

  if (messages.length === 0) {
    return (
      <div className="relative flex-1 flex flex-col items-center justify-center px-6 py-8 text-center max-w-2xl mx-auto space-y-6 select-none overflow-y-auto">
        {/* Subtle ambient radial glow behind empty state */}
        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_60%_45%_at_50%_35%,rgba(37,99,235,0.05),transparent_70%)]" />

        <div className="relative w-14 h-14 rounded-2xl bg-white border border-slate-200 flex items-center justify-center text-brand-600 shadow-[0_8px_24px_rgba(15,23,42,0.08)] hover:shadow-lift transition-shadow duration-200">
          <Bot className="w-7 h-7" />
        </div>

        <div className="relative space-y-2">
          <h2 className="text-xl font-bold text-slate-900 tracking-tight">
            {hasDocuments
              ? 'Ask your documents. Verify every answer.'
              : 'Your knowledge workspace is empty.'}
          </h2>
          <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
            {hasDocuments
              ? 'Vericore retrieves verified evidence passages from your uploaded business documents and returns concise answers grounded in that evidence.'
              : 'Upload documents to start building your knowledge workspace.'}
          </p>
          {!hasDocuments && (
            <p className="text-[12px] sm:text-[13px] text-slate-500 leading-relaxed">
              Add policies, handbooks, SOPs, reports, or other business documents to start
              asking questions.
            </p>
          )}
        </div>

        {/* Value pillars */}
        <div className="relative grid grid-cols-1 sm:grid-cols-3 gap-3 w-full text-left">
          <div className="p-3.5 rounded-xl border border-slate-200 bg-white shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lift hover:border-brand-300">
            <div className="w-8 h-8 rounded-lg bg-brand-50 border border-brand-100 flex items-center justify-center mb-2">
              <ShieldCheck className="w-4 h-4 text-brand-600" />
            </div>
            <h4 className="text-xs font-bold text-slate-800">Evidence-Grounded</h4>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Responses are built from retrieved, verifiable document context.
            </p>
          </div>

          <div className="p-3.5 rounded-xl border border-slate-200 bg-white shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lift hover:border-brand-300">
            <div className="w-8 h-8 rounded-lg bg-brand-50 border border-brand-100 flex items-center justify-center mb-2">
              <FileCheck className="w-4 h-4 text-brand-600" />
            </div>
            <h4 className="text-xs font-bold text-slate-800">Page-Level Audit</h4>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Exact source document, section, and page attribution.
            </p>
          </div>

          <div className="p-3.5 rounded-xl border border-slate-200 bg-white shadow-card transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lift hover:border-brand-300">
            <div className="w-8 h-8 rounded-lg bg-brand-50 border border-brand-100 flex items-center justify-center mb-2">
              <HelpCircle className="w-4 h-4 text-brand-600" />
            </div>
            <h4 className="text-xs font-bold text-slate-800">Clear Unknowns</h4>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Distinct 'Information Not Found' when evidence is absent.
            </p>
          </div>
        </div>

        {/* Demo starter prompts if documents exist */}
        {hasDocuments && (
          <div className="relative w-full pt-2">
            <p className="text-xs font-semibold text-slate-500 flex items-center justify-center gap-1 mb-2.5">
              <Sparkles className="w-3.5 h-3.5 text-brand-600" />
              <span>Try asking these sample questions:</span>
            </p>
            <div className="flex flex-col gap-2">
              {[
                'How many annual leaves does an employee receive?',
                'Can unused leave be carried forward?',
                'What is the probation period?',
                'What health insurance coverage is provided?',
                "What was NovaTech's revenue last year?",
              ].map((sampleQ, idx) => (
                <button
                  key={idx}
                  onClick={() => onAskQuestion(sampleQ)}
                  className="text-left text-xs bg-white hover:bg-brand-50/60 hover:border-brand-300 border border-slate-200 text-slate-700 hover:text-slate-900 px-3.5 py-2 rounded-xl shadow-subtle hover:shadow-card transition-all duration-200 hover:-translate-y-px flex items-center justify-between group"
                >
                  <span className="font-medium">{sampleQ}</span>
                  {idx === 4 ? (
                    <span className="text-[10px] bg-amber-50 text-amber-800 font-bold px-1.5 py-0.5 rounded border border-amber-200">
                      Tests NOT_FOUND
                    </span>
                  ) : (
                    <span className="text-[10px] text-brand-600 font-semibold group-hover:text-brand-800">
                      Ask →
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2">
      {messages.map((msg) => (
        <MessageCard
          key={msg.id}
          message={msg}
          onSelectEvidence={onSelectEvidence}
          onAskSuggestion={onAskQuestion}
        />
      ))}

      {/* Querying stage progress indicator */}
      {isQuerying && (
        <div className="flex items-start gap-3.5 my-4">
          <div className="w-8 h-8 rounded-full bg-brand-600 flex items-center justify-center text-white shrink-0 mt-0.5 shadow-card">
            <Bot className="w-4.5 h-4.5" />
          </div>
          <div className="bg-white border border-slate-200 rounded-2xl px-5 py-4 shadow-card flex items-center gap-3">
            <Loader2 className="w-4 h-4 text-brand-600 animate-spin" />
            <div className="space-y-0.5">
              <p className="text-xs font-semibold text-slate-800">
                {queryStep || 'Searching documents and retrieving verified evidence...'}
              </p>
              <p className="text-[11px] text-slate-500">
                Evaluating semantic relevance & verifying citations
              </p>
            </div>
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
};