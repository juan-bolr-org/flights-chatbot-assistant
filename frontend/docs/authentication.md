# Frontend Authentication System

This document explains the authentication flow and automatic redirect system implemented in the frontend.

## Overview

The authentication system consists of:

1. **Middleware**: Server-side route protection and redirects
2. **UserContext**: Client-side authentication state management
3. **JWT Token Management**: Token validation, refresh, and expiration handling
4. **Protected Routes**: Component-level protection for specific pages

## Components

### 1. Middleware (`middleware.ts`)

The middleware runs on **every request** and handles:

- **Route Protection**: Automatically redirects to login for protected routes without valid tokens
- **Token Validation**: Checks if JWT tokens are expired
- **Auth Page Redirects**: Redirects authenticated users away from login/register pages
- **Redirect Preservation**: Saves the intended destination for post-login redirect

**Protected Routes:**
- `/flights`
- `/bookings` 
- `/profile`
- `/dashboard`
- `/chat`

**Public Routes:**
- `/` (home)
- `/login`
- `/register`
- `/about`
- `/contact`

### 2. UserContext (`context/UserContext.tsx`)

Manages authentication state throughout the application:

- **User State**: Stores current user information
- **Token Monitoring**: Checks token expiration every minute
- **Auto Refresh**: Automatically refreshes tokens that expire within 5 minutes
- **Loading States**: Handles loading states during authentication checks

### 3. JWT Utilities (`lib/utils/jwt.ts`)

Client-side JWT token utilities:

- `parseJWT()`: Safely parse JWT tokens without signature verification
- `isTokenExpired()`: Check if a token is expired
- `isTokenExpiringSoon()`: Check if a token expires within N minutes

### 4. Auth API (`lib/api/auth.ts`)

API functions for authentication:

- `login()`: User login
- `register()`: User registration
- `logout()`: User logout
- `getCurrentUser()`: Get current user info
- `refreshToken()`: Refresh JWT token (30-minute duration)

### 5. Protected Route Component (`components/auth/ProtectedRoute.tsx`)

Component-level protection for extra security:

```tsx
<ProtectedRoute>
  <SensitiveComponent />
</ProtectedRoute>
```

## Authentication Flow

### 1. Login Process

1. User visits `/login`
2. If already authenticated → redirect to `/flights` (or saved redirect path)
3. User submits credentials
4. On success → JWT cookie is set + redirect to intended page
5. UserContext updates with user data

### 2. Protected Route Access

1. User visits protected route (e.g., `/flights`)
2. Middleware checks for valid token
3. If no token or expired → redirect to `/login?redirect=/flights`
4. If valid → allow access

### 3. Token Refresh

1. UserContext monitors token expiration every minute
2. If token expires within 5 minutes → automatically refresh
3. If refresh fails → clear user state (triggers re-authentication)

### 4. Logout Process

1. User clicks logout
2. Server clears JWT cookie
3. UserContext clears user state
4. Redirect to login page

## Configuration

Routes are configured in `lib/config/routes.ts`:

```typescript
export const PROTECTED_ROUTES = ['/flights', '/bookings', ...];
export const PUBLIC_ROUTES = ['/', '/login', ...];
export const DEFAULT_LOGIN_REDIRECT = '/flights';
```

## Usage Examples

### Protecting a New Page

Add the route to `PROTECTED_ROUTES` in `lib/config/routes.ts`:

```typescript
export const PROTECTED_ROUTES = [
  '/flights',
  '/bookings',
  '/your-new-page', // Add here
];
```

### Using Protected Route Component

```tsx
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

export default function SensitivePage() {
  return (
    <ProtectedRoute>
      <div>This content is protected!</div>
    </ProtectedRoute>
  );
}
```

### Using Auth Hooks

```tsx
import { useUser } from '@/context/UserContext';
import { useAuthRedirect } from '@/lib/hooks/useAuthRedirect';

export default function LoginPage() {
  const { user, loading } = useUser();
  const { redirectAfterLogin } = useAuthRedirect();
  
  // Redirect if already authenticated
  useRedirectIfAuthenticated(user, loading);
  
  // ... rest of component
}
```

## Security Features

1. **HTTP-Only Cookies**: Tokens stored as HTTP-only cookies prevent XSS attacks
2. **Server-Side Validation**: Middleware validates tokens before page loads
3. **Automatic Refresh**: Tokens refresh automatically before expiration
4. **Token Expiration**: Short-lived tokens (30 minutes) reduce security risk
5. **Redirect Protection**: Original destination preserved through login flow

## Debugging

Enable console logs to see middleware behavior:

- `🔒 No token found` - User needs to login
- `🔒 Expired token found` - Token expired, redirecting to login
- `✅ Valid token found` - Authentication successful
- `🔄 Authenticated user accessing auth page` - Redirecting away from login/register

## Backend Integration

The frontend integrates with these backend endpoints:

- `POST /users/login` - User login (7-day token)
- `POST /users/register` - User registration (7-day token)  
- `POST /users/refresh` - Token refresh (30-minute token)
- `GET /users/me` - Get current user info
- `POST /users/logout` - Clear JWT cookie
