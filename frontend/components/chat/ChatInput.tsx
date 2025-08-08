'use client';

import { useState } from 'react';
import { Box, TextArea, Button, Flex } from '@radix-ui/themes';
import { PaperPlaneIcon } from '@radix-ui/react-icons';
import { AudioRecorder } from './AudioRecorder';

interface ChatInputProps {
  onSendMessage: (message: string) => Promise<void>;
  onAudioMessage?: (text: string) => Promise<void>;
  disabled?: boolean;
  token?: string;
  placeholder?: string;
  showAudioRecorder?: boolean;
}

export function ChatInput({ 
  onSendMessage, 
  onAudioMessage, 
  disabled = false, 
  token,
  placeholder = "Type your message...",
  showAudioRecorder = true
}: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = async () => {
    if (!input.trim() || disabled) return;
    
    const message = input.trim();
    setInput('');
    await onSendMessage(message);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box p="3" style={{ borderTop: '1px solid var(--gray-6)' }}>
      <Flex direction="column" gap="3">
        {/* Audio Recording */}
        {showAudioRecorder && token && onAudioMessage && (
          <AudioRecorder
            onTextReceived={onAudioMessage}
            disabled={disabled}
            token={token}
          />
        )}
        
        {/* Text Input */}
        <Flex gap="2" align="end">
          <TextArea
            placeholder={placeholder}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            style={{ flex: 1, minHeight: '60px', resize: 'vertical' }}
            disabled={disabled}
          />
          <Button 
            size="3" 
            onClick={handleSend} 
            disabled={disabled || !input.trim()}
          >
            {disabled ? '...' : <PaperPlaneIcon />}
          </Button>
        </Flex>
      </Flex>
    </Box>
  );
}
