'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SocialLoginButtons from '@/components/auth/SocialLoginButtons';
import { register as apiRegister } from '@/lib/api/auth';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Button,
  TextField,
  Callout,
  Flex,
  Box,
  Heading,
  Text,
} from '@radix-ui/themes';
import { ExclamationTriangleIcon } from '@radix-ui/react-icons';

const registerSchema = z
  .object({
    name: z.string().min(2, { message: 'Name is required' }),
    email: z.string().email({ message: 'Invalid email' }),
    password: z.string().min(8, { message: 'Password must have at least 8 characters' }),
    confirmPassword: z.string().min(1, { message: 'Confirm your password' }),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

type RegisterFormValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
    clearErrors,
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormValues) => {
    clearErrors();
    try {
      const response = await apiRegister({
        name: data.name,
        email: data.email,
        password: data.password,
      });

      if (response.access_token) {
        localStorage.setItem('token', response.access_token);
        localStorage.setItem('registerSuccess', 'true');
        router.push('/register/success');
      } else {
        setError('root', { message: response.error || 'Could not register the account' });
      }
    } catch (err) {
      setError('root', { message: err instanceof Error ? err.message : 'Unknown registration error' });
    }
  };

  return (
    <Flex justify="center" align="center" px="4" py="100px">
      <Box className="bg-white shadow-md rounded-xl p-6 w-full max-w-sm">
        <Heading as="h1" size="5" mb="4" align="center">
          Create an Account
        </Heading>
        <Text align="center" size="2" mb="4">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-600 hover:underline">
            Sign in here
          </Link>
        </Text>

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <Flex direction="column" gap="4">
            {errors.root && (
              <Callout.Root color="red">
                <Callout.Icon>
                  <ExclamationTriangleIcon />
                </Callout.Icon>
                <Callout.Text>{errors.root.message}</Callout.Text>
              </Callout.Root>
            )}

            {/* Full name */}
            <TextField.Root
              placeholder="Full Name"
              {...register('name')}
              size="3"
              variant="surface"
            />
            {errors.name && (
              <Callout.Root color="red">
                <Callout.Text>{errors.name.message}</Callout.Text>
              </Callout.Root>
            )}

            {/* Email */}
            <TextField.Root
              placeholder="Email"
              {...register('email')}
              size="3"
              variant="surface"
            />
            {errors.email && (
              <Callout.Root color="red">
                <Callout.Text>{errors.email.message}</Callout.Text>
              </Callout.Root>
            )}

            {/* Password */}
            <TextField.Root
              type="password"
              placeholder="Password"
              {...register('password')}
              size="3"
              variant="surface"
            />
            {errors.password && (
              <Callout.Root color="red">
                <Callout.Text>{errors.password.message}</Callout.Text>
              </Callout.Root>
            )}

            {/* Confirm Password */}
            <TextField.Root
              type="password"
              placeholder="Confirm Password"
              {...register('confirmPassword')}
              size="3"
              variant="surface"
            />
            {errors.confirmPassword && (
              <Callout.Root color="red">
                <Callout.Text>{errors.confirmPassword.message}</Callout.Text>
              </Callout.Root>
            )}

            <Button type="submit" size="3" highContrast disabled={isSubmitting}>
              {isSubmitting ? 'Registering...' : 'Register'}
            </Button>
          </Flex>
        </form>
      </Box>
    </Flex>
  );
}
