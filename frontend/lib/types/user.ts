export interface User {
    id: number
    email: string
    name: string
    phone: string
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

export interface AuthResponse {
    access_token: string
    user: User
}
