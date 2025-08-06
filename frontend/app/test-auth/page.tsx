// app/test-auth/page.tsx
'use client';

import { useUser } from '@/context/UserContext';
import { Button, Flex, Box, Heading, Text, Code } from '@radix-ui/themes';
import { getCookie, setCookie } from '@/lib/utils/cookies';
import { isTokenExpired, isTokenExpiringSoon, parseJWT, getTimeUntilExpiration } from '@/lib/utils/jwt';
import { refreshToken } from '@/lib/api/auth';
import { useState } from 'react';

export default function TestAuthPage() {
  const { user, loading } = useUser();
  const [tokenInfo, setTokenInfo] = useState<any>(null);
  const [refreshResult, setRefreshResult] = useState<string>('');

  const analyzeToken = () => {
    const token = getCookie('access_token');
    if (!token) {
      setTokenInfo({ error: 'No token found' });
      return;
    }

    const parsed = parseJWT(token);
    const expired = isTokenExpired(token);
    const expiringSoon = isTokenExpiringSoon(token, 5);

    setTokenInfo({
      token: token.substring(0, 50) + '...',
      parsed,
      expired,
      expiringSoon,
      expirationTime: parsed?.exp ? new Date(parsed.exp * 1000).toLocaleString() : 'Unknown'
    });
  };

  const testRefresh = async () => {
    try {
      setRefreshResult('Refreshing...');
      const result = await refreshToken();
      setRefreshResult(`Success! New token: ${result.access_token.substring(0, 30)}...`);
      // Re-analyze token after refresh
      setTimeout(analyzeToken, 100);
    } catch (error) {
      setRefreshResult(`Error: ${error}`);
    }
  };

  const testContextRefresh = async () => {
    try {
      setRefreshResult('Testing context refresh...');
      const result = await refreshToken();
      setRefreshResult(`Context refresh result: Success - ${result.access_token.substring(0, 30)}...`);
      setTimeout(analyzeToken, 100);
    } catch (error) {
      setRefreshResult(`Context refresh error: ${error}`);
    }
  };

  if (loading) {
    return (
      <Flex justify="center" align="center" p="4">
        <Text>Loading authentication state...</Text>
      </Flex>
    );
  }

  return (
    <Flex direction="column" gap="4" p="4" maxWidth="800px" mx="auto">
      <Heading size="6">Authentication Test Page</Heading>
      
      <Text size="3" color="gray">
        This page is automatically protected by middleware. You can only see this if you have a valid token.
      </Text>

      <Box p="4" style={{ backgroundColor: 'var(--gray-2)', borderRadius: '8px' }}>
        <Heading size="4" mb="3">User Information</Heading>
        {user ? (
          <Flex direction="column" gap="2">
            <Text><strong>Name:</strong> {user.name}</Text>
            <Text><strong>Email:</strong> {user.email}</Text>
            <Text><strong>ID:</strong> {user.id}</Text>
          </Flex>
        ) : (
          <Text color="red">No user data available</Text>
        )}
      </Box>

      <Flex direction="column" gap="3">
        <Heading size="4">Token Analysis</Heading>
        <Button onClick={analyzeToken} variant="outline">
          Analyze Current Token
        </Button>
        
        {tokenInfo && (
          <Box p="3" style={{ backgroundColor: 'var(--gray-2)', borderRadius: '8px' }}>
            <Code size="2">
              <pre>{JSON.stringify(tokenInfo, null, 2)}</pre>
            </Code>
          </Box>
        )}
      </Flex>

      <Flex direction="column" gap="3">
        <Heading size="4">Token Refresh Testing</Heading>
        <Flex gap="2">
          <Button onClick={testRefresh} variant="solid">
            Test Direct Refresh
          </Button>
          <Button onClick={testContextRefresh} variant="solid">
            Test Context Refresh
          </Button>
        </Flex>
        
        {refreshResult && (
          <Box p="3" style={{ backgroundColor: 'var(--gray-2)', borderRadius: '8px' }}>
            <Text size="2">{refreshResult}</Text>
          </Box>
        )}
      </Flex>

      <Box p="4" style={{ backgroundColor: 'var(--yellow-2)', borderRadius: '8px' }}>
        <Heading size="4" mb="2">How to Test Token Refresh Popup</Heading>
        <Flex direction="column" gap="2">
          <Text size="2">1. <strong>Analyze Token</strong> - See current token status and expiration</Text>
          <Text size="2">2. <strong>Test Refresh</strong> - Try refreshing the token manually</Text>
          <Text size="2">3. <strong>Look at bottom-right corner</strong> - Debug info shows real-time token status</Text>
          <Text size="2">4. <strong>Wait for popup</strong> - A popup will appear when token has 5 minutes or less remaining</Text>
          <Text size="2">5. <strong>Note:</strong> Your backend refresh endpoint gives 30-minute tokens, so popup will show after 25 minutes</Text>
          <Text size="2">6. <strong>Debug mode:</strong> Check the bottom-right corner for real-time token status</Text>
        </Flex>
      </Box>
    </Flex>
  );
}
