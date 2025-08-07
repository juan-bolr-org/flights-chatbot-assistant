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
  id: string;
  name: string;
  lastActivity: string;
  messageCount: number;
}

// API response interfaces
export interface ChatResponse {
  response: string;
  session_id?: string;
}

export interface ChatHistoryMessage {
  message: string;
  response: string;
  created_at: string;
}

export interface ChatHistoryResponse {
  messages: ChatHistoryMessage[];
}

export interface ChatSessionsResponse {
  sessions: string[];
}
