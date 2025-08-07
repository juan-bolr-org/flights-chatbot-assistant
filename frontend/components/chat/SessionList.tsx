'use client';

import { useState } from 'react';
import { 
  Box, 
  Text, 
  Flex, 
  Button, 
  Card, 
  Dialog, 
  TextField, 
  ScrollArea, 
  AlertDialog,
  IconButton 
} from '@radix-ui/themes';
import {
  PlusIcon,
  Pencil1Icon,
  TrashIcon,
  CheckIcon,
  Cross2Icon,
} from '@radix-ui/react-icons';
import { MessageSquare } from 'lucide-react';
import { ChatSession } from './types';

interface SessionListProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSessionSelect: (session: ChatSession) => void;
  onSessionCreate: (name: string) => void;
  onSessionDelete: (sessionId: string) => void;
  onSessionRename: (sessionId: string, newName: string) => void;
  newSessionTitle?: string;
  newSessionDescription?: string;
}

export function SessionList({
  sessions,
  currentSessionId,
  onSessionSelect,
  onSessionCreate,
  onSessionDelete,
  onSessionRename,
  newSessionTitle = "Create New Session",
  newSessionDescription = "Enter a name for your new chat session."
}: SessionListProps) {
  const [showNewSessionDialog, setShowNewSessionDialog] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editingSessionName, setEditingSessionName] = useState('');

  const handleCreateSession = () => {
    // Allow creating session with empty name (backend will generate default)
    onSessionCreate(newSessionName.trim());
    setNewSessionName('');
    setShowNewSessionDialog(false);
  };

  const handleRenameSession = (sessionId: string, newName: string) => {
    if (!newName.trim() || newName.toLowerCase() === 'default') {
      setEditingSessionId(null);
      return;
    }
    
    onSessionRename(sessionId, newName.trim());
    setEditingSessionId(null);
  };

  return (
    <Box style={{ width: '300px', minWidth: '300px' }}>
      <Flex direction="column" gap="3" style={{ height: '100%' }}>
        <Flex justify="between" align="center">
          <Text size="4" weight="bold">Chat Sessions</Text>
          <Dialog.Root open={showNewSessionDialog} onOpenChange={setShowNewSessionDialog}>
            <Dialog.Trigger>
              <Button size="2" variant="soft">
                <PlusIcon /> New
              </Button>
            </Dialog.Trigger>
            <Dialog.Content style={{ maxWidth: 450 }}>
              <Dialog.Title>{newSessionTitle}</Dialog.Title>
              <Dialog.Description size="2" mb="4">
                Enter a name for your new chat session, or leave blank for a default name (Chat #1, Chat #2, etc.).
              </Dialog.Description>

              <Flex direction="column" gap="3">
                <TextField.Root
                  placeholder="Session name (e.g., Flight Planning, Support Chat)"
                  value={newSessionName}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setNewSessionName(e.target.value)}
                  onKeyDown={(e: React.KeyboardEvent) => {
                    if (e.key === 'Enter') handleCreateSession();
                  }}
                />
              </Flex>

              <Flex gap="3" mt="4" justify="end">
                <Dialog.Close>
                  <Button variant="soft" color="gray">
                    Cancel
                  </Button>
                </Dialog.Close>
                <Button 
                  onClick={handleCreateSession}
                  disabled={newSessionName.toLowerCase() === 'default'}
                >
                  Create Session
                </Button>
              </Flex>
            </Dialog.Content>
          </Dialog.Root>
        </Flex>

        <ScrollArea style={{ flex: 1 }}>
          <Flex direction="column" gap="2">
            {sessions.map((session) => (
              <Card
                key={session.session_id}
                style={{
                  cursor: 'pointer',
                  backgroundColor: currentSessionId === session.session_id ? 'var(--accent-3)' : undefined,
                  border: currentSessionId === session.session_id ? '1px solid var(--accent-7)' : undefined,
                }}
                onClick={() => onSessionSelect(session)}
              >
                <Flex justify="between" align="center" p="2">
                  <Flex direction="column" gap="1" style={{ flex: 1 }}>
                    {editingSessionId === session.session_id ? (
                      <TextField.Root
                        size="1"
                        value={editingSessionName}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setEditingSessionName(e.target.value)}
                        onKeyDown={(e: React.KeyboardEvent) => {
                          if (e.key === 'Enter') handleRenameSession(session.session_id, editingSessionName);
                          if (e.key === 'Escape') setEditingSessionId(null);
                        }}
                        onBlur={() => handleRenameSession(session.session_id, editingSessionName)}
                        autoFocus
                        onClick={(e: React.MouseEvent) => e.stopPropagation()}
                      />
                    ) : (
                      <Text size="2" weight="medium" truncate>
                        {session.alias}
                      </Text>
                    )}
                    <Text size="1" color="gray">
                      {session.message_count} messages
                    </Text>
                  </Flex>
                  
                  <Flex gap="1" onClick={(e) => e.stopPropagation()}>
                    {editingSessionId === session.session_id ? (
                      <>
                        <IconButton
                          size="1"
                          variant="ghost"
                          onClick={() => handleRenameSession(session.session_id, editingSessionName)}
                        >
                          <CheckIcon />
                        </IconButton>
                        <IconButton
                          size="1"
                          variant="ghost"
                          onClick={() => setEditingSessionId(null)}
                        >
                          <Cross2Icon />
                        </IconButton>
                      </>
                    ) : (
                      <IconButton
                        size="1"
                        variant="ghost"
                        onClick={() => {
                          setEditingSessionId(session.session_id);
                          setEditingSessionName(session.alias);
                        }}
                      >
                        <Pencil1Icon />
                      </IconButton>
                    )}
                    
                    <AlertDialog.Root>
                      <AlertDialog.Trigger>
                        <IconButton size="1" variant="ghost" color="red">
                          <TrashIcon />
                        </IconButton>
                      </AlertDialog.Trigger>
                      <AlertDialog.Content style={{ maxWidth: 450 }}>
                        <AlertDialog.Title>Delete Session</AlertDialog.Title>
                        <AlertDialog.Description size="2">
                          Are you sure you want to delete "{session.alias}"? This action cannot be undone.
                        </AlertDialog.Description>

                        <Flex gap="3" mt="4" justify="end">
                          <AlertDialog.Cancel>
                            <Button variant="soft" color="gray">Cancel</Button>
                          </AlertDialog.Cancel>
                          <AlertDialog.Action>
                            <Button variant="solid" color="red" onClick={() => onSessionDelete(session.session_id)}>
                              Delete Session
                            </Button>
                          </AlertDialog.Action>
                        </Flex>
                      </AlertDialog.Content>
                    </AlertDialog.Root>
                  </Flex>
                </Flex>
              </Card>
            ))}
            
            {sessions.length === 0 && (
              <Card>
                <Flex direction="column" align="center" gap="2" p="4">
                  <MessageSquare size={32} color="var(--gray-9)" />
                  <Text size="2" color="gray" align="center">
                    No sessions yet. Create your first session to start chatting!
                  </Text>
                </Flex>
              </Card>
            )}
          </Flex>
        </ScrollArea>
      </Flex>
    </Box>
  );
}
