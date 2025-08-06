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
    let errorMessage = 'Failed to convert speech to text';
    
    try {
      const errorData = await response.json();

      console.error('Speech-to-text error response:', JSON.stringify(errorData, null, 2));
      
      // Handle different error response formats
      if (typeof errorData === 'string') {
        errorMessage = errorData;
      } else if (errorData?.detail) {
        // Handle structured error from backend
        if (typeof errorData.detail === 'object') {
          errorMessage = errorData.detail.message || JSON.stringify(errorData.detail);
        } else {
          errorMessage = errorData.detail;
        }
      } else if (errorData?.message) {
        errorMessage = errorData.message;
      } else if (errorData?.error) {
        errorMessage = errorData.error;
      } else if (typeof errorData === 'object') {
        // Try to extract meaningful info from object
        errorMessage = JSON.stringify(errorData);
      }
    } catch (parseError) {
      // If JSON parsing fails, try to get text response
      try {
        const textResponse = await response.text();
        errorMessage = textResponse || `HTTP ${response.status}: ${response.statusText}`;
      } catch (textError) {
        errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      }
    }
    
    throw new Error(errorMessage);
  }

  const data: SpeechToTextResponse = await response.json();
  return data.text;
}
