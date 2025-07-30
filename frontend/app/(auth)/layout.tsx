import { Container } from "@radix-ui/themes";
import { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Sign In - Flight Assistant Chatbot',
    description: 'Sign in to the Flight Assistant Chatbot',
}

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <Container flexGrow="1">
            {children}
        </Container>
    )
} 