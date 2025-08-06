// lib/api/chat.ts

import { ChatHistoryResponse, DeleteChatHistoryResponse } from '../types/chat';

const API_URL = '/api';

export async function sendChatMessage(token: string, query: string): Promise<string> {

  const res = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include', // Include cookies in the request
    body: JSON.stringify({ "content": query }),
  });

  if (!res.ok) {
    throw new Error("Error sending message");
  }

  const data = await res.json();
  return data.response || "No response from server";
}

export async function getChatHistory(
  token: string, 
  limit: number = 50, 
  offset: number = 0
): Promise<ChatHistoryResponse> {
  const res = await fetch(`${API_URL}/chat/history?limit=${limit}&offset=${offset}`, {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include', // Include cookies in the request
  });

  if (!res.ok) {
    throw new Error("Error fetching chat history");
  }

  return await res.json();
}

export async function deleteChatHistory(token: string): Promise<DeleteChatHistoryResponse> {
  const res = await fetch(`${API_URL}/chat/history`, {
    method: "DELETE",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    credentials: 'include', // Include cookies in the request
  });

  if (!res.ok) {
    throw new Error("Error deleting chat history");
  }

  return await res.json();
}
