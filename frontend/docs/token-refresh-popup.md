# Token Refresh Popup Implementation

## Overview

This implementation provides an automatic token refresh popup that appears when a user's JWT token is about to expire (5 minutes before expiration). The popup allows users to extend their session without losing their work or being redirected to login.

## Components and Files Created/Modified

### 1. Core Components

#### `TokenRefreshPopup.tsx`
- The actual popup component that displays when token is expiring
- Provides "Extend Session" and "Ignore" buttons
- Handles the refresh API call and user context updates

#### `TokenManager.tsx`
- Orchestrates the token monitoring and popup display
- Automatically redirects to login if token expires
- Only shows popup for authenticated users

#### `TokenDebugInfo.tsx`
- Development-only component showing real-time token status
- Displays in bottom-right corner during development
- Shows time remaining, expiration status, and token preview

### 2. Hooks

#### `useTokenExpiration.ts`
- Monitors token expiration every 30 seconds
- Determines when to show/hide the popup
- Manages popup dismissal state
- Provides timer reset functionality

### 3. Utilities Updated

#### `jwt.ts` - Added functions:
- `getTokenExpirationTime()` - Get expiration timestamp
- `getTimeUntilExpiration()` - Get remaining seconds

### 4. Layout Integration

#### `layout.tsx`
- Added `<TokenManager />` component globally
- Added `<TokenDebugInfo />` for development

## How It Works

### 1. Token Monitoring
- `useTokenExpiration` hook checks token every 30 seconds
- Calculates time remaining until expiration
- Determines if popup should be shown (≤ 5 minutes remaining)

### 2. Popup Logic
- Shows popup when token has 5 minutes or less remaining
- Popup can be dismissed but won't show again until next expiration window
- After refresh, timer resets and popup disappears

### 3. Token Refresh Flow
1. User clicks "Extend Session"
2. Calls `/users/refresh` API endpoint  
3. Backend returns new 30-minute token
4. Frontend updates user context
5. Timer resets, popup closes

### 4. Expiration Handling
- If token actually expires, automatic redirect to login
- Expired tokens are cleared from cookies
- User context is reset

## Backend Integration

The implementation works with your existing backend endpoints:

- **Login/Register**: Returns 7-day tokens
- **Refresh**: Returns 30-minute tokens  
- **Token validation**: Middleware checks expiration

## Testing

### Manual Testing Routes

1. **`/token-test`** - Simple test page showing current status
2. **`/test-auth`** - Comprehensive auth testing page

### Debug Information

In development mode, check the bottom-right corner for:
- Real-time countdown
- Token status (VALID/EXPIRING SOON/EXPIRED)
- Token preview

### Testing Steps

1. **Login** to get a fresh token
2. **Monitor debug info** in bottom-right corner
3. **Wait for popup** (appears at 5 minutes remaining)
4. **Test refresh** by clicking "Extend Session"
5. **Test dismissal** by clicking "Ignore"

## Configuration

### Popup Timing
Change warning time in `TokenManager.tsx`:
```tsx
useTokenExpiration(5) // 5 minutes before expiration
```

### Check Interval
Modify in `useTokenExpiration.ts`:
```tsx
setInterval(checkTokenExpiration, 30000) // Every 30 seconds
```

### Protected Routes
Add routes in `lib/config/routes.ts`:
```tsx
export const PROTECTED_ROUTES = [
  '/flights',
  '/bookings',
  '/your-new-route', // Add here
] as const;
```

## User Experience

### Popup Appearance
- Non-intrusive modal dialog
- Clear messaging about time remaining
- Two clear action buttons
- Can be dismissed without action

### Smart Behavior
- Only shows for authenticated users
- Respects user dismissal choice
- Automatically resets after successful refresh
- Handles network errors gracefully

### Development Features
- Real-time debug information
- Test routes for validation
- Console logging for troubleshooting

## Security Considerations

1. **Client-side validation only** - Token parsing is for UX only
2. **Server verification required** - Backend still validates all tokens
3. **Short refresh tokens** - 30-minute duration reduces risk
4. **Automatic cleanup** - Expired tokens are removed
5. **Secure cookies** - HTTP-only cookies prevent XSS

## Troubleshooting

### Popup Not Showing
- Check if user is authenticated
- Verify token has < 5 minutes remaining
- Check console for errors
- Ensure TokenManager is in layout

### Refresh Failing
- Check network connectivity
- Verify backend `/users/refresh` endpoint
- Check token validity
- Review console errors

### Debug Info Not Visible
- Only shows in development mode
- Requires authenticated user
- Check bottom-right corner of screen

## Future Enhancements

1. **Configurable warning time** per user preferences
2. **Multiple warning levels** (10min, 5min, 1min)
3. **Activity detection** to prevent unnecessary refreshes
4. **Offline handling** for network issues
5. **Toast notifications** as alternative to modal
