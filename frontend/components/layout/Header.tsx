'use client';

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { User } from 'lucide-react';
import { logout } from '@/lib/api/auth';

export default function Header() {
  const router = useRouter();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isUserDropdownOpen, setIsUserDropdownOpen] = useState(false);
  const [isLoginDropdownOpen, setIsLoginDropdownOpen] = useState(false);
  const [user, setUser] = useState<{ name: string } | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const storedUser = localStorage.getItem('token');
      if (storedUser) {
        try {
          const parsedUser = { name: "polvora" };
          setUser(parsedUser);
        } catch (err) {
          console.error("Failed to parse user from localStorage:", err);
        }
      }
    }
  }, []);

  const handleLogout = async () => {
    try {
      await logout();
      setUser(null);
      router.push('/');
    } catch (error) {
      console.error('Logout failed', error);
    }
  };

  return (
    <header className="bg-white gradient-border-bottom">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-bold gradient-text">
            Flights Chatbot Assistant
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link href="/flights" className="text-gray-900 hover:text-[var(--color-green)]">
              Flights
            </Link>
            <Link
              href="/bookings"
              className="text-gray-900 hover:text-[var(--color-green)]"
            >
              My Bookings
            </Link>
            {user ? (
              <div className="relative group">
                <button
                  className="flex items-center group px-3 py-2 rounded hover:bg-gray-100 transition"
                  onClick={() => setIsUserDropdownOpen((open) => !open)}
                  aria-label="Open user menu"
                >
                  <User size={24} className="transition-colors text-gray-700 group-hover:text-[var(--color-green)]" />
                  <span className="ml-2 text-gray-900 font-medium">{user.name}</span>
                  <svg className="ml-1 w-4 h-4 text-gray-500 group-hover:text-[var(--color-green)]" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isUserDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-44 bg-white border border-gray-200 rounded shadow-lg z-50">
                    <button
                      onClick={() => {
                        setIsUserDropdownOpen(false);
                        handleLogout();
                      }}
                      className="btn-antiprimary"
                    >
                      Log out
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <div className="relative group">
                <button
                  className="flex items-center group px-3 py-2 rounded hover:bg-gray-100 transition"
                  onClick={() => setIsLoginDropdownOpen((open) => !open)}
                  aria-label="Open login menu"
                >
                  <User size={24} className="transition-colors text-gray-700 group-hover:text-[var(--color-green)]" />
                  <svg className="ml-1 w-4 h-4 text-gray-500 group-hover:text-[var(--color-green)]" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {isLoginDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-44 bg-white border border-gray-200 rounded shadow-lg z-50">
                    <Link
                      href="/login"
                      className="btn-antiprimary"
                      onClick={() => setIsLoginDropdownOpen(false)}
                    >
                      Sign In
                    </Link>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
