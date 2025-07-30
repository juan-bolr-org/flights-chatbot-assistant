'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { login } from '@/lib/api/auth';
import SocialLoginButtons from '@/components/auth/SocialLoginButtons';

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

      if (result?.access_token) {
        localStorage.setItem('token', result.access_token);
        router.push('/');
      } else {
        setError('root', { message: 'Invalid credentials. Please try again.' });
      }
    } catch {
      setError('root', { message: 'Something went wrong. Please try again.' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-gray-50 pt-20 px-4 sm:px-6 lg:px-8">
      <div className="card gradient-border max-w-md w-full space-y-6">
        <div>
          <h2 className="text-center text-2xl font-extrabold gradient-text">
            Sign In
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Need an account?{' '}
            <Link href="/register" className="text-[var(--color-pink)] hover:text-[var(--color-pink-dark)]">
              Register here
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)} noValidate>
          {errors.root && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
              {errors.root.message}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                autoComplete="email"
                className="input mt-1"
                {...register('email')}
                aria-invalid={!!errors.email}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                autoComplete="current-password"
                className="input mt-1"
                {...register('password')}
                aria-invalid={!!errors.password}
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isSubmitting}
              className="btn btn-primary w-full"
            >
              {isSubmitting ? 'Signing in...' : 'Sign In'}
            </button>
          </div>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or sign in with</span>
            </div>
          </div>

          <div className="mt-6">
            <SocialLoginButtons />
          </div>
        </div>
      </div>
    </div>
  );
}
