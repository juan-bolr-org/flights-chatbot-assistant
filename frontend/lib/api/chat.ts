// lib/api/chat.ts

import { 
  ChatHistoryResponse, 
  DeleteChatHistoryResponse, 
  ChatSessionsResponse, 
  DeleteSessionResponse,
  ChatResponse 
} from '../types/chat';

const API_URL = '/api';

export async function sendChatMessage(
  token: string, 
  query: string, 
  sessionId?: string
): Promise<ChatResponse> {
  const body: any = { content: query };
  if (sessionId) {
    body.session_id = sessionId;
  }

  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    throw new Error("Error sending message");
  }

  return await res.json();
}

export async function getChatHistory(
  token: string, 
  sessionId?: string,
  limit: number = 50, 
  offset: number = 0
): Promise<ChatHistoryResponse> {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  });
  
  if (sessionId) {
    params.append('session_id', sessionId);
  }

  const res = await fetch(`${API_URL}/chat/history?${params}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error("Error fetching chat history");
  }

  return await res.json();
}

export async function deleteChatHistory(
  token: string, 
  sessionId?: string
): Promise<DeleteChatHistoryResponse> {
  const params = sessionId ? `?session_id=${sessionId}` : '';
  
  const res = await fetch(`${API_URL}/chat/history${params}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error("Error deleting chat history");
  }

  return await res.json();
}

export async function getChatSessions(token: string): Promise<ChatSessionsResponse> {
  const res = await fetch(`${API_URL}/chat/sessions`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error("Error fetching chat sessions");
  }

  return await res.json();
}

export async function deleteSession(
  token: string, 
  sessionId: string
): Promise<DeleteSessionResponse> {
  const res = await fetch(`${API_URL}/chat/sessions/${sessionId}`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
  });

  if (!res.ok) {
    throw new Error("Error deleting session");
  }

  return await res.json();
}
