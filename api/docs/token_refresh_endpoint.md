# Token Refresh Endpoint Documentation

## Overview

The `/users/refresh` endpoint allows authenticated users with valid JWT tokens to obtain a new token with a 30-minute duration. This endpoint is useful for maintaining user sessions without requiring them to log in again when their current token is still valid but will expire soon.

## Endpoint Details

- **URL**: `/users/refresh`
- **Method**: `POST`
- **Authentication**: Required (valid JWT token)
- **Content-Type**: `application/json`

## Request

### Headers
```
Authorization: Bearer <your_jwt_token>
Content-Type: application/json
```

### Body
No request body required.

## Response

### Success (200 OK)
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

The response also sets an HTTP-only cookie named `access_token` with the new token value and a max age of 30 minutes.

### Error Responses

#### 401 Unauthorized
```json
{
  "detail": "Invalid token"
}
```

#### 403 Forbidden
```json
{
  "detail": "Not authenticated"
}
```

#### 500 Internal Server Error
```json
{
  "detail": "Error refreshing token: [error details]"
}
```

## Usage Examples

### Using curl
```bash
curl -X POST http://localhost:8000/users/refresh \
  -H "Authorization: Bearer your_current_token" \
  -H "Content-Type: application/json"
```

### Using JavaScript (fetch)
```javascript
const response = await fetch('/users/refresh', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${currentToken}`,
    'Content-Type': 'application/json'
  }
});

if (response.ok) {
  const data = await response.json();
  const newToken = data.access_token;
  console.log('Token refreshed successfully');
} else {
  console.error('Failed to refresh token');
}
```

### Using Python (requests)
```python
import requests

headers = {
    'Authorization': f'Bearer {current_token}',
    'Content-Type': 'application/json'
}

response = requests.post('http://localhost:8000/users/refresh', headers=headers)

if response.status_code == 200:
    data = response.json()
    new_token = data['access_token']
    print('Token refreshed successfully')
else:
    print(f'Failed to refresh token: {response.status_code}')
```

## Key Features

1. **Valid Token Required**: Only users with currently valid JWT tokens can refresh them
2. **30-minute Duration**: New tokens have exactly 30 minutes of validity
3. **Cookie Setting**: The new token is automatically set as an HTTP-only cookie
4. **Security**: Uses the same cryptographic manager and validation as other authentication endpoints
5. **Logging**: All refresh attempts are logged for security monitoring

## Security Considerations

- The original token must still be valid (not expired)
- The token subject (user email) is extracted from the current token to ensure consistency
- The new token maintains the same user identity but with fresh expiration time
- HTTP-only cookies help prevent XSS attacks

## Integration Notes

This endpoint is designed to work seamlessly with the existing authentication flow:

1. User logs in and receives a token
2. Before the token expires, they can call `/users/refresh` to get a new 30-minute token
3. The frontend can implement automatic token refresh logic
4. When done, users can call `/users/logout` to clear the token

## Testing

A test script is available in the project root (`test_refresh_endpoint.py`) that demonstrates the complete workflow:

```bash
python test_refresh_endpoint.py
```

This script will:
1. Register/login a test user
2. Refresh the token
3. Verify the new token works
4. Test logout functionality
