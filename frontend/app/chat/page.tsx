'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  Container,
  Section,
  Box,
  Text,
  Flex,
} from '@radix-ui/themes';
import { MessageSquare } from 'lucide-react';
import { useUser } from '@/context/UserContext';
import { ChatMessages } from '@/components/chat/ChatMessages';
import { ChatInput } from '@/components/chat/ChatInput';
import { ChatHeader } from '@/components/chat/ChatHeader';
import { SessionList } from '@/components/chat/SessionList';
import { useChatInterface } from '@/components/chat/useChatInterface';
import {
  getChatSessions,
  deleteSession,
  createSession,
  updateSessionAlias,
} from '@/lib/api/chat';
import { ChatSession } from '@/components/chat/types';

export default function ChatPage() {
  const { user, loading: userLoading } = useUser();
  const router = useRouter();

  // Session management
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const [currentSessionName, setCurrentSessionName] = useState<string>('');

  // Use the shared chat interface for the current session
  const {
    messages,
    loading,
    isLoadingHistory,
    isClearingChat,
    sendMessage,
    clearChat,
    loadHistory,
    canClearChat,
    setMessages
  } = useChatInterface({
    sessionId: currentSessionId || 'default',
    defaultWelcomeMessage: "Hello! How can I assist you today? Feel free to ask me anything about flights, bookings, or travel information.",
    loadHistoryOnMount: false // We'll manage loading manually for session switching
  });

  // Load sessions on mount
  useEffect(() => {
    if (user?.token) {
      loadSessions();
    }
  }, [user]);

  const loadSessions = async () => {
    try {
      if (!user?.token) return;
      
      const response = await getChatSessions(user.token.access_token);
      
      // Convert API sessions to ChatSession format
      const sessionData: ChatSession[] = response.sessions.map(sessionInfo => {
        return {
          session_id: sessionInfo.session_id,
          alias: sessionInfo.alias,
          message_count: sessionInfo.message_count,
          created_at: sessionInfo.created_at,
          updated_at: sessionInfo.updated_at,
        };
      });

      setSessions(sessionData);

      // If no current session and we have sessions, select the first one
      if (!currentSessionId && sessionData.length > 0) {
        setCurrentSessionId(sessionData[0].session_id);
        setCurrentSessionName(sessionData[0].alias);
        await loadHistory(sessionData[0].session_id);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const createNewSession = async (sessionName: string) => {
    if (!user?.token) return;
    
    try {
      // Call API to create session
      const response = await createSession(user.token.access_token, {
        alias: sessionName.trim() || undefined // Let backend generate default if empty
      });

      const newSession: ChatSession = {
        session_id: response.session_id,
        alias: response.alias,
        message_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setSessions(prev => [newSession, ...prev]);
      setCurrentSessionId(response.session_id);
      setCurrentSessionName(response.alias);
      setMessages([
        { 
          role: 'bot', 
          content: `Welcome to "${response.alias}"! How can I help you today?`,
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const selectSession = async (session: ChatSession) => {
    setCurrentSessionId(session.session_id);
    setCurrentSessionName(session.alias);
    await loadHistory(session.session_id);
  };

  const deleteSessionHandler = async (sessionId: string) => {
    try {
      if (!user?.token) return;

      await deleteSession(user.token.access_token, sessionId);
      
      setSessions(prev => prev.filter(s => s.session_id !== sessionId));
      
      if (currentSessionId === sessionId) {
        const remainingSessions = sessions.filter(s => s.session_id !== sessionId);
        if (remainingSessions.length > 0) {
          await selectSession(remainingSessions[0]);
        } else {
          setCurrentSessionId(null);
          setCurrentSessionName('');
          setMessages([]);
        }
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  const renameSession = async (sessionId: string, newName: string) => {
    if (!newName.trim() || newName.toLowerCase() === 'default' || !user?.token) {
      return;
    }

    try {
      // Call API to update session alias
      await updateSessionAlias(user.token.access_token, sessionId, {
        alias: newName.trim()
      });
      
      setSessions(prev => prev.map(s => 
        s.session_id === sessionId ? { ...s, alias: newName.trim() } : s
      ));
      
      if (currentSessionId === sessionId) {
        setCurrentSessionName(newName.trim());
      }
    } catch (error) {
      console.error('Error renaming session:', error);
    }
  };

  const handleSendMessage = async (messageContent: string) => {
    if (!currentSessionId) return;
    
    await sendMessage(messageContent);
    
    // Update session activity
    setSessions(prev => prev.map(s => 
      s.session_id === currentSessionId 
        ? { ...s, updated_at: new Date().toISOString(), message_count: s.message_count + 1 }
        : s
    ));
  };

  const handleClearChat = async () => {
    await clearChat();
  };

  // Show loading while checking authentication status
  if (userLoading) {
    return (
      <div className="p-4 text-center">
        <Text>Loading...</Text>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    router.replace('/login');
    return null;
  }

  return (
    <Container size="4">
      <Section py="4">
        <Flex direction="row" gap="4" style={{ height: '80vh' }}>
          {/* Sidebar - Sessions */}
          <SessionList
            sessions={sessions}
            currentSessionId={currentSessionId}
            onSessionSelect={selectSession}
            onSessionCreate={createNewSession}
            onSessionDelete={deleteSessionHandler}
            onSessionRename={renameSession}
          />

          {/* Main Chat Area */}
          <Box style={{ flex: 1 }}>
            {currentSessionId ? (
              <Flex direction="column" style={{ height: '100%' }}>
                {/* Chat Header */}
                <ChatHeader
                  title={currentSessionName}
                  onClearChat={handleClearChat}
                  showCloseButton={false}
                  showClearButton={true}
                  isClearing={isClearingChat}
                  canClear={!!canClearChat}
                />

                {/* Messages */}
                <ChatMessages 
                  messages={messages} 
                  isLoadingHistory={isLoadingHistory} 
                />

                {/* Input Area */}
                {user?.token && (
                  <ChatInput
                    onSendMessage={handleSendMessage}
                    onAudioMessage={handleSendMessage}
                    disabled={loading}
                    token={user.token.access_token}
                    placeholder="Type your message..."
                    showAudioRecorder={true}
                  />
                )}
              </Flex>
            ) : (
              <Flex direction="column" align="center" justify="center" style={{ height: '100%' }}>
                <MessageSquare size={64} color="var(--gray-9)" />
                <Text size="4" weight="bold" mt="4" mb="2">
                  Welcome to Chat
                </Text>
                <Text size="2" color="gray" align="center" mb="4">
                  Create a new session or select an existing one to start chatting
                </Text>
                <Text size="2" color="gray" align="center">
                  Use the "New" button in the sidebar to create your first session
                </Text>
              </Flex>
            )}
          </Box>
        </Flex>
      </Section>
    </Container>
  );
}
