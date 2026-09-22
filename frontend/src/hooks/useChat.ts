import { useState } from 'react';
import { ChatMessage, SourceEvidence } from '../types';
import { api } from '../services/api';

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isQuerying, setIsQuerying] = useState<boolean>(false);
  const [queryStep, setQueryStep] = useState<string | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<SourceEvidence | null>(null);
  const [isEvidenceDrawerOpen, setIsEvidenceDrawerOpen] = useState<boolean>(false);
  const [chatError, setChatError] = useState<string | null>(null);

  const openEvidence = (evidence: SourceEvidence) => {
    setSelectedEvidence(evidence);
    setIsEvidenceDrawerOpen(true);
  };

  const closeEvidence = () => {
    setSelectedEvidence(null);
    setIsEvidenceDrawerOpen(false);
  };

  const sendQuery = async (question: string, documentIdFilter?: string | null) => {
    const trimmed = question.trim();
    if (!trimmed || isQuerying) return;

    setChatError(null);
    const userMsgId = `usr_${Date.now()}`;
    const userMsg: ChatMessage = {
      id: userMsgId,
      role: 'user',
      content: trimmed,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsQuerying(true);
    setQueryStep('Searching semantic vector index...');

    try {
      // Create compact history (last 4 messages)
      const compactHistory = messages.slice(-4).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      setTimeout(() => {
        setQueryStep('Retrieving and verifying grounded evidence...');
      }, 300);

      const response = await api.sendQuery({
        question: trimmed,
        conversation_history: compactHistory,
        document_id: documentIdFilter,
      });

      setQueryStep('Generating grounded answer...');

      const assistantMsg: ChatMessage = {
        id: `ast_${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        status: response.status,
        confidence: response.confidence,
        sources: response.sources,
        suggested_followups: response.suggested_followups,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMsg]);
      setSelectedEvidence(null);
    } catch (err: any) {
      setChatError(err.message || 'Failed to generate answer from documents.');
    } finally {
      setIsQuerying(false);
      setQueryStep(null);
    }
  };

  const clearMessages = () => {
    setMessages([]);
    setSelectedEvidence(null);
    setIsEvidenceDrawerOpen(false);
    setChatError(null);
  };

  return {
    messages,
    isQuerying,
    queryStep,
    selectedEvidence,
    setSelectedEvidence,
    isEvidenceDrawerOpen,
    openEvidence,
    closeEvidence,
    chatError,
    sendQuery,
    clearMessages,
  };
}
