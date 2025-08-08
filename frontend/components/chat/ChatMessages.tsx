'use client';

import { useEffect, useRef } from 'react';
import { Box, ScrollArea, Text, Flex } from '@radix-ui/themes';
import ReactMarkdown from 'react-markdown';
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
                <div style={{ fontSize: '14px' }}>
                  <ReactMarkdown
                    components={{
                      // Customize markdown components to fit the design
                      p: ({ children }) => (
                        <Text size="2" style={{ display: 'block', margin: '0 0 8px 0' }}>
                          {children}
                        </Text>
                      ),
                      code: ({ children, className }) => {
                        const isInline = !className;
                        return isInline ? (
                          <code style={{
                            backgroundColor: 'var(--gray-4)',
                            padding: '2px 4px',
                            borderRadius: '4px',
                            fontSize: '13px',
                            fontFamily: 'monospace'
                          }}>
                            {children}
                          </code>
                        ) : (
                          <pre style={{
                            backgroundColor: 'var(--gray-4)',
                            padding: '8px',
                            borderRadius: '6px',
                            overflow: 'auto',
                            fontSize: '13px',
                            fontFamily: 'monospace',
                            margin: '8px 0'
                          }}>
                            <code>{children}</code>
                          </pre>
                        );
                      },
                      ul: ({ children }) => (
                        <ul style={{ paddingLeft: '16px', margin: '8px 0' }}>
                          {children}
                        </ul>
                      ),
                      ol: ({ children }) => (
                        <ol style={{ paddingLeft: '16px', margin: '8px 0' }}>
                          {children}
                        </ol>
                      ),
                      li: ({ children }) => (
                        <li style={{ marginBottom: '4px' }}>
                          <Text size="2">{children}</Text>
                        </li>
                      ),
                      strong: ({ children }) => (
                        <strong style={{ fontWeight: '600' }}>{children}</strong>
                      ),
                      em: ({ children }) => (
                        <em style={{ fontStyle: 'italic' }}>{children}</em>
                      ),
                      h1: ({ children }) => (
                        <Text size="5" weight="bold" style={{ display: 'block', margin: '12px 0 8px 0' }}>
                          {children}
                        </Text>
                      ),
                      h2: ({ children }) => (
                        <Text size="4" weight="bold" style={{ display: 'block', margin: '10px 0 6px 0' }}>
                          {children}
                        </Text>
                      ),
                      h3: ({ children }) => (
                        <Text size="3" weight="bold" style={{ display: 'block', margin: '8px 0 4px 0' }}>
                          {children}
                        </Text>
                      ),
                      blockquote: ({ children }) => (
                        <blockquote style={{
                          borderLeft: '3px solid var(--gray-6)',
                          paddingLeft: '12px',
                          margin: '8px 0',
                          fontStyle: 'italic',
                          color: 'var(--gray-11)'
                        }}>
                          {children}
                        </blockquote>
                      ),
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
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
