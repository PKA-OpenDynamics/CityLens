// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Environment Detection and Configuration
 * Automatically detect local vs production environment
 */

export type Environment = 'local' | 'production' | 'staging';

export interface EnvironmentConfig {
  backendUrl: string;
  fusekiUrl: string;
  wsUrl: string;
  environment: Environment;
}

// Environment URLs configuration
const ENV_CONFIGS: Record<Environment, Omit<EnvironmentConfig, 'environment'>> = {
  local: {
    backendUrl: 'http://localhost:8000',
    fusekiUrl: 'http://localhost:7200',
    wsUrl: 'ws://localhost:8000',
  },
  staging: {
    backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://staging-api.citylens.vn',
    fusekiUrl: process.env.NEXT_PUBLIC_FUSEKI_URL || 'http://localhost:7200',
    wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'wss://staging-api.citylens.vn',
  },
  production: {
    backendUrl: process.env.NEXT_PUBLIC_BACKEND_URL || 'https://api.citylens.vn',
    fusekiUrl: process.env.NEXT_PUBLIC_FUSEKI_URL || 'https://fuseki.citylens.vn',
    wsUrl: process.env.NEXT_PUBLIC_WS_URL || 'wss://api.citylens.vn',
  },
};

/**
 * Detect current environment based on hostname and other signals
 */
export function detectEnvironment(): Environment {
  // Server-side rendering check
  if (typeof window === 'undefined') {
    return (process.env.NODE_ENV === 'production' ? 'production' : 'local') as Environment;
  }

  const hostname = window.location.hostname;

  // Explicit environment from URL param (for testing)
  const urlParams = new URLSearchParams(window.location.search);
  const envParam = urlParams.get('env');
  if (envParam && ['local', 'staging', 'production'].includes(envParam)) {
    return envParam as Environment;
  }

  // Check for production indicators
  if (
    hostname === 'citylens.vn' ||
    hostname.endsWith('.citylens.vn') ||
    hostname.endsWith('.netlify.app') ||
    hostname.endsWith('.vercel.app') ||
    // Cloudflare tunnel domains
    hostname.endsWith('.trycloudflare.com')
  ) {
    return 'production';
  }

  // Check for staging
  if (
    hostname.includes('staging') ||
    hostname.includes('preview') ||
    hostname.includes('dev.')
  ) {
    return 'staging';
  }

  // Local development
  if (
    hostname === 'localhost' ||
    hostname === '127.0.0.1' ||
    hostname.startsWith('192.168.') ||
    hostname.startsWith('10.')
  ) {
    return 'local';
  }

  // Default to production for unknown hosts
  return 'production';
}

/**
 * Get environment configuration
 */
export function getEnvironmentConfig(): EnvironmentConfig {
  const environment = detectEnvironment();
  
  // Allow runtime override via env variables
  const config = {
    ...ENV_CONFIGS[environment],
    environment,
  };

  // Check for Cloudflare tunnel URL in localStorage or env
  if (typeof window !== 'undefined') {
    const storedBackendUrl = localStorage.getItem('citylens_backend_url');
    if (storedBackendUrl) {
      config.backendUrl = storedBackendUrl;
    }
  }

  // Override with NEXT_PUBLIC env vars if available
  if (process.env.NEXT_PUBLIC_BACKEND_URL) {
    config.backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL;
  }
  if (process.env.NEXT_PUBLIC_FUSEKI_URL) {
    config.fusekiUrl = process.env.NEXT_PUBLIC_FUSEKI_URL;
  }

  return config;
}

/**
 * Get backend API URL
 */
export function getBackendUrl(): string {
  return getEnvironmentConfig().backendUrl;
}

/**
 * Get Fuseki/SPARQL endpoint URL
 */
export function getFusekiUrl(): string {
  return getEnvironmentConfig().fusekiUrl;
}

/**
 * Check if running locally
 */
export function isLocal(): boolean {
  return detectEnvironment() === 'local';
}

/**
 * Check if running in production
 */
export function isProduction(): boolean {
  return detectEnvironment() === 'production';
}

/**
 * Set custom backend URL (useful for development with tunnels)
 */
export function setBackendUrl(url: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem('citylens_backend_url', url);
  }
}

/**
 * Clear custom backend URL
 */
export function clearBackendUrl(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('citylens_backend_url');
  }
}

/**
 * Build full API URL
 */
export function buildApiUrl(path: string): string {
  const baseUrl = getBackendUrl();
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${baseUrl}${cleanPath}`;
}

/**
 * Build SPARQL endpoint URL
 */
export function buildSparqlUrl(dataset: string, queryType: 'query' | 'update' = 'query'): string {
  const baseUrl = getFusekiUrl();
  return `${baseUrl}/${dataset}/${queryType}`;
}

// Export singleton config for easy access
export const envConfig = getEnvironmentConfig();

export default {
  detectEnvironment,
  getEnvironmentConfig,
  getBackendUrl,
  getFusekiUrl,
  isLocal,
  isProduction,
  setBackendUrl,
  clearBackendUrl,
  buildApiUrl,
  buildSparqlUrl,
  envConfig,
};
