export interface DocumentRecord {
  document_id: string;
  filename: string;
  content_type?: string | null;
  size: number;
  stored_path: string;
  uploaded_at: string;
}

export interface UploadResponse {
  document: DocumentRecord;
  chunks_indexed: number;
  status: string;
}

export interface DocumentChunk {
  chunk_id: string;
  document_id: string;
  content: string;
  source: string;
  page?: number | null;
  uploaded_at: string;
}

export interface ChatResponse {
  answer: string;
  sources: DocumentChunk[];
  retrieval_used: boolean;
  latency_ms: number;
}
