import { useState, useEffect, useCallback } from 'react';
import { DocumentItem } from '../types';
import { api } from '../services/api';

export function useDocuments() {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await api.getDocuments();
      setDocuments(res.documents);
    } catch (err: any) {
      setError(err.message || 'Failed to load documents');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const uploadFile = async (file: File): Promise<{ success: boolean; message: string; doc?: any }> => {
    // Validate file type
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (ext !== 'pdf' && ext !== 'txt') {
      const msg = `Unsupported file type .${ext}. Only PDF and TXT files are supported.`;
      setError(msg);
      return { success: false, message: msg };
    }

    // Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      const msg = 'File size exceeds 10MB limit.';
      setError(msg);
      return { success: false, message: msg };
    }

    try {
      setIsUploading(true);
      setUploadProgress('Extracting & indexing document...');
      setError(null);

      const res = await api.uploadDocument(file);
      await fetchDocuments();

      if (res.status === 'already_exists') {
        return {
          success: true,
          message: 'Document already indexed (deduplicated).',
          doc: res,
        };
      }

      return {
        success: true,
        message: `Successfully indexed ${res.pages} page(s) and ${res.chunks} chunks.`,
        doc: res,
      };
    } catch (err: any) {
      const msg = err.message || 'Failed to upload document.';
      setError(msg);
      return { success: false, message: msg };
    } finally {
      setIsUploading(false);
      setUploadProgress(null);
    }
  };

  const deleteDocument = async (documentId: string) => {
    try {
      setError(null);
      await api.deleteDocument(documentId);
      setDocuments((prev) => prev.filter((d) => d.document_id !== documentId));
      if (selectedDocId === documentId) {
        setSelectedDocId(null);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to delete document');
    }
  };

  const clearAll = async () => {
    try {
      setError(null);
      await api.clearAllDocuments();
      setDocuments([]);
      setSelectedDocId(null);
    } catch (err: any) {
      setError(err.message || 'Failed to clear documents');
    }
  };

  // Collect all suggested questions from active documents
  const allSuggestedQuestions = documents.flatMap((d) => d.suggested_questions || []).slice(0, 6);

  return {
    documents,
    isLoading,
    isUploading,
    uploadProgress,
    error,
    selectedDocId,
    setSelectedDocId,
    uploadFile,
    deleteDocument,
    clearAll,
    refreshDocuments: fetchDocuments,
    allSuggestedQuestions,
  };
}
