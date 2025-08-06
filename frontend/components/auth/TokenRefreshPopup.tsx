'use client';

import React, { useState } from 'react';
import { Dialog, Flex, Button, Text, Box } from '@radix-ui/themes';
import { refreshToken } from '@/lib/api/auth';
import { useUser } from '@/context/UserContext';

interface TokenRefreshPopupProps {
  isOpen: boolean;
  onClose: () => void;
  onRefresh: () => Promise<void>;
  timeRemaining: number; // in minutes
}

export function TokenRefreshPopup({ 
  isOpen, 
  onClose, 
  onRefresh, 
  timeRemaining 
}: TokenRefreshPopupProps) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const { refreshUser } = useUser();

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await refreshToken();
      await refreshUser(); // Update user context
      await onRefresh(); // Reset the timer
      onClose();
    } catch (error) {
      console.error('Failed to refresh token:', error);
      // Optionally show an error message or redirect to login
    } finally {
      setIsRefreshing(false);
    }
  };

  const handleIgnore = () => {
    onClose();
  };

  return (
    <Dialog.Root open={isOpen}>
      <Dialog.Content style={{ maxWidth: 450 }}>
        <Dialog.Title>Session Expiring Soon</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          Your session will expire in {Math.ceil(timeRemaining)} minute{timeRemaining !== 1 ? 's' : ''}. 
          Would you like to extend your session?
        </Dialog.Description>

        <Box mb="4">
          <Text size="2" color="gray">
            Click "Extend Session" to continue working, or "Ignore" if you're finishing up.
          </Text>
        </Box>

        <Flex gap="3" mt="4" justify="end">
          <Button 
            variant="soft" 
            color="gray"
            onClick={handleIgnore}
            disabled={isRefreshing}
          >
            Ignore
          </Button>
          <Button 
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Extending...' : 'Extend Session'}
          </Button>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
}
