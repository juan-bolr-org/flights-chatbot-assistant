'use client';

import { Flex, Text, Button, Box, DropdownMenu, Avatar } from '@radix-ui/themes';
import { PersonIcon } from '@radix-ui/react-icons';
import Link from 'next/link';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { logout } from '@/lib/api/auth';

export default function Header() {
  const router = useRouter();
  const [user, setUser] = useState<{ name: string } | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem('token');
      if (storedUser) {
        try {
          const parsedUser = { name: 'polvora' };
          setUser(parsedUser);
        } catch (err) {
          console.error('Failed to parse user from localStorage:', err);
        }
      }
    }
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      router.push('/');
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  return (
    <Flex
      justify="between"
      align="center"
      pt="6"
      pb="6"
      px="6"
      className="border-b-[3px] border-transparent border-b-gradient"
    >
      <Box>
        <Text size="5" weight="bold" className="gradient-text" asChild>
          <Link href="/">Flights Chatbot Assistant</Link>
        </Text>
      </Box>

      <Flex justify="between" gap="4" align="center">
        <Box>
          <Button variant="ghost" asChild>
            <Link href="/flights">Flights</Link>
          </Button>
        </Box>

        <Box>
          <Button variant="ghost" asChild>
            <Link href="/bookings">My Bookings</Link>
          </Button>
        </Box>

        {user ? (
          <Box>
            <DropdownMenu.Root>
              <DropdownMenu.Trigger>
                <Button variant="soft">
                  <Avatar
                    fallback={user.name.charAt(0).toUpperCase()}
                    size="2"
                  />
                  <DropdownMenu.TriggerIcon />
                </Button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Content>
                <DropdownMenu.Item>
                  <Text>{user.name}</Text>
                </DropdownMenu.Item>
                <DropdownMenu.Item onClick={handleLogout}>
                  Log out
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          </Box>
        ) : (
          <Box>
            <DropdownMenu.Root>
              <DropdownMenu.Trigger>
                <Button variant="soft">
                  <PersonIcon />
                  <DropdownMenu.TriggerIcon />
                </Button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Content>
                <DropdownMenu.Item asChild>
                  <Link href="/login">
                    <Text>Sign In</Text>
                  </Link>
                </DropdownMenu.Item>
              </DropdownMenu.Content>
            </DropdownMenu.Root>
          </Box>
        )}
      </Flex>
    </Flex>
  );
}
