//..............................................................
//   ~/sopira.magic/version_01/frontend/src/security/index.ts
//   Security Module - Barrel Export
//   Frontend security utilities entry point
//..............................................................

/**
 * Security Module - Barrel Export.
 *
 * Centralized frontend security utilities module.
 * Mirrors backend sopira_magic.apps.security architecture.
 *
 * Module Structure:
 * - csrf.ts: CSRF token handling for Django API calls
 * - index.ts: Barrel export (this file)
 *
 * Future Extensions:
 * - auth.ts: JWT token management
 * - apikeys.ts: API key handling
 * - storage.ts: Secure token storage (localStorage/sessionStorage)
 * - encryption.ts: Client-side encryption utilities
 *
 * Architecture Principles:
 * - SSOT for all security-related frontend logic
 * - Config-driven approach (mirrors BE security config)
 * - No hardcoded security logic in domain modules
 * - Type-safe interfaces
 * - Environment-aware (dev vs production)
 *
 * Integration with Backend:
 * - CSRF token name: 'csrftoken' (Django default)
 * - CSRF header name: 'X-CSRFToken' (matches BE security/config.py)
 * - CORS credentials: 'include' (matches BE CORS allow_credentials)
 * - Cookie-based session management
 *
 * Usage Across Apps:
 * All app-specific API clients (e.g., apps/pdfviewer/api.ts) MUST
 * import and use these utilities instead of implementing their own
 * security logic.
 *
 * Example:
 * ```typescript
 * import { getMutatingHeaders } from '@/security'
 *
 * export async function createEntity(payload: Payload): Promise<Entity> {
 *   const response = await fetch('/api/entities/', {
 *     method: 'POST',
 *     headers: getMutatingHeaders(),
 *     credentials: 'include',
 *     body: JSON.stringify(payload),
 *   })
 *   // ...
 * }
 * ```
 */

// CSRF utilities

export { getCsrfToken, getMutatingHeaders, getReadOnlyHeaders } from './csrf'
