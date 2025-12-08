/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  
  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },

  // Image optimization
  images: {
    unoptimized: true, // Required for Netlify static export
  },

  // Webpack configuration
  webpack: (config) => {
    config.externals = [...(config.externals || []), 'canvas', 'jsdom'];
    return config;
  },
};

export default nextConfig;
