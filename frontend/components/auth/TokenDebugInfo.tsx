'use client';

import React, { useState, useEffect } from 'react';
import { Box, Text, Button, Flex } from '@radix-ui/themes';
import { getCookie } from '@/lib/utils/cookies';
import { getTimeUntilExpiration, isTokenExpired, isTokenExpiringSoon } from '@/lib/utils/jwt';
import { useUser } from '@/context/UserContext';

export function TokenDebugInfo() {
  const { user } = useUser();
  const [tokenInfo, setTokenInfo] = useState<any>(null);

  const updateTokenInfo = () => {
    const token = getCookie('access_token');
    if (!token) {
      setTokenInfo({ error: 'No token found' });
      return;
    }

    const timeLeft = getTimeUntilExpiration(token);
    const expired = isTokenExpired(token);
    const expiringSoon = isTokenExpiringSoon(token, 5);

    setTokenInfo({
      timeLeftSeconds: timeLeft,
      timeLeftMinutes: Math.floor(timeLeft / 60),
      expired,
      expiringSoon,
      token: token.substring(0, 20) + '...'
    });
  };

  useEffect(() => {
    updateTokenInfo();
    const interval = setInterval(updateTokenInfo, 1000);
    return () => clearInterval(interval);
  }, []);

  // Only show in development mode
  if (process.env.NODE_ENV === 'production' || !user) {
    return null;
  }

  return (
    <Box 
      style={{ 
        position: 'fixed', 
        bottom: 10, 
        left: 10, 
        padding: '12px', 
        backgroundColor: 'var(--gray-2)', 
        borderRadius: '8px',
        fontSize: '12px',
        zIndex: 1000,
        border: '1px solid var(--gray-6)',
        minWidth: '200px'
      }}
    >
      <Text size="1" weight="bold" style={{ display: 'block', marginBottom: '8px' }}>
        Token Debug Info
      </Text>
      
      {tokenInfo ? (
        <Flex direction="column" gap="1">
          {tokenInfo.error ? (
            <Text size="1" color="red">{tokenInfo.error}</Text>
          ) : (
            <>
              <Text size="1">
                Time left: {tokenInfo.timeLeftMinutes}m {tokenInfo.timeLeftSeconds % 60}s
              </Text>
              <Text size="1" color={tokenInfo.expired ? 'red' : tokenInfo.expiringSoon ? 'orange' : 'green'}>
                Status: {tokenInfo.expired ? 'EXPIRED' : tokenInfo.expiringSoon ? 'EXPIRING SOON' : 'VALID'}
              </Text>
              <Text size="1" style={{ wordBreak: 'break-all' }}>
                Token: {tokenInfo.token}
              </Text>
            </>
          )}
        </Flex>
      ) : (
        <Text size="1">Loading...</Text>
      )}
      
      <Button 
        size="1" 
        variant="ghost" 
        onClick={updateTokenInfo}
        style={{ marginTop: '8px', fontSize: '11px' }}
      >
        Refresh
      </Button>
    </Box>
  );
}
