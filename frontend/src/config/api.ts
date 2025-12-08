/**
 * Intelligent API Configuration
 * Automatically detects environment and configures API URLs appropriately.
 * No more manual CORS/CSRF debugging!
 */

// =============================================================================
// 🎯 SINGLE SOURCE OF TRUTH - ENVIRONMENT DETECTION
// =============================================================================

/**
 * Environment types matching backend configuration
 */
type EnvType = 'local' | 'dev' | 'production' | 'render';

/**
 * Complete environment information - computed once, used everywhere
 */
interface EnvironmentInfo {
  envType: EnvType;
  isLocalhost: boolean;
  isHttps: boolean;
  streamServicePort: number;
}

/**
 * Environment configuration matching backend PORT_MAPPING
 * 
 * PORT MAPPING for Stream Microservice:
 * --------------------------------------
 * 9010 - Production & Local (default)
 *        - Production Hetzner (thermal-eye.sopira.com)
 *        - Local development (localhost)
 *        - Render deployment
 *        
 * 9011 - DEV Environment (Hetzner)
 *        - Used by dev.thermal-eye.sopira.com
 *        - Runs parallel to production without port conflict
 * 
 * Why different ports?
 * - DEV and PROD run on same Hetzner server (138.199.224.196)
 * - Each needs its own stream service instance
 * - Different ports prevent conflicts
 */
interface EnvPattern {
  pattern: string;
  envType: EnvType;
  isLocalhost: boolean;
  streamPort: number;
}

const ENVIRONMENT_PATTERNS: EnvPattern[] = [
  // Local development (developer's machine)
  { pattern: 'localhost', envType: 'local', isLocalhost: true, streamPort: 9010 },
  { pattern: '127.0.0.1', envType: 'local', isLocalhost: true, streamPort: 9010 },
  
  // DEV environment (Hetzner server - parallel to production)
  { pattern: 'dev.thermal-eye.sopira.com', envType: 'dev', isLocalhost: false, streamPort: 9011 },
  
  // Production environment (Hetzner server - main deployment)
  { pattern: 'thermal-eye.sopira.com', envType: 'production', isLocalhost: false, streamPort: 9010 },
  
  // Render.com deployment (cloud hosting)
  { pattern: 'onrender.com', envType: 'render', isLocalhost: false, streamPort: 9010 },
];

// Cached environment info
let cachedEnvInfo: EnvironmentInfo | null = null;

/**
 * 🎯 SINGLE SOURCE OF TRUTH for environment detection.
 * 
 * Detects environment ONCE at app startup based on hostname.
 * All other code should use getCachedEnvironment() or the exported constants.
 * 
 * Returns:
 *   EnvironmentInfo with env_type, is_https, is_localhost, stream_service_port
 */
export function detectAndCacheEnvironment(): EnvironmentInfo {
  if (cachedEnvInfo) return cachedEnvInfo;
  
  const hostname = window.location.hostname.toLowerCase();
  const protocol = window.location.protocol;
  const isHttps = protocol === 'https:';
  
  // Find matching environment pattern
  for (const config of ENVIRONMENT_PATTERNS) {
    if (hostname.includes(config.pattern)) {
      cachedEnvInfo = {
        envType: config.envType,
        isLocalhost: config.isLocalhost,
        isHttps: isHttps,  // 🔧 Use actual protocol (works with HTTP or HTTPS)
        streamServicePort: config.streamPort,
      };
      console.log('[Environment] Detected:', cachedEnvInfo);
      return cachedEnvInfo;
    }
  }
  
  // Fallback to local for unknown domains
  cachedEnvInfo = {
    envType: 'local',
    isLocalhost: true,
    isHttps: false,
    streamServicePort: 9010,
  };
  console.log('[Environment] Detected (fallback):', cachedEnvInfo);
  return cachedEnvInfo;
}

/**
 * Get cached environment info.
 * Must be called after detectAndCacheEnvironment().
 */
export function getCachedEnvironment(): EnvironmentInfo {
  if (!cachedEnvInfo) {
    return detectAndCacheEnvironment();
  }
  return cachedEnvInfo;
}

// Initialize on module load
detectAndCacheEnvironment();

/**
 * DEPRECATED: Use getCachedEnvironment() instead.
 * Kept for backward compatibility.
 */
export function detectEnvironment(): { envType: string; isHttps: boolean; isLocalhost: boolean } {
  const env = getCachedEnvironment();
  return {
    envType: env.envType,
    isHttps: env.isHttps,
    isLocalhost: env.isLocalhost,
  };
}

/**
 * Get API base URL intelligently based on environment
 * @param useProxy - If true, returns empty string for localhost to use Vite proxy (for regular fetch)
 *                  If false, returns explicit URL (for EventSource, direct links)
 */
export function getApiUrl(useProxy: boolean = true): string {
  const env = getCachedEnvironment();
  const hostname = window.location.hostname;
  const protocol = env.isHttps ? 'https:' : 'http:';
  
  if (env.isLocalhost) {
    // Local development
    // Use proxy for regular fetch (empty string), explicit URL for EventSource
    // IMPORTANT: Use 'localhost' not '127.0.0.1' for EventSource to match frontend origin
    // so cookies are sent correctly (same-origin policy)
    return useProxy ? '' : 'http://localhost:8000';
  } else if (env.envType === 'dev' || env.envType === 'production') {
    // DEV & Production: same origin (nginx proxy)
    // Both use nginx to proxy API requests
    return useProxy ? '' : `${protocol}//${hostname}`;
  } else if (env.envType === 'render') {
    // Render production
    return 'https://thermal-eye-backend.onrender.com';
  }
  
  // Fallback
  return 'http://localhost:8000';
}

/**
 * API base URL for API calls (uses Vite proxy on localhost)
 */
export const API_BASE = getApiUrl(true);

/**
 * Backend URL for direct backend links like Django admin (explicit URL even on localhost)
 */
export const BACKEND_URL = getApiUrl(false);

/**
 * Check if running in development mode
 */
export const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

/**
 * Check if running on Render production
 */
export const isRenderProduction = window.location.hostname.includes('onrender.com');

/**
 * Check if running on sopira.com production
 */
export const isSopiraProduction = window.location.hostname.includes('sopira.com');

/**
 * Check if running on custom server
 */
export const isCustomServer = window.location.hostname === '138.199.224.196';

/**
 * Base URL for the dedicated stream microservice.
 * Automatically uses correct port based on environment (9010 or 9011).
 * Can be overridden via VITE_STREAM_SERVICE_BASE_URL for custom deployments.
 */
export function getStreamServiceBaseUrl(): string {
  // Allow manual override via environment variable
  const configured = import.meta.env.VITE_STREAM_SERVICE_BASE_URL;
  if (configured && configured.trim().length > 0) {
    return configured.replace(/\/$/, '');
  }
  
  // Use centralized environment detection
  const env = getCachedEnvironment();
  const protocol = env.isHttps ? 'https:' : 'http:';
  const hostname = window.location.hostname;
  
  if (env.isLocalhost) {
    // Use dedicated microservice port directly to avoid proxy connection limits
    // Prefer 127.0.0.1 so browser treats it as a different origin than localhost:5173
    return `http://127.0.0.1:${env.streamServicePort}`;
  }
  
  // Use dynamic port from environment detection
  return `${protocol}//${hostname}:${env.streamServicePort}`;
}

export const STREAM_SERVICE_BASE_URL = getStreamServiceBaseUrl();

/**
 * Camera network configuration
 */
const CAMERA_LOCAL_HOST = '192.168.1.64';
const CAMERA_LOCAL_HTTP_PORT = 80;
const CAMERA_LOCAL_RTSP_PORT = 554;

const CAMERA_PUBLIC_HOST_FALLBACK = 'lp17.ddns.net';
const CAMERA_PUBLIC_HTTP_PORT_FALLBACK = 9080;
const CAMERA_PUBLIC_RTSP_PORT_FALLBACK = 8064;

export type CameraNetworkConfig = {
  host: string;
  httpPort: number;
  rtspPort: number;
  isLocal: boolean;
};

/**
 * Resolve camera host/ports for the current environment.
 * Allows overriding via VITE_CAMERA_PUBLIC_HOST / VITE_CAMERA_PUBLIC_PORT.
 */
export function getCameraNetworkConfig(): CameraNetworkConfig {
  const { envType, isLocalhost } = detectEnvironment();

  const publicHost =
    (import.meta.env.VITE_CAMERA_PUBLIC_HOST as string | undefined)?.trim() || CAMERA_PUBLIC_HOST_FALLBACK;
  const publicHttpPortRaw = (import.meta.env.VITE_CAMERA_PUBLIC_HTTP_PORT as string | undefined)?.trim();
  const publicRtspPortRaw = (import.meta.env.VITE_CAMERA_PUBLIC_RTSP_PORT as string | undefined)?.trim();
  const parsedHttp = Number.parseInt(publicHttpPortRaw || '', 10);
  const parsedRtsp = Number.parseInt(publicRtspPortRaw || '', 10);
  const resolvedHttpPort = Number.isFinite(parsedHttp) ? parsedHttp : CAMERA_PUBLIC_HTTP_PORT_FALLBACK;
  const resolvedRtspPort = Number.isFinite(parsedRtsp) ? parsedRtsp : CAMERA_PUBLIC_RTSP_PORT_FALLBACK;

  if (isLocalhost || envType === 'local') {
    return {
      host: CAMERA_LOCAL_HOST,
      httpPort: CAMERA_LOCAL_HTTP_PORT,
      rtspPort: CAMERA_LOCAL_RTSP_PORT,
      isLocal: true,
    };
  }

  return {
    host: publicHost,
      httpPort: resolvedHttpPort,
      rtspPort: resolvedRtspPort,
    isLocal: false,
  };
}

export const CAMERA_PUBLIC_HOST_DEFAULT = CAMERA_PUBLIC_HOST_FALLBACK;
