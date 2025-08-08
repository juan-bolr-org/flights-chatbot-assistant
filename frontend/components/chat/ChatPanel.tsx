'use client';

import { Flex, Callout } from '@radix-ui/themes';
import { AlertCircleIcon } from 'lucide-react';
import { useChatInterface } from './useChatInterface';
import { ChatHeader } from './ChatHeader';
import { ChatMessages } from './ChatMessages';
import { ChatInput } from './ChatInput';

export function ChatPanel({
    open,
    onOpenChange
}: {
    open: boolean;
    onOpenChange: (open: boolean) => void;
}) {

    // Use a fixed session ID for the floating panel so users always see the same chat
    const sessionId = `chat-session`;

    const {
        messages,
        loading,
        isLoadingHistory,
        isClearingChat,
        sendMessage,
        clearChat,
        canClearChat,
        user,
    } = useChatInterface({
        sessionId: sessionId,
        defaultWelcomeMessage: "Hello! How can I assist you today?\nFeel free to ask me anything about your flight."
    });

    if (!open) return null;

    return (
        <Flex direction="column" flexGrow="1" justify="between" mt="4" className="openChat">
            <ChatHeader
                title="Flight Assistant Chatbot"
                onClose={() => onOpenChange(false)}
                onClearChat={clearChat}
                showCloseButton={true}
                showClearButton={true}
                isClearing={isClearingChat}
                canClear={!!canClearChat}
            />

            <ChatMessages
                messages={messages}
                isLoadingHistory={isLoadingHistory}
            />

            {user?.token ? (
                <ChatInput
                    onSendMessage={sendMessage}
                    onAudioMessage={sendMessage}
                    disabled={loading}
                    token={user.token.access_token}
                    placeholder="Write your message..."
                    showAudioRecorder={true}
                />
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
