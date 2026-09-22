export type ConfidenceLevel = 'high' | 'medium' | 'low';
export type ChatStatus = 'answered' | 'not_found';
export type DocumentStatus = 'indexed' | 'processing' | 'failed' | 'already_exists';

export interface SourceEvidence {
  document_id: string;
  filename: string;
  page: number;
  section?: string;
  evidence: string;
  chunk_id: string;
  similarity_score?: number;
}

export interface DocumentItem {
  document_id: string;
  filename: string;
  file_type: string;
  pages: number;
  chunks: number;
  status: string;
  created_at: string;
  suggested_questions: string[];
}

export interface DocumentListResponse {
  total: number;
  documents: DocumentItem[];
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  pages: number;
  chunks: number;
  status: string;
  message?: string;
  suggested_questions: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  status?: ChatStatus;
  confidence?: ConfidenceLevel;
  sources?: SourceEvidence[];
  suggested_followups?: string[];
  timestamp: string;
}

export interface ChatRequest {
  question: string;
  conversation_history: { role: string; content: string }[];
  document_id?: string | null;
}

export interface ChatResponse {
  status: ChatStatus;
  answer: string;
  confidence: ConfidenceLevel;
  sources: SourceEvidence[];
  suggested_followups: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
  embedding_model: string;
  llm_provider: string;
  vector_store_documents: number;
}
