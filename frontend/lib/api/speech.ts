export interface SpeechToTextResponse {
  text: string;
  confidence: number;
}

export async function speechToText(audioFile: File, token: string): Promise<string> {
  const formData = new FormData();
  formData.append('audio', audioFile);

  const response = await fetch('/api/speech/to-text', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => null);
    throw new Error(errorData?.detail || 'Failed to convert speech to text');
  }

  const data: SpeechToTextResponse = await response.json();
  return data.text;
}
