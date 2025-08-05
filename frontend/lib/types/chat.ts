export interface ChatRequest {
  content: string;
}

export interface ChatResponse {
  response: string;
}

export interface ChatMessage {
  id: number;
  message: string;
  response: string;
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
