'use client';

import { useState } from 'react';
import { IconButton } from '@radix-ui/themes';
import { ChatBubbleIcon } from '@radix-ui/react-icons';
import { ChatPanel } from './ChatPanel';

export function FloatingChatButton() {
  const [open, setOpen] = useState(false);
  const [messageCount, setMessageCount] = useState(0);

  return (
    <div style={{ zIndex: 50, position: 'fixed', bottom: '2rem', right: '2rem' }}>
      <IconButton
        size="3"
        radius="full"
        style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          zIndex: 50,
          boxShadow: '0 4px 10px rgba(0, 0, 0, 0.15)',
        }}
        onClick={() => setOpen(!open)}
      >
        <ChatBubbleIcon />
      </IconButton>
      <ChatPanel open={open} onOpenChange={setOpen} messageCount={messageCount} setMessageCount={setMessageCount} />
      {messageCount > 0 && (
        <div
          style={{
            position: 'fixed',
            bottom: '3.5rem',
            right: '2rem',
            backgroundColor: 'red',
            color: 'white',
            borderRadius: '50%',
            width: '1.5rem',
            height: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.75rem',
            zIndex: 60,
          }}
        >
          {messageCount}
        </div>
      )}
    </div>
  );
}
