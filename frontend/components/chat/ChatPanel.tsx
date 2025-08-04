'use client';

import { useState, useEffect } from 'react';
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
import { sendChatMessage } from '@/lib/api/chat';
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
    const [messages, setMessages] = useState<Message[]>([
        { role: 'bot', content: 'Hello! How can I assist you today?' },
        { role: 'bot', content: 'Feel free to ask me anything about your flight.' },
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const { user } = useUser();

    useEffect(() => {
        if (open) {
            setMessageCount(0);
        }
    }, [open]);

    useEffect(() => {
        if (messages[messages.length - 1].role === 'bot' && !open) {
            setMessageCount(messageCount + 1);
        }

    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            console.log("user", user);
            if (user && user.token) {
                const botResponse = await sendChatMessage(user.token.access_token, userMessage.content);
                const botMessage: Message = { role: 'bot', content: botResponse };
                setMessageCount(messageCount + 1);
                setMessages((prev) => [...prev, botMessage]);
            } else {
                setMessages((prev) => [
                    ...prev,
                    { role: 'bot', content: 'Please log in to send messages.' },
                ]);
            }

        } catch {
            setMessages((prev) => [
                ...prev,
                { role: 'bot', content: 'Error on server.' },
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
                    {messages.map((msg, idx) => (
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
                    ))}
                </Flex>
            </ScrollArea>


            {user ? (
                <Flex mt="3" gap="2" align="center">
                    <TextArea
                        placeholder="Write your message..."
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        style={{ flex: 1 }}
                    />
                    <Button size="2" onClick={handleSend} disabled={loading}>
                        {loading ? '...' : <PaperPlaneIcon />}
                    </Button>
                </Flex>
            ) : (
                <Callout.Root color="orange">
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
