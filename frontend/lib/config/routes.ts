// lib/config/routes.ts

// Define routes that require authentication
export const PROTECTED_ROUTES = [
  '/flights',
  '/bookings',
  '/chat',
  '/test-auth',
  '/token-test',
] as const;

// Define public routes (that don't require authentication)
export const PUBLIC_ROUTES = [
  '/',
  '/login',
  '/register'
] as const;

// API routes and static files that should be ignored by middleware
export const IGNORED_ROUTES = [
  '/api',
  '/_next',
  '/favicon.ico',
  '/images',
  '/static',
  '/public',
] as const;

// Auth-related routes (login, register)
export const AUTH_ROUTES = [
  '/login',
  '/register',
] as const;

// Default redirect paths
export const DEFAULT_LOGIN_REDIRECT = '/flights';
export const DEFAULT_LOGOUT_REDIRECT = '/login';

// Route helper functions
export const isProtectedRoute = (pathname: string): boolean => {
  return PROTECTED_ROUTES.some(route => pathname.startsWith(route));
};

export const isPublicRoute = (pathname: string): boolean => {
  return PUBLIC_ROUTES.some(route => {
    if (route === '/') {
      return pathname === '/';
    }
    return pathname === route || pathname.startsWith(route + '/');
  });
};

export const isAuthRoute = (pathname: string): boolean => {
  return AUTH_ROUTES.some(route => pathname.startsWith(route));
};

export const isIgnoredRoute = (pathname: string): boolean => {
  return IGNORED_ROUTES.some(route => pathname.startsWith(route));
};
