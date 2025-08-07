'use client';

import { useState, useEffect, useRef } from 'react';
import { sendChatMessage, getChatHistory, deleteChatHistory } from '@/lib/api/chat';
import { useUser } from '@/context/UserContext';
import { ChatMessage, ChatResponse, hasTimestamp } from './types';

interface UseChatInterfaceProps {
  sessionId: string;
  onMessageCountChange?: (count: number) => void;
  defaultWelcomeMessage?: string;
  loadHistoryOnMount?: boolean;
}

export function useChatInterface({ 
  sessionId, 
  onMessageCountChange,
  defaultWelcomeMessage = "Hello! How can I assist you today?",
  loadHistoryOnMount = true
}: UseChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(loadHistoryOnMount);
  const [isClearingChat, setIsClearingChat] = useState(false);
  const { user } = useUser();
  
  const hasFetchedHistory = useRef(false);

  // Load chat history when component mounts or user changes
  useEffect(() => {
    if (!loadHistoryOnMount) return;
    
    const loadChatHistory = async () => {
      if (!user?.token) {
        // If no user, show login message
        setMessages([
          { role: 'bot', content: 'Please login to use the chat.' },
        ]);
        setIsLoadingHistory(false);
        return;
      }

      if (hasFetchedHistory.current) {
        setIsLoadingHistory(false);
        return;
      }

      hasFetchedHistory.current = true;
      setIsLoadingHistory(true);

      try {
        const history = await getChatHistory(user.token.access_token, sessionId);
        
        if (history.messages && history.messages.length > 0) {
          // Convert backend chat history to frontend message format
          const chatMessages: ChatMessage[] = [];
          history.messages.forEach(msg => {
            chatMessages.push(
              { role: 'user', content: msg.message, timestamp: new Date(msg.created_at) },
              { role: 'bot', content: msg.response, timestamp: new Date(msg.created_at) }
            );
          });
          setMessages(chatMessages);
        } else {
          // If no history, show default messages
          setMessages([
            { role: 'bot', content: defaultWelcomeMessage, timestamp: new Date() }
          ]);
        }
      } catch (error) {
        console.error('Error loading chat history:', error);
        // On error, show unavailable message
        setMessages([
          { role: 'bot', content: 'Sorry, chat is not available at the moment.', timestamp: new Date() },
        ]);
      } finally {
        setIsLoadingHistory(false);
      }
    };

    loadChatHistory();
  }, [user, sessionId, defaultWelcomeMessage, loadHistoryOnMount]);

  // Reset fetch flag when user changes
  useEffect(() => {
    hasFetchedHistory.current = false;
  }, [user?.id]);

  // Handle message count changes
  useEffect(() => {
    if (messages.length > 0 && messages[messages.length - 1].role === 'bot' && onMessageCountChange) {
      onMessageCountChange(1);
    }
  }, [messages, onMessageCountChange]);

  const sendMessage = async (messageContent: string): Promise<void> => {
    if (!messageContent.trim()) return;

    const userMessage: ChatMessage = { 
      role: 'user', 
      content: messageContent, 
      timestamp: new Date() 
    };
    setMessages(prev => [...prev, userMessage]);
    setLoading(true);

    try {
      if (user && user.token) {
        const chatResponse: ChatResponse = await sendChatMessage(
          user.token.access_token, 
          messageContent, 
          sessionId
        );
        const botMessage: ChatMessage = { 
          role: 'bot', 
          content: chatResponse.response, 
          timestamp: new Date() 
        };
        setMessages(prev => [...prev, botMessage]);
      } else {
        setMessages(prev => [
          ...prev,
          { role: 'bot', content: 'Please log in to send messages.', timestamp: new Date() },
        ]);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Sorry, chat is not available at the moment.', timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = async (): Promise<void> => {
    if (!user?.token) return;

    setIsClearingChat(true);
    try {
      await deleteChatHistory(user.token.access_token, sessionId);
      
      // Reset messages to default welcome messages with success notification
      setMessages([
        { role: 'bot', content: 'Chat history has been cleared successfully! 🗑️', timestamp: new Date() },
        { role: 'bot', content: defaultWelcomeMessage, timestamp: new Date() },
      ]);
      
      // Reset the fetch flag so history can be loaded again if needed
      hasFetchedHistory.current = false;
      
    } catch (error) {
      console.error('Error clearing chat history:', error);
      setMessages(prev => [
        ...prev,
        { role: 'bot', content: 'Sorry, there was an error clearing the chat history.', timestamp: new Date() },
      ]);
    } finally {
      setIsClearingChat(false);
    }
  };

  const loadHistory = async (newSessionId?: string): Promise<void> => {
    const targetSessionId = newSessionId || sessionId;
    setIsLoadingHistory(true);
    
    try {
      if (!user?.token) return;

      const history = await getChatHistory(user.token.access_token, targetSessionId);
      
      if (history.messages && history.messages.length > 0) {
        const chatMessages: ChatMessage[] = [];
        history.messages.forEach(msg => {
          chatMessages.push(
            { role: 'user', content: msg.message, timestamp: new Date(msg.created_at) },
            { role: 'bot', content: msg.response, timestamp: new Date(msg.created_at) }
          );
        });
        setMessages(chatMessages);
      } else {
        setMessages([
          { role: 'bot', content: defaultWelcomeMessage, timestamp: new Date() }
        ]);
      }
    } catch (error) {
      console.error('Error loading chat history:', error);
      setMessages([
        { role: 'bot', content: 'Sorry, I couldn\'t load the chat history for this session.', timestamp: new Date() }
      ]);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  const canClearChat = user && (
    messages.length > 0 && 
    !(messages.length <= 2 && messages.every(msg => msg.role === 'bot'))
  );

  return {
    messages,
    loading,
    isLoadingHistory,
    isClearingChat,
    user,
    sendMessage,
    clearChat,
    loadHistory,
    canClearChat: canClearChat,
    setMessages
  };
}
