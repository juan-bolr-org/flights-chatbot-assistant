// lib/api/chat.ts

const API_URL = process.env.API_ENV || 'http://localhost:3000';

export async function sendChatMessage(query: string): Promise<string> {
  const jwt = localStorage.getItem("token");

  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(jwt ? { Authorization: `Bearer ${jwt}` } : {}),
    },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("Error al enviar mensaje");
  }

  const data = await res.json();
  return data.response || "Sin respuesta del servidor";
}
