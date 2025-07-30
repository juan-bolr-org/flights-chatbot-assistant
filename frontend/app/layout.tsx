import "@/styles/global.css";
import "@radix-ui/themes/styles.css";

import { Theme, Flex, Container } from "@radix-ui/themes";
import { FloatingChatButton } from '@/components/chat/FloatingChatButton';
import { Inter } from "next/font/google";
import type { Metadata, Viewport } from "next";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Flight Assistant",
  description: "Woohooo flights",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es">
      <body className={`${inter.className} text-gray-900`}>
        <Theme appearance="dark">
          <Flex direction="column" justify="between" className="min-h-screen">
            <Header />
            <Container flexGrow={"1"}>{children}</Container>
            <Footer />
            <FloatingChatButton />
          </Flex>
        </Theme>
      </body>
    </html>
  );
}
