export interface Conversation {
  id: string;
  title: string;
  summary?: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  created_at: string;
  metadata?: Record<string, unknown>;
}

export interface SourceInfo {
  document_id: string;
  document_name: string;
  chunk_id: string;
  page_number?: number;
  similarity_score?: number;
  retrieval_strategy: string;
}

export interface ChatResponse {
  message: Message;
  sources: SourceInfo[];
  retrieval: {
    used: boolean;
    strategy: string;
    decision?: Record<string, unknown>;
  };
}

export interface Document {
  id: string;
  conversation_id: string;
  file_name: string;
  file_type: string;
  file_size: number;
  status: "pending" | "processing" | "ready" | "error";
  metadata?: Record<string, unknown> & {
    processing_progress?: ProcessingProgress;
  };
  created_at: string;
  updated_at: string;
}

export interface ProcessingProgress {
  status: string;
  step: string;
  percent: number;
  chunks_processed?: number | null;
  chunks_total?: number | null;
  step_percent?: number | null;
}

export interface MessageWithSources extends Message {
  sources?: SourceInfo[];
  retrieval?: {
    used: boolean;
    strategy: string;
  };
}
