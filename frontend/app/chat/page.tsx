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

  const generateSessionId = () => {
    return Date.now().toString() + '_' + Math.random().toString(36).substr(2, 9);
  };

  const loadSessions = async () => {
    try {
      if (!user?.token) return;
      
      const response = await getChatSessions(user.token.access_token);
      
      // Convert API sessions to ChatSession format with names from localStorage
      const sessionData: ChatSession[] = response.sessions.map(sessionId => {
        const storedName = localStorage.getItem(`session_name_${sessionId}`);
        return {
          id: sessionId,
          name: storedName || `Session ${sessionId.slice(-8)}`,
          lastActivity: new Date().toISOString(),
          messageCount: 0,
        };
      });

      setSessions(sessionData);

      // If no current session and we have sessions, select the first one
      if (!currentSessionId && sessionData.length > 0) {
        setCurrentSessionId(sessionData[0].id);
        setCurrentSessionName(sessionData[0].name);
        await loadHistory(sessionData[0].id);
      }
    } catch (error) {
      console.error('Error loading sessions:', error);
    }
  };

  const createNewSession = async (sessionName: string) => {
    if (!sessionName.trim() || sessionName.toLowerCase() === 'default') {
      return;
    }

    const sessionId = generateSessionId();
    const newSession: ChatSession = {
      id: sessionId,
      name: sessionName.trim(),
      lastActivity: new Date().toISOString(),
      messageCount: 0,
    };

    // Save session name to localStorage
    localStorage.setItem(`session_name_${sessionId}`, newSession.name);

    setSessions(prev => [newSession, ...prev]);
    setCurrentSessionId(sessionId);
    setCurrentSessionName(newSession.name);
    setMessages([
      { 
        role: 'bot', 
        content: `Welcome to "${newSession.name}"! How can I help you today?`,
        timestamp: new Date()
      }
    ]);
  };

  const selectSession = async (session: ChatSession) => {
    setCurrentSessionId(session.id);
    setCurrentSessionName(session.name);
    await loadHistory(session.id);
  };

  const deleteSessionHandler = async (sessionId: string) => {
    try {
      if (!user?.token) return;

      await deleteSession(user.token.access_token, sessionId);
      
      // Remove from localStorage
      localStorage.removeItem(`session_name_${sessionId}`);
      
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      
      if (currentSessionId === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId);
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

  const renameSession = (sessionId: string, newName: string) => {
    if (!newName.trim() || newName.toLowerCase() === 'default') {
      return;
    }

    // Update localStorage
    localStorage.setItem(`session_name_${sessionId}`, newName.trim());
    
    setSessions(prev => prev.map(s => 
      s.id === sessionId ? { ...s, name: newName.trim() } : s
    ));
    
    if (currentSessionId === sessionId) {
      setCurrentSessionName(newName.trim());
    }
  };

  const handleSendMessage = async (messageContent: string) => {
    if (!currentSessionId) return;
    
    await sendMessage(messageContent);
    
    // Update session activity
    setSessions(prev => prev.map(s => 
      s.id === currentSessionId 
        ? { ...s, lastActivity: new Date().toISOString(), messageCount: s.messageCount + 1 }
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
                  canClear={canClearChat}
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
