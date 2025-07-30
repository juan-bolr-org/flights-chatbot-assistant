'use client';

import { useState } from 'react';
import { Box, TextArea, Button, ScrollArea, Text, Flex } from '@radix-ui/themes';
import { sendChatMessage } from '@/lib/api/chat';

type Message = {
    role: 'user' | 'bot';
    content: string;
};

export function ChatPanel() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { role: 'user', content: input };
        setMessages((prev) => [...prev, userMessage]);
        setInput('');
        setLoading(true);

        try {
            const botResponse = await sendChatMessage(userMessage.content);
            const botMessage: Message = { role: 'bot', content: botResponse };
            setMessages((prev) => [...prev, botMessage]);
        } catch (err) {
            setMessages((prev) => [
                ...prev,
                { role: 'bot', content: 'Error on server.' },
            ]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Flex direction="column" flexGrow="1" justify="between" mt="4">
            <ScrollArea
                type="always"
                scrollbars="vertical"
                style={{ height: '100%', maxHeight: '250px' }}
            >
                <Flex direction="column" gap="2">
                    {messages.map((msg, idx) => (
                        <Box
                            key={idx}
                            p="3"
                            m="3"
                            style={{
                                backgroundColor: msg.role === 'user' ? '#292727ff' : '#383838ff',
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

            <Flex mt="3" gap="2" align="center">
                <TextArea
                    placeholder="Write your message..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    style={{ flex: 1 }}
                />
                <Button size="2" onClick={handleSend} disabled={loading}>
                    {loading ? '...' : 'Send'}
                </Button>
            </Flex>
        </Flex>
    );
}
