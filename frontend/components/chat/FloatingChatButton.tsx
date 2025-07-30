'use client';

import { useState } from 'react';
import { Dialog, Button, IconButton, Flex } from '@radix-ui/themes';
import { ChatBubbleIcon } from '@radix-ui/react-icons';
import { ChatPanel } from './ChatPanel';

export function FloatingChatButton() {
  const [open, setOpen] = useState(false);

  return (
    <Dialog.Root open={open} onOpenChange={setOpen}>
      <Dialog.Trigger>
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
        >
          <ChatBubbleIcon />
        </IconButton>
      </Dialog.Trigger>

      <Dialog.Content style={{ width: 420, height: 520 }}>
        <Flex direction="column" height="100%">
          <Dialog.Title>Asistente</Dialog.Title>
          <Dialog.Description>How can I help you?</Dialog.Description>
          <ChatPanel />
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
}
