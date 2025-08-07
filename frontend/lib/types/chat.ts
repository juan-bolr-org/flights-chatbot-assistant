export interface ChatRequest {
  content: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
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
}

export interface DeleteChatHistoryResponse {
  deleted_count: number;
  message: string;
}

export interface ChatSessionsResponse {
  sessions: string[];
  total_count: number;
}

export interface DeleteSessionResponse {
  message: string;
  session_id: string;
  deleted_count: number;
}

export interface ChatSession {
  id: string;
  name: string;
  lastActivity: string;
  messageCount: number;
}
