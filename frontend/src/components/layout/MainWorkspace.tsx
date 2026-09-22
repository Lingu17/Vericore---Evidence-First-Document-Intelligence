import React from 'react';
import { ChatMessage, SourceEvidence } from '../../types';
import { ChatArea } from '../chat/ChatArea';
import { QueryInput } from '../chat/QueryInput';
import { SuggestedQuestions } from '../chat/SuggestedQuestions';
import { AlertCircle } from 'lucide-react';

interface MainWorkspaceProps {
  messages: ChatMessage[];
  isQuerying: boolean;
  queryStep: string | null;
  hasDocuments: boolean;
  suggestedQuestions: string[];
  chatError: string | null;
  onSendQuery: (question: string) => void;
  onSelectEvidence: (evidence: SourceEvidence) => void;
}

export const MainWorkspace: React.FC<MainWorkspaceProps> = ({
  messages,
  isQuerying,
  queryStep,
  hasDocuments,
  suggestedQuestions,
  chatError,
  onSendQuery,
  onSelectEvidence,
}) => {
  return (
    <main className="flex-1 flex flex-col h-full bg-[#F8FAFC] overflow-hidden">
      {/* Error alert if present */}
      {chatError && (
        <div className="mx-4 mt-3 p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{chatError}</span>
        </div>
      )}

      {/* Main Conversation Timeline */}
      <ChatArea
        messages={messages}
        isQuerying={isQuerying}
        queryStep={queryStep}
        hasDocuments={hasDocuments}
        onSelectEvidence={onSelectEvidence}
        onAskQuestion={onSendQuery}
      />

      {/* Bottom Query & Suggestions Bar */}
      <div className="p-4 lg:px-8 border-t border-slate-200/90 bg-white space-y-3 shrink-0 shadow-lg">
        {/* Suggested questions chips if conversation is active */}
        {hasDocuments && messages.length > 0 && suggestedQuestions.length > 0 && (
          <SuggestedQuestions
            questions={suggestedQuestions}
            onSelect={onSendQuery}
            disabled={isQuerying}
          />
        )}

        {/* Question Search Input */}
        <QueryInput
          onSend={onSendQuery}
          isLoading={isQuerying}
          disabled={!hasDocuments}
          placeholder={
            hasDocuments
              ? 'Ask a factual question across your uploaded documents...'
              : 'Upload documents in the sidebar to start asking questions...'
          }
        />
      </div>
    </main>
  );
};
