//..............................................................
//   ~/sopira.magic/version_01/frontend/src/security/csrf.ts
//   Security Module - CSRF Token Handling
//   Frontend security utilities for Django CSRF protection
//.............................................................

/**
 * Security Module - CSRF Token Handling.
 *
 * Centralized CSRF token management for frontend API calls.
 * Mirrors backend security module architecture.
 *
 * Django CSRF Flow:
 * 1. Django sends CSRF token in 'csrftoken' cookie
 * 2. Frontend reads token from cookie using getCsrfToken()
 * 3. Frontend sends token back in 'X-CSRFToken' header for mutations
 * 4. Django SecurityMiddleware validates token on POST/PATCH/DELETE/PUT
 *
 * Key Features:
 * - Automatic CSRF token extraction from cookies
 * - Header builders for mutating vs read-only requests
 * - Type-safe HeadersInit interface
 * - Ready for extension (JWT, API keys, etc.)
 *
 * Usage:
 * ```typescript
 * import { getMutatingHeaders } from '@/security'
 *
 * // For POST/PATCH/DELETE - includes CSRF token
 * fetch('/api/endpoint/', {
 *   method: 'POST',
 *   headers: getMutatingHeaders(),
 *   body: JSON.stringify(payload),
 * })
 *
 * // For GET - no CSRF token needed
 * fetch('/api/endpoint/', {
 *   method: 'GET',
 *   headers: getReadOnlyHeaders(),
 * })
 * ```
 *
 * SSOT Invariants:
 * - All mutating requests MUST use getMutatingHeaders() or getCsrfToken()
 * - CSRF token name 'csrftoken' matches Django default
 * - Header name 'X-CSRFToken' matches Django backend security config
 * - No hardcoded token extraction logic in individual API clients
 */

/**
 * Extract CSRF token from browser cookies.
 * 
 * Django sends the CSRF token in a cookie named 'csrftoken'.
 * This function reads that cookie and returns its value.
 * 
 * @returns CSRF token string or null if not found
 * 
 * @example
 * ```typescript
 * const token = getCsrfToken()
 * if (token) {
 *   headers['X-CSRFToken'] = token
 * }
 * ```
 */
export function getCsrfToken(): string | null {
  const match = document.cookie.match(/csrftoken=([^;]+)/)
  return match ? match[1] : null
}

/**
 * Get headers for mutating requests (POST, PATCH, DELETE, PUT).
 * 
 * Automatically includes CSRF token if available.
 * Use this for all state-changing API calls.
 * 
 * @param additionalHeaders - Optional additional headers to merge
 * @returns Headers object with CSRF token and Content-Type
 * 
 * @example
 * ```typescript
 * // Simple POST
 * fetch('/api/annotations/', {
 *   method: 'POST',
 *   headers: getMutatingHeaders(),
 *   credentials: 'include',
 *   body: JSON.stringify(payload),
 * })
 * 
 * // With custom headers
 * fetch('/api/upload/', {
 *   method: 'POST',
 *   headers: getMutatingHeaders({ 'X-Custom-Header': 'value' }),
 *   body: formData,
 * })
 * ```
 */
export function getMutatingHeaders(additionalHeaders?: HeadersInit): HeadersInit {
  const csrftoken = getCsrfToken()
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(additionalHeaders || {}),
  }
  
  if (csrftoken) {
    headers['X-CSRFToken'] = csrftoken
  }
  
  return headers
}

/**
 * Get headers for read-only requests (GET).
 * 
 * Does not include CSRF token as it's not required for read operations.
 * 
 * @param additionalHeaders - Optional additional headers to merge
 * @returns Headers object with Content-Type
 * 
 * @example
 * ```typescript
 * fetch('/api/annotations/', {
 *   method: 'GET',
 *   headers: getReadOnlyHeaders(),
 *   credentials: 'include',
 * })
 * ```
 */
export function getReadOnlyHeaders(additionalHeaders?: HeadersInit): HeadersInit {
  return {
    'Content-Type': 'application/json',
    ...(additionalHeaders || {}),
  }
}
