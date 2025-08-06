// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { isTokenExpired } from '@/lib/utils/jwt';
import {
  isProtectedRoute,
  isPublicRoute,
  isAuthRoute,
  isIgnoredRoute,
  DEFAULT_LOGIN_REDIRECT
} from '@/lib/config/routes';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip middleware for API routes, static files, and Next.js internals
  if (isIgnoredRoute(pathname)) {
    return NextResponse.next();
  }

  // Get the token from cookies
  const token = request.cookies.get('access_token')?.value;

  // Check if the current path is protected
  const isProtected = isProtectedRoute(pathname);
  
  // Check if the current path is public
  const isPublic = isPublicRoute(pathname);
  
  // Check if the current path is an auth route (login/register)
  const isAuth = isAuthRoute(pathname);

  // If it's a public route, allow access without authentication
  if (isPublic && !isAuth) {
    console.log(`✅ Public route allowed: ${pathname}`);
    return NextResponse.next();
  }

  // If it's a protected route
  if (isProtected) {
    // No token found
    if (!token) {
      console.log(`🔒 No token found, redirecting to login from: ${pathname}`);
      return redirectToLogin(request);
    }

    // Token exists but is expired
    if (isTokenExpired(token)) {
      console.log(`🔒 Expired token found, redirecting to login from: ${pathname}`);
      // Clear the expired token
      const response = redirectToLogin(request);
      response.cookies.delete('access_token');
      return response;
    }

    // Token is valid, allow access
    console.log(`✅ Valid token found, allowing access to: ${pathname}`);
    return NextResponse.next();
  }

  // If user is logged in and tries to access login/register pages
  if (isAuth && token && !isTokenExpired(token)) {
    console.log(`🔄 Authenticated user accessing auth page, redirecting to ${DEFAULT_LOGIN_REDIRECT}`);
    return NextResponse.redirect(new URL(DEFAULT_LOGIN_REDIRECT, request.url));
  }

  // For all other routes (public or unspecified), allow access
  return NextResponse.next();
}

function redirectToLogin(request: NextRequest): NextResponse {
  const loginUrl = new URL('/login', request.url);
  
  // Add the current path as a redirect parameter so we can return the user there after login
  if (request.nextUrl.pathname !== '/login') {
    loginUrl.searchParams.set('redirect', request.nextUrl.pathname);
  }
  
  return NextResponse.redirect(loginUrl);
}

// Configure which paths the middleware should run on
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder files
     */
    '/((?!api|_next/static|_next/image|favicon.ico|images|static|public).*)',
  ],
};
