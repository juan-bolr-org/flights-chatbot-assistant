import { AuthResponse, Token, RegisterData, User } from '../types/user';

const API_URL = '/api';

// Register a new user
export async function register(data: RegisterData): Promise<Token> {
    try {
        const res = await fetch(`${API_URL}/users/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
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
        localStorage.removeItem('token');
    } catch (error) {
        if (error instanceof Error) {
            throw new Error(`Error while logging out: ${error.message}`);
        }
        throw new Error('Unknown error while logging out');
    }
}
