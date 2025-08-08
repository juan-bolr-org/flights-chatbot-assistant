export interface TokenSuccess {
    access_token: string;
    token_type: string;
}

export interface TokenError {
    detail: {
        error_code?: string;
        message?: string;
    };
}

export type Token = TokenSuccess | TokenError;
export interface User {
    id: number
    email: string
    name: string
    phone?: string
    created_at?: string
    token?: Token
}

export interface UserResponse {
    ok: boolean
    data: User
}

export interface LoginCredentials {
    email: string
    password: string
}

export interface RegisterData extends LoginCredentials {
    name: string
}

export type AuthResponse = User;
