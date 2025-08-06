'use client';

import { useState } from 'react';
import { Button, Flex, Text, AlertDialog } from '@radix-ui/themes';
import { MicIcon, Square, SendIcon } from 'lucide-react';
import { useAudioRecorder } from '@/lib/hooks/useAudioRecorder';
import { speechToText } from '@/lib/api/speech';

interface AudioRecorderProps {
  onTextReceived: (text: string) => void;
  disabled?: boolean;
  token: string;
}

export function AudioRecorder({ onTextReceived, disabled = false, token }: AudioRecorderProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    isRecording,
    recordingTime,
    audioBlob,
    startRecording,
    stopRecording,
    resetRecording,
    error: recordingError
  } = useAudioRecorder(60000); // 1 minute max

  const formatTime = (timeMs: number) => {
    const seconds = Math.floor(timeMs / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const handleStartRecording = async () => {
    setError(null);
    try {
      await startRecording();
    } catch (err) {
      console.error('Recording start error:', err);
      
      let errorMessage = 'Failed to start recording. Please check microphone permissions.';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        errorMessage = (err as any).message || (err as any).detail || errorMessage;
      }
      
      setError(errorMessage);
    }
  };

  const handleStopRecording = () => {
    stopRecording();
  };

  const handleSendAudio = async () => {
    if (!audioBlob) return;

    setIsProcessing(true);
    setError(null);

    try {
      // Determine file extension based on blob type
      let extension = '.webm'; // default
      let fileName = 'audio-recording.webm';
      
      if (audioBlob.type.includes('wav')) {
        extension = '.wav';
        fileName = 'audio-recording.wav';
      } else if (audioBlob.type.includes('ogg')) {
        extension = '.ogg';
        fileName = 'audio-recording.ogg';
      }

      // Convert blob to File
      const audioFile = new File([audioBlob], fileName, {
        type: audioBlob.type
      });

      // Send to speech-to-text API
      const text = await speechToText(audioFile, token);
      
      if (text.trim()) {
        onTextReceived(text.trim());
        resetRecording();
      } else {
        setError('No speech detected in the recording. Please try again.');
      }
    } catch (err) {
      console.error('Error processing audio:', err);
      
      let errorMessage = 'Failed to process audio';
      
      if (err instanceof Error) {
        errorMessage = err.message;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err && typeof err === 'object') {
        // Handle cases where err might be an object with message property
        errorMessage = (err as any).message || (err as any).detail || JSON.stringify(err);
      }
      
      setError(errorMessage);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    resetRecording();
    setError(null);
  };

  return (
    <Flex direction="column" gap="2">
      {/* Recording Controls */}
      <Flex align="center" gap="2">
        {!isRecording && !audioBlob && (
          <Button
            size="2"
            variant="soft"
            onClick={handleStartRecording}
            disabled={disabled || isProcessing}
            title="Start recording (max 1 minute)"
          >
            <MicIcon size={16} />
            Record
          </Button>
        )}

        {isRecording && (
          <Flex align="center" gap="2">
            <Button
              size="2"
              variant="solid"
              color="red"
              onClick={handleStopRecording}
              title="Stop recording"
            >
              <Square size={16} />
              Stop
            </Button>
            <Text size="2" weight="medium">
              {formatTime(recordingTime)} / 1:00
            </Text>
          </Flex>
        )}

        {audioBlob && !isRecording && (
          <Flex align="center" gap="2">
            <Button
              size="2"
              variant="solid"
              onClick={handleSendAudio}
              disabled={isProcessing}
              title="Convert to text and send"
            >
              <SendIcon size={16} />
              {isProcessing ? 'Processing...' : 'Send'}
            </Button>
            <Button
              size="2"
              variant="ghost"
              onClick={handleReset}
              disabled={isProcessing}
              title="Record again"
            >
              <MicIcon size={16} />
              Record Again
            </Button>
            <Text size="2" color="gray">
              Recorded: {formatTime(recordingTime)}
            </Text>
          </Flex>
        )}
      </Flex>

      {/* Error Display */}
      {(error || recordingError) && (
        <Text size="2" color="red">
          {error || recordingError}
        </Text>
      )}

      {/* Recording Status */}
      {isRecording && (
        <Text size="2" color="green">
          🎙️ Recording... Speak clearly into your microphone
        </Text>
      )}

      {audioBlob && !isRecording && !isProcessing && (
        <Text size="2" color="blue">
          ✅ Recording ready. Click "Send" to convert to text and send to chat.
        </Text>
      )}

      {isProcessing && (
        <Text size="2" color="orange">
          🔄 Converting speech to text...
        </Text>
      )}
    </Flex>
  );
}
