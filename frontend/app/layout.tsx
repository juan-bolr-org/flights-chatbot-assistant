// app/layout.tsx
import "@/styles/global.css";
import "@radix-ui/themes/styles.css";

import { Theme, Flex, Container } from "@radix-ui/themes";
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';
import { Inter } from "next/font/google";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { Providers } from './providers';

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${inter.className} text-gray-900`}>
        <Theme appearance="dark">
          <Providers>
            <Flex direction="column" justify="between" className="min-h-screen">
              <Header />
              <Container flexGrow="1">{children}</Container>
              <Footer />
            </Flex>
            <FloatingChatButton />
          </Providers>
        </Theme>
      </body>
    </html>
  );
}
