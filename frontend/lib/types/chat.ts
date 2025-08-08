export interface ChatRequest {
  content: string;
  session_id: string;  // Required session ID
  session_alias?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  session_alias: string;
}

export interface ChatMessage {
  id: number;
  message: string;
  response: string;
  session_id: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total_count: number;
  session_alias: string;
}

export interface DeleteChatHistoryResponse {
  deleted_count: number;
  message: string;
  session_id: string;
}

export interface ChatSession {
  session_id: string;
  alias: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ChatSessionsResponse {
  sessions: ChatSession[];
  total_count: number;
}

export interface DeleteSessionResponse {
  message: string;
  session_id: string;
  deleted_count: number;
}
