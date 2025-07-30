'use client';

import { useRouter } from 'next/navigation';
import Link from 'next/link';
import SocialLoginButtons from '@/components/auth/SocialLoginButtons';
import { register as apiRegister } from '@/lib/api/auth';
import { TriangleAlert } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';

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

      if (response.ok) {
        sessionStorage.setItem('registerSuccess', '1');
        router.push('/register/success');
      } else {
        setError('root', { message: response.error || 'Could not register the account' });
      }
    } catch (err) {
      setError('root', { message: err instanceof Error ? err.message : 'Unknown registration error' });
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-gray-50 px-4 sm:px-6 lg:px-8">
      <div className="card gradient-border max-w-md w-full space-y-6">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold gradient-text">
            Create an Account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="text-[var(--color-pink)] hover:text-[var(--color-pink-dark)]">
              Sign in here
            </Link>
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit(onSubmit)} noValidate>
          {errors.root && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-md text-sm">
              <TriangleAlert className="inline-block mr-2" /> {errors.root.message}
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="full_name" className="block text-sm font-medium text-gray-700">
                Full Name
              </label>
              <input
                id="full_name"
                type="text"
                className="input mt-1"
                {...register('name')}
                aria-invalid={!!errors.name}
              />
              {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                type="email"
                className="input mt-1"
                {...register('email')}
                aria-invalid={!!errors.email}
              />
              {errors.email && <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>}
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                type="password"
                className="input mt-1"
                {...register('password')}
                aria-invalid={!!errors.password}
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className="input mt-1"
                {...register('confirmPassword')}
                aria-invalid={!!errors.confirmPassword}
              />
              {errors.confirmPassword && (
                <p className="mt-1 text-xs text-red-600">{errors.confirmPassword.message}</p>
              )}
            </div>
          </div>

          <div>
            <button type="submit" disabled={isSubmitting} className="btn btn-primary w-full">
              {isSubmitting ? 'Registering...' : 'Register'}
            </button>
          </div>
        </form>

        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or register with</span>
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
