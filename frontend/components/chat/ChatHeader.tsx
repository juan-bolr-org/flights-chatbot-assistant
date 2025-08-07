'use client';

import { Button, Text, Flex, AlertDialog } from '@radix-ui/themes';
import { ExitIcon, TrashIcon, ChatBubbleIcon } from '@radix-ui/react-icons';

interface ChatHeaderProps {
  title: string;
  onClose?: () => void;
  onClearChat?: () => void;
  showCloseButton?: boolean;
  showClearButton?: boolean;
  isClearing?: boolean;
  canClear?: boolean;
}

export function ChatHeader({ 
  title, 
  onClose, 
  onClearChat, 
  showCloseButton = false,
  showClearButton = true,
  isClearing = false,
  canClear = true
}: ChatHeaderProps) {
  return (
    <Flex justify="between" align="center" mb="3" p="3" style={{
      borderBottom: '1px solid var(--gray-6)',
    }}>
      <Flex align="center" gap="2">
        <ChatBubbleIcon />
        <Text size="4" weight="bold">{title}</Text>
      </Flex>
      
      <Flex gap="2" align="center">
        {showClearButton && onClearChat && (
          <AlertDialog.Root>
            <AlertDialog.Trigger>
              <Button
                variant={showCloseButton ? "ghost" : "soft"}
                size="2"
                color="red"
                disabled={isClearing || !canClear}
                title="Clear chat history"
              >
                {isClearing ? '...' : <TrashIcon />}
                {!showCloseButton && " Clear Chat"}
              </Button>
            </AlertDialog.Trigger>
            <AlertDialog.Content style={{ maxWidth: 450 }}>
              <AlertDialog.Title>Clear Chat History</AlertDialog.Title>
              <AlertDialog.Description size="2">
                Are you sure you want to clear all chat history? This action cannot be undone.
              </AlertDialog.Description>

              <Flex gap="3" mt="4" justify="end">
                <AlertDialog.Cancel>
                  <Button variant="soft" color="gray">
                    Cancel
                  </Button>
                </AlertDialog.Cancel>
                <AlertDialog.Action>
                  <Button variant="solid" color="red" onClick={onClearChat}>
                    Clear Chat
                  </Button>
                </AlertDialog.Action>
              </Flex>
            </AlertDialog.Content>
          </AlertDialog.Root>
        )}
        
        {showCloseButton && onClose && (
          <Button
            variant="ghost"
            size="2"
            onClick={onClose}
          >
            <ExitIcon />
          </Button>
        )}
      </Flex>
    </Flex>
  );
}
