'use client';

import { Flex, Button, Heading, Text } from '@radix-ui/themes';
import Link from 'next/link';

export default function NotFound() {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      style={{ minHeight: '60vh' }}
      px="4"
      gap="4"
    >
      <Heading size="9" as="h1" color="gray" highContrast>
        404
      </Heading>

      <Text size="5" color="gray" className="mb-6">
        Page not found
      </Text>

      <Button asChild size="3" color="blue" variant="solid">
        <Link href="/">Back to Home</Link>
      </Button>
    </Flex>
  );
}
