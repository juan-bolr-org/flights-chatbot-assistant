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

    // <Dialog.Root defaultOpen={true} open={open} onOpenChange={setOpen}>
    //   <Dialog.Trigger>
    //     <IconButton
    //       size="3"
    //       radius="full"
    //       style={{
    //         position: 'fixed',
    //         bottom: '2rem',
    //         right: '2rem',
    //         zIndex: 50,
    //         boxShadow: '0 4px 10px rgba(0, 0, 0, 0.15)',
    //       }}
    //     >
    //       <ChatBubbleIcon />
    //     </IconButton>
    //   </Dialog.Trigger>
    //   <Dialog.Content style={{ width: 420, height: 520 }}>
    //     <Flex direction="column" height="100%">
    //       <Flex direction="row" justify="between" align="center" mb="4">
    //         <Flex direction="column">
    //           <Dialog.Title>Assistant</Dialog.Title>
    //           <Dialog.Description>How can I help you?</Dialog.Description>
    //         </Flex>

    //         <Dialog.Close>
    //           <Button variant="soft" color="gray">
    //             <ExitIcon />
    //           </Button>
    //         </Dialog.Close>
    //       </Flex>
    //       <ChatPanel />
    //     </Flex>
    //   </Dialog.Content>
    // </Dialog.Root>
  );
}
