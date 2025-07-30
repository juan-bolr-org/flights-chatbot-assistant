'use client';

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RegisterSuccessPage() {
    const router = useRouter();

    useEffect(() => {
        // Solo permite acceso si la bandera está presente
        if (typeof window !== "undefined") {
            const ok = sessionStorage.getItem("registerSuccess");
            if (!ok) {
                router.replace("/register");
            } else {
                // Limpia la bandera para que no se pueda recargar la página de éxito
                sessionStorage.removeItem("registerSuccess");
            }
        }
    }, [router]);

    return (
        <main className="flex flex-col items-center justify-center min-h-[60vh] p-4">
            <div className="bg-white rounded-lg shadow-md p-8 max-w-md w-full text-center">
                <h1 className="text-2xl font-bold text-rose-700 mb-4">¡Registro exitoso!</h1>
                <p className="text-gray-700 mb-6">
                    Account Created, Yay!
                </p>
                <a
                    href="/login"
                    className="btn btn-primary w-full"
                >
                    Go Login bro.
                </a>
            </div>
        </main>
    );
}