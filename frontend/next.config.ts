import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactStrictMode: true,
  
  // Allow builds to complete even with warnings
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  
  typescript: {
    // Warning: This allows production builds to successfully complete even if
    // your project has TypeScript errors.
    ignoreBuildErrors: false, // Keep this false to catch actual TS errors
  },
  
  // Reduce build output verbosity
  logging: {
    fetches: {
      fullUrl: false,
    },
  },
  
  env: {
    API_URL: process.env.API_URL || "http://localhost:8000",
  },
  
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.API_URL || 'http://localhost:8000'}/:path*`,
      },
    ];
  },
};

export default nextConfig;