'use client';

import { Box, Text, Flex, Link as RadixLink } from '@radix-ui/themes';
import Link from 'next/link';

export default function Footer() {
  return (
    <Flex
      direction="column"
      justify="between"
      gap="6"
      py="6"
    >
      <Flex
        align="start"
        pt="6"
        pb="6"
        justify="center"
        gap="150px"
        className="border-t-[3px] border-transparent border-t-gradient"
      >
        <Box>
          <Text weight="bold" size="4" mb="2">
            Flight Assistant Chatbot
          </Text>
          <Text as="p" color="gray" highContrast>
            DreamTeam Airlines, where your adventure begins.
          </Text>
        </Box>

        <Box>
          <Text weight="bold" size="4" mb="2">
            Navigation
          </Text>
          <Flex direction="column" gap="1">
            <RadixLink asChild>
              <Link href="/flights">Flights</Link>
            </RadixLink>
            <RadixLink asChild>
              <Link href="/bookings">My Bookings</Link>
            </RadixLink>
            <RadixLink asChild>
              <Link href="/login">Sign In</Link>
            </RadixLink>
          </Flex>
        </Box>

        <Box>
          <Text weight="bold" size="4" mb="2">
            Follow us
          </Text>
          <Flex direction="column" gap="1">
            <RadixLink asChild>
              <a href="#">Instagram</a>
            </RadixLink>
            <RadixLink asChild>
              <a href="#">Facebook</a>
            </RadixLink>
            <RadixLink asChild>
              <a href="#">WhatsApp</a>
            </RadixLink>
          </Flex>
        </Box>
      </Flex>

      <Flex align="center" justify="center">
        <Text align="center" size="1" className="gradient-text">
          © {new Date().getFullYear()} DreamTeam Inc. All rights reserved.
        </Text>
      </Flex>
    </Flex>
  );
}
