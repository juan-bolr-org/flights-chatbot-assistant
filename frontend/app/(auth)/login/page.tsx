'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { login } from '@/lib/api/auth';
import {
  Button,
  TextField,
  Callout,
  Flex,
  Container,
  Box,
  Heading,
  Text,
} from '@radix-ui/themes';
import { EnvelopeClosedIcon, LockClosedIcon } from '@radix-ui/react-icons';

const loginSchema = z.object({
  email: z.string().email({ message: 'Invalid email' }),
  password: z.string().min(1, { message: 'Password is required' }),
});

type LoginFormValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const router = useRouter();
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  if (token) {
    router.replace('/');
    return null;
  }

  const onSubmit = async (data: LoginFormValues) => {
    clearErrors();
    try {
      const result = await login({ email: data.email, password: data.password });
      
      if (result) {
        localStorage.setItem('token', result.token.access_token);
        router.push('/');
      } else {
        setError('root', { message: 'Invalid credentials. Please try again.' });
      }
    } catch {
      setError('root', { message: 'Something went wrong. Please try again.' });
    }
  };

  return (
    <Flex justify="center" align="center" px="4" py="100px">
      <Box className="bg-white shadow-md rounded-xl p-6 w-full max-w-sm">
        <Heading as="h1" size="5" mb="4" align="center">
          Login
        </Heading>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Flex direction="column" gap="4">
            {/* Email */}
            <Flex direction="column" gap="1">
              <TextField.Root
                variant="surface"
                placeholder="email"
                {...register('email')}
                size="3"
              >
                <TextField.Slot side="left">
                  <EnvelopeClosedIcon />
                </TextField.Slot>
              </TextField.Root>
              {errors.email && (
                <Callout.Root>
                  <Callout.Text>{errors.email.message}</Callout.Text>
                </Callout.Root>
              )}
            </Flex>

            {/* Password */}
            <Flex direction="column" gap="1">
              <TextField.Root
                variant="surface"
                type="password"
                placeholder="password"
                {...register('password')}
                size="3"
              >
                <TextField.Slot side="left">
                  <LockClosedIcon />
                </TextField.Slot>
              </TextField.Root>
              {errors.password && (
                <Callout.Root>
                  <Callout.Text>{errors.password.message}</Callout.Text>
                </Callout.Root>
              )}
            </Flex>

            {/* Error general */}
            {errors.root?.message && (
              <Callout.Root>
                <Callout.Text>{errors.root.message}</Callout.Text>
              </Callout.Root>
            )}

            <Button type="submit" size="3" className='btn-primary' highContrast disabled={isSubmitting}>
              Sign In
            </Button>

            <Text size="2" align="center">
              No account? {' '}
              <Link href="/register" className="text-blue-600 hover:underline">
                Register here
              </Link>
            </Text>
          </Flex>
        </form>
      </Box>
    </Flex>
  );
}
