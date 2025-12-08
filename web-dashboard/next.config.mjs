/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',  // Static export for Netlify
  
  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Base path (if needed)
  // basePath: '',
  
  // Trailing slash for static hosting
  trailingSlash: true,

  // Environment variables
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL,
  },

  // Webpack configuration
  webpack: (config) => {
    config.externals = [...(config.externals || []), 'canvas', 'jsdom'];
    return config;
  },
};

export default nextConfig;
