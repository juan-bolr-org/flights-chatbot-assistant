'use client';

import React from 'react';
import { Button, Flex, Box, Heading, Text, Callout } from '@radix-ui/themes';
import { useTokenExpiration } from '@/lib/hooks/useTokenExpiration';

export default function TokenTestPage() {
  const { showPopup, timeRemaining, isExpired, dismissPopup } = useTokenExpiration(5);

  return (
    <Flex direction="column" gap="4" p="4" maxWidth="600px" mx="auto">
      <Heading size="6">Token Refresh Popup Test</Heading>
      
      <Text size="3" color="gray">
        This page demonstrates the token refresh popup functionality.
      </Text>

      <Box p="4" style={{ backgroundColor: 'var(--gray-2)', borderRadius: '8px' }}>
        <Heading size="4" mb="3">Current Token Status</Heading>
        <Flex direction="column" gap="2">
          <Text><strong>Time Remaining:</strong> {Math.ceil(timeRemaining)} minutes</Text>
          <Text><strong>Is Expired:</strong> {isExpired ? 'Yes' : 'No'}</Text>
          <Text><strong>Popup Showing:</strong> {showPopup ? 'Yes' : 'No'}</Text>
        </Flex>
      </Box>

      <Callout.Root>
        <Callout.Icon>💡</Callout.Icon>
        <Callout.Text>
          <strong>How it works:</strong><br />
          • The popup will automatically appear when your token has 5 minutes or less remaining<br />
          • Your backend refresh endpoint creates 30-minute tokens<br />
          • So after login/refresh, you'll see the popup after 25 minutes<br />
          • The debug info in the bottom-right corner shows real-time status
        </Callout.Text>
      </Callout.Root>

      <Box p="4" style={{ backgroundColor: 'var(--blue-2)', borderRadius: '8px' }}>
        <Heading size="4" mb="2">Testing Instructions</Heading>
        <Text size="2">
          1. Login to get a fresh token<br />
          2. Watch the debug info in the bottom-right corner<br />
          3. The popup will appear when the countdown reaches 5 minutes<br />
          4. Click "Extend Session" to refresh the token<br />
          5. Or click "Ignore" to dismiss the popup
        </Text>
      </Box>

      {showPopup && (
        <Callout.Root color="orange">
          <Callout.Icon>⚠️</Callout.Icon>
          <Callout.Text>
            The token refresh popup should be visible on your screen right now!
          </Callout.Text>
        </Callout.Root>
      )}

      <Button onClick={dismissPopup} variant="outline">
        Manually Dismiss Popup (for testing)
      </Button>
    </Flex>
  );
}
