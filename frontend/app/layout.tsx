'use client';

import "@/styles/global.css";
import "@radix-ui/themes/styles.css";

import { useState } from "react";
import { Theme, Flex, Container } from "@radix-ui/themes";
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';
import { Inter } from "next/font/google";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { UserContext } from "@/contexts/UserContext";

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<{ name: string } | null>({ name: 'polvora' });

  return (
    <html lang="es">
      <body className={`${inter.className} text-gray-900`}>
        <Theme appearance="dark">
          <UserContext.Provider value={{ user, setUser }}>
            <Flex direction="column" justify="between" className="min-h-screen">
              <Header />
              <Container flexGrow={"1"}>{children}</Container>
              <Footer />
            </Flex>
            <FloatingChatButton />
          </UserContext.Provider>
        </Theme>
      </body>
    </html>
  );
}
