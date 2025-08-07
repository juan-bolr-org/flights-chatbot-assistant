// lib/api/chat.ts

import { 
  ChatHistoryResponse, 
  DeleteChatHistoryResponse, 
  ChatSessionsResponse, 
  DeleteSessionResponse,
  ChatResponse
} from '../types/chat';

// Import the new types from the shared components
import { 
  CreateSessionRequest,
  CreateSessionResponse,
  UpdateSessionAliasRequest,
  UpdateSessionAliasResponse
} from '../../components/chat/types';

const API_URL = '/api';

export async function sendChatMessage(
  token: string, 
  query: string, 
  sessionId: string,  // Now required
  sessionAlias?: string
): Promise<ChatResponse> {
  const body: any = { 
    content: query,
    session_id: sessionId
  };
  if (sessionAlias) {
    body.session_alias = sessionAlias;
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
  sessionId: string,  // Now required
  limit: number = 50, 
  offset: number = 0
): Promise<ChatHistoryResponse> {
  const params = new URLSearchParams({
    session_id: sessionId,
    limit: limit.toString(),
    offset: offset.toString(),
  });

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
  sessionId: string  // Now required
): Promise<DeleteChatHistoryResponse> {
  const params = `?session_id=${sessionId}`;
  
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

export async function createSession(
  token: string,
  request: CreateSessionRequest
): Promise<CreateSessionResponse> {
  const res = await fetch(`${API_URL}/chat/sessions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    throw new Error("Error creating session");
  }

  return await res.json();
}

export async function updateSessionAlias(
  token: string,
  sessionId: string,
  request: UpdateSessionAliasRequest
): Promise<UpdateSessionAliasResponse> {
  const res = await fetch(`${API_URL}/chat/sessions/${sessionId}/alias`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include',
    body: JSON.stringify(request),
  });

  if (!res.ok) {
    throw new Error("Error updating session alias");
  }

  return await res.json();
}
