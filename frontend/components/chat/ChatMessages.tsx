'use client';

import { useEffect, useRef } from 'react';
import { Box, ScrollArea, Text, Flex } from '@radix-ui/themes';
import { ChatMessage, hasTimestamp } from './types';

interface ChatMessagesProps {
  messages: ChatMessage[];
  isLoadingHistory: boolean;
}

export function ChatMessages({ messages, isLoadingHistory }: ChatMessagesProps) {
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const scrollAreaRef = useRef<HTMLDivElement | null>(null);

  // Auto scroll to bottom only when messages change
  useEffect(() => {
    if (messages.length > 0 && bottomRef.current) {
      // Use scrollIntoView but restrict it to the ScrollArea container
      bottomRef.current.scrollIntoView({ 
        behavior: 'smooth',
        block: 'end',
        inline: 'nearest'
      });
    }
  }, [messages]);

  return (
    <ScrollArea 
      ref={scrollAreaRef}
      style={{ flex: 1 }} 
      mb="3"
      type="always"
      scrollbars="vertical"
    >
      <Flex direction="column" gap="3" p="3">
        {isLoadingHistory ? (
          <Box p="4" style={{ textAlign: 'center' }}>
            <Text size="2" color="gray">Loading chat history...</Text>
          </Box>
        ) : (
          messages.map((msg, idx) => (
            <Flex
              key={idx}
              justify={msg.role === 'user' ? 'end' : 'start'}
            >
              <Box
                p="3"
                style={{
                  backgroundColor: msg.role === 'user' ? 'var(--accent-3)' : 'var(--gray-3)',
                  borderRadius: '12px',
                  maxWidth: '70%',
                  border: msg.role === 'user' ? '1px solid var(--accent-7)' : '1px solid var(--gray-6)',
                }}
              >
                <Text size="2" style={{ whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </Text>
                {hasTimestamp(msg) && (
                  <Text size="1" color="gray" style={{ display: 'block', marginTop: '4px' }}>
                    {msg.timestamp.toLocaleTimeString()}
                  </Text>
                )}
              </Box>
            </Flex>
          ))
        )}
        <div ref={bottomRef} />
      </Flex>
    </ScrollArea>
  );
}
