// Shared types for chat components
export interface BaseMessage {
  role: 'user' | 'bot';
  content: string;
}

export interface MessageWithTimestamp extends BaseMessage {
  timestamp: Date;
}

export interface MessageWithoutTimestamp extends BaseMessage {
  // No timestamp field
}

// Union type for all message formats
export type ChatMessage = MessageWithTimestamp | MessageWithoutTimestamp;

// Type guard to check if message has timestamp
export function hasTimestamp(message: ChatMessage): message is MessageWithTimestamp {
  return 'timestamp' in message && message.timestamp instanceof Date;
}

// Chat session interface
export interface ChatSession {
  session_id: string;
  alias: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

// API response interfaces
export interface ChatResponse {
  response: string;
  session_id: string;
  session_alias: string;
}

export interface ChatHistoryMessage {
  id: number;
  message: string;
  response: string;
  session_id: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: ChatHistoryMessage[];
  total_count: number;
}

export interface ChatSessionsResponse {
  sessions: ChatSession[];
  total_count: number;
}

// Session management requests
export interface CreateSessionRequest {
  alias?: string;
}

export interface CreateSessionResponse {
  session_id: string;
  alias: string;
  message: string;
}

export interface UpdateSessionAliasRequest {
  alias: string;
}

export interface UpdateSessionAliasResponse {
  session_id: string;
  alias: string;
  message: string;
}

export interface DeleteSessionResponse {
  message: string;
  session_id: string;
  deleted_count: number;
}
