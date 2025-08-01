'use client';

import { useState } from 'react';
import { Dialog, IconButton, Flex, Button } from '@radix-ui/themes';
import { ChatBubbleIcon, ExitIcon } from '@radix-ui/react-icons';
import { ChatPanel } from './ChatPanel';

export function FloatingChatButton() {
  const [open, setOpen] = useState(false);

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
      <ChatPanel open={open} onOpenChange={setOpen} />
    </div>
  );
}
