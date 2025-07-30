import { User } from "lucide-react";

export interface Token {
    access_token: string;
    token_type: string;
}

export interface User {
    id: number
    email: string
    name: string
    phone: string
    token: Token
    created_at: string
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
