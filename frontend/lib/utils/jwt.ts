// lib/utils/jwt.ts
export interface JWTPayload {
  sub: string; // subject (user email)
  exp: number; // expiration time
  iat?: number; // issued at
}

/**
 * Parse JWT token without verifying signature (for expiration check only)
 * Note: This is for client-side validation only. Server-side verification is still required.
 */
export function parseJWT(token: string): JWTPayload | null {
  try {
    // JWT has 3 parts separated by dots
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }

    // Decode the payload (second part)
    const payload = parts[1];
    
    // Add padding if needed for base64 decoding
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    
    // Decode base64
    const decodedPayload = atob(paddedPayload.replace(/-/g, '+').replace(/_/g, '/'));
    
    // Parse JSON
    return JSON.parse(decodedPayload) as JWTPayload;
  } catch (error) {
    console.error('Error parsing JWT:', error);
    return null;
  }
}

/**
 * Check if JWT token is expired
 */
export function isTokenExpired(token: string): boolean {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return true;
  }

  // Check if token is expired (exp is in seconds, Date.now() is in milliseconds)
  const currentTime = Math.floor(Date.now() / 1000);
  return payload.exp < currentTime;
}

/**
 * Check if token expires within the next N minutes
 */
export function isTokenExpiringSoon(token: string, minutesThreshold: number = 5): boolean {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return true;
  }

  // Check if token expires within the threshold
  const currentTime = Math.floor(Date.now() / 1000);
  const thresholdTime = currentTime + (minutesThreshold * 60);
  return payload.exp < thresholdTime;
}

/**
 * Get token expiration time in seconds since epoch
 */
export function getTokenExpirationTime(token: string): number | null {
  const payload = parseJWT(token);
  return payload?.exp || null;
}

/**
 * Get time until expiration in seconds
 */
export function getTimeUntilExpiration(token: string): number {
  const payload = parseJWT(token);
  if (!payload || !payload.exp) {
    return 0;
  }

  const currentTime = Math.floor(Date.now() / 1000);
  return Math.max(0, payload.exp - currentTime);
}
