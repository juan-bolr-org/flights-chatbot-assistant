// components/Footer.tsx
'use client';

import { Box, Text, Flex } from "@radix-ui/themes";
import Link from "next/link";

export default function Footer() {
    return (

        <Flex
            direction="column"
            justify="between"
            gap="6"
            py="6"
        >
            <Flex align="start" pt="6" pb={"6"} justify={"center"} gap={"150px"} className="border-t-[3px] border-transparent border-t-gradient">
                <Box>
                    <Text weight="bold" size="4" mb="2">
                        Flight Assistant Chatbot
                    </Text>
                    <Text as="p" color="gray" highContrast>
                        Polvora no, repolvora
                    </Text>
                </Box>

                <Box>
                    <Text weight="bold" size="4" mb="2">
                        Navigation
                    </Text>
                    <Flex direction="column" gap="1">
                        <Link href="/flights" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>Flights</Text>
                        </Link>
                        <Link href="/bookings" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>My Bookings</Text>
                        </Link>
                        <Link href="/login" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>Sign In</Text>
                        </Link>
                    </Flex>
                </Box>

                <Box>
                    <Text weight="bold" size="4" mb="2">
                        Follow us
                    </Text>
                    <Flex direction="column" gap="1">
                        <a href="#" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>Instagram</Text>
                        </a>
                        <a href="#" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>Facebook</Text>
                        </a>
                        <a href="#" className="unstyled-link hover:text-[var(--color-green)]">
                            <Text>WhatsApp</Text>
                        </a>
                    </Flex>
                </Box>
            </Flex>

            <Flex align={"center"} justify="center">
                <Text align="center" size="1" className="gradient-text">
                    © {new Date().getFullYear()} Polvora Inc. All rights reserved.
                </Text>
            </Flex>
        </Flex>
    );
}
