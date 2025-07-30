import { Metadata } from 'next'

export const metadata: Metadata = {
    title: 'Autenticación | Flagertour',
    description: 'Inicia sesión o regístrate en Flagertour',
}

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8">
                {children}
            </div>
        </div>
    )
} 