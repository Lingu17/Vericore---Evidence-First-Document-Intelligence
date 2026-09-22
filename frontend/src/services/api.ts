import {
  ChatRequest,
  ChatResponse,
  DocumentListResponse,
  DocumentUploadResponse,
  HealthResponse,
} from '../types';

const API_BASE = '/api';

class ApiService {
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch {
        // use default error message
      }
      throw new Error(errorMessage);
    }
    return response.json();
  }

  async getHealth(): Promise<HealthResponse> {
    const res = await fetch('/health');
    return this.handleResponse<HealthResponse>(res);
  }

  async getDocuments(): Promise<DocumentListResponse> {
    const res = await fetch(`${API_BASE}/documents`);
    return this.handleResponse<DocumentListResponse>(res);
  }

  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/documents/upload`, {
      method: 'POST',
      body: formData,
    });
    return this.handleResponse<DocumentUploadResponse>(res);
  }

  async deleteDocument(documentId: string): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/documents/${documentId}`, {
      method: 'DELETE',
    });
    return this.handleResponse<{ status: string; message: string }>(res);
  }

  async clearAllDocuments(): Promise<{ status: string; message: string }> {
    const res = await fetch(`${API_BASE}/documents`, {
      method: 'DELETE',
    });
    return this.handleResponse<{ status: string; message: string }>(res);
  }

  async sendQuery(request: ChatRequest): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return this.handleResponse<ChatResponse>(res);
  }
}

export const api = new ApiService();
