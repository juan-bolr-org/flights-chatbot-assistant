'use client';

import { useState, useEffect, useRef } from 'react';
import {
    Box,
    TextArea,
    Button,
    ScrollArea,
    Text,
    Flex,
    Callout,
} from '@radix-ui/themes';
import { ExitIcon, PaperPlaneIcon } from '@radix-ui/react-icons';
import { sendChatMessage, getChatHistory } from '@/lib/api/chat';
import { AlertCircleIcon } from 'lucide-react';
import { useUser } from '@/context/UserContext';

type Message = {
    role: 'user' | 'bot';
    content: string;
};

export function ChatPanel({
    open,
    onOpenChange,
    messageCount,
    setMessageCount,
}: {
    open: boolean;
    messageCount: number;
    onOpenChange: (open: boolean) => void;
    setMessageCount: (count: number) => void;
}) {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [isLoadingHistory, setIsLoadingHistory] = useState(true);
    const { user } = useUser();

    const bottomRef = useRef<HTMLElement | null>(null);
    const hasFetchedHistory = useRef(false);

    // Load chat history when component mounts or user changes
    useEffect(() => {
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
                const history = await getChatHistory(user.token.access_token);
                
                if (history.messages && history.messages.length > 0) {
                    // Convert backend chat history to frontend message format
                    const chatMessages: Message[] = [];
                    history.messages.forEach(msg => {
                        chatMessages.push(
                            { role: 'user', content: msg.message },
                            { role: 'bot', content: msg.response }
                        );
                    });
                    setMessages(chatMessages);
                } else {
                    // If no history, show default messages
                    setMessages([
                        { role: 'bot', content: 'Hello! How can I assist you today?' },
                        { role: 'bot', content: 'Feel free to ask me anything about your flight.' },
                    ]);
                }
            } catch (error) {
                console.error('Error loading chat history:', error);
                // On error, show unavailable message
                setMessages([
                    { role: 'bot', content: 'Sorry, chat is not available at the moment.' },
                ]);
            } finally {
                setIsLoadingHistory(false);
            }
        };

        loadChatHistory();
    }, [user]);

    // Reset fetch flag when user changes
    useEffect(() => {
        hasFetchedHistory.current = false;
    }, [user?.id]);

    useEffect(() => {
        if (open) {
            setMessageCount(0);
        }
    }, [open]);

    useEffect(() => {
        if (messages.length > 0 && messages[messages.length - 1].role === 'bot' && !open) {
            setMessageCount(messageCount + 1);
        }
    }, [messages]);

    // Scroll automático al final
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages((prev: Message[]) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            if (user && user.token) {
                const botResponse = await sendChatMessage(user.token.access_token, userMessage.content);
                const botMessage: Message = { role: 'bot', content: botResponse };
                setMessageCount(messageCount + 1);
                setMessages((prev: Message[]) => [...prev, botMessage]);
            } else {
                setMessages((prev: Message[]) => [
                    ...prev,
                    { role: 'bot', content: 'Please log in to send messages.' },
                ]);
            }

        } catch {
            setMessages((prev: Message[]) => [
                ...prev,
                { role: 'bot', content: 'Sorry, chat is not available at the moment.' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    if (!open) return null;

    return (
        <Flex direction="column" flexGrow="1" justify="between" mt="4" className="openChat">
            <Flex direction="row" justify="between" align="center" mb="4">
                <Text size="3" weight="bold">Flight Assistant Chatbot</Text>
                <Button
                    variant="ghost"
                    size="2"
                    onClick={() => onOpenChange(false)}
                >
                    <ExitIcon />
                </Button>
            </Flex>

            <ScrollArea
                type="always"
                scrollbars="vertical"
                style={{ height: '100%', maxHeight: '100%' }}
            >
                <Flex direction="column" gap="2">
                    {isLoadingHistory ? (
                        <Box p="3" m="3">
                            <Text size="2">Loading chat history...</Text>
                        </Box>
                    ) : (
                        messages.map((msg: Message, idx: number) => (
                            <Box
                                key={idx}
                                p="3"
                                m="3"
                                style={{
                                    backgroundColor: msg.role === 'user' ? '#292727' : '#383838',
                                    borderRadius: 6,
                                    alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                                    maxWidth: '80%',
                                }}
                            >
                                <Text size="2">{msg.content}</Text>
                            </Box>
                        ))
                    )}
                    <Box ref={bottomRef} />
                </Flex>
            </ScrollArea>

            {user ? (
                <Flex mt="3" gap="2" align="center">
                    <TextArea
                        placeholder="Write your message..."
                        value={input}
                        onChange={(e: { target: { value: string } }) => setInput(e.target.value)}
                        onKeyDown={(e: { key: string; shiftKey: boolean; preventDefault: () => void }) => {
                            if (e.key === 'Enter' && !e.shiftKey) {
                                e.preventDefault();
                                handleSend();
                            }
                        }}
                        style={{ flex: 1 }}
                    />
                    <Button size="2" onClick={handleSend} disabled={loading}>
                        {loading ? '...' : <PaperPlaneIcon />}
                    </Button>
                </Flex>
            ) : (
                <Callout.Root color="orange" mt="3">
                    <Callout.Icon>
                        <AlertCircleIcon />
                    </Callout.Icon>
                    <Callout.Text>
                        Please log in to send messages.
                    </Callout.Text>
                </Callout.Root>
            )}
        </Flex>
    );
}
