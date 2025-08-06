import { AuthResponse, Token, RegisterData } from '../types/user';
import { getCookie } from '../utils/cookies';

const API_URL = '/api';

// Register a new user
export async function register(data: RegisterData): Promise<Token> {
    try {
        const res = await fetch(`${API_URL}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Include cookies in the request
            body: JSON.stringify(data),
        });

        const response = await res.json();

        if (!response) {
            throw new Error('Unexpected server response');
        }

        return response;
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(error.message);
        }
        throw new Error('Unknown error during registration');
    }
}

// Login with credentials
export async function login({
    email,
    password,
}: {
    email: string;
    password: string;
}): Promise<AuthResponse> {
    try {
        const res = await fetch(`${API_URL}/users/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include', // Include cookies in the request
            body: JSON.stringify({ email, password }),
        });

        const response = await res.json();

        if (!response) {
            throw new Error('Unexpected server response');
        }

        return response;

    } catch (error) {
        if (error instanceof Error) {
            throw new Error(error.message);
        }
        throw new Error('Unknown error during login');
    }
}

// Logout
export async function logout(): Promise<void> {
    try {
        const token = getCookie('access_token');
        
        // Call the server logout endpoint to clear the cookie
        await fetch(`${API_URL}/users/logout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(token ? { Authorization: `Bearer ${token}` } : {}),
            },
            credentials: 'include', // Include cookies in the request
        });
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Error while logging out: ${error.message}`);
        }
        throw new Error('Unknown error while logging out');
    }
}

// Get current user information
export async function getCurrentUser(): Promise<AuthResponse> {
    try {
        const token = getCookie('access_token');
        
        if (!token) {
            throw new Error('No access token found');
        }

        const res = await fetch(`${API_URL}/users/me`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            credentials: 'include', // Include cookies in the request
        });

        if (!res.ok) {
            throw new Error('Failed to get current user');
        }

        return await res.json();
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(error.message);
        }
        throw new Error('Unknown error while getting current user');
    }
}

// Refresh JWT token
export async function refreshToken(): Promise<Token> {
    try {
        const token = getCookie('access_token');
        
        if (!token) {
            throw new Error('No access token found');
        }

        const res = await fetch(`${API_URL}/users/refresh`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            credentials: 'include', // Include cookies in the request
        });

        if (!res.ok) {
            throw new Error('Failed to refresh token');
        }

        return await res.json();
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Error refreshing token: ${error.message}`);
        }
        throw new Error('Unknown error while refreshing token');
    }
}
