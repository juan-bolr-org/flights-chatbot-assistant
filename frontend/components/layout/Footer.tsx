// components/Footer.tsx
import Link from "next/link";

export default function Footer() {
    return (
        <footer className="mt-10 gradient-border-top">
            <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-sm text-gray-900">
                <div>
                    <h3 className="font-bold text-lg mb-2">Flight Assistant Chatbot</h3>
                    <p className="opacity-90">
                        Polvora no, repolvora
                    </p>
                </div>

                <div>
                    <h4 className="font-bold text-lg mb-2">Navigation</h4>
                    <ul className="space-y-1">
                        <li><Link href="/flights" className="hover:text-[var(--color-green)]">Flights</Link></li>
                        <li><Link href="/bookings" className="hover:text-[var(--color-green)]">My Bookings</Link></li>
                        <li><Link href="/login" className="hover:text-[var(--color-green)]">Sign In</Link></li>
                    </ul>
                </div>

                <div>
                    <h4 className="font-bold text-lg mb-2">Follow us</h4>
                    <ul className="space-y-1">
                        <li><a href="#" className="hover:text-[var(--color-green)]">Instagram</a></li>
                        <li><a href="#" className="hover:text-[var(--color-green)]">Facebook</a></li>
                        <li><a href="#" className="hover:text-[var(--color-green)]">WhatsApp</a></li>
                    </ul>
                </div>
            </div>
            <div className="text-center py-4 text-xs gradient-text">
                © {new Date().getFullYear()} Polvora Inc. All rights reserved.
            </div>
        </footer>
    );
}