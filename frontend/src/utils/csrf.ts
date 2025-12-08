/**
 * CSRF Token utilities
 */

/**
 * Get cookie value by name
 * @param name - Cookie name
 * @returns Cookie value or null if not found
 */
function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[2]) : null;
}

/**
 * Get CSRF token from cookies
 * @returns CSRF token or empty string
 */
export function getCsrfToken(): string {
  return getCookie('csrftoken') || '';
}

