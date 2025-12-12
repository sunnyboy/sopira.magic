//*........................................................
//*       www/thermal_eye_ui/src/hooks/useApi.tsx
//*       Custom hook pre API volania s auth headers
//*........................................................

import { useAuth } from '../contexts/AuthContext';
import { useCallback, useMemo } from 'react';
import { getMutatingHeaders } from '@/security/csrf';

export const useApi = () => {
  const { csrfToken } = useAuth();

  // API base URL
  const getApiUrl = useCallback(() => {
    const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    return isLocalhost ? 'http://localhost:8000' : '';
  }, []);

  // Vytvorí headers s autentifikáciou
  const getAuthHeaders = useCallback((additionalHeaders: Record<string, string> = {}) => ({
    ...getMutatingHeaders(additionalHeaders),
  }), [csrfToken]);

  const createHttpError = useCallback((status: number, message?: string) => {
    const error = new Error(message || `HTTP error! status: ${status}`) as Error & { status?: number };
    error.status = status;
    return error;
  }, []);

  // GET request s auth
  const get = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'GET',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw createHttpError(response.status);
    }

    return response.json();
  }, [createHttpError, getApiUrl, getAuthHeaders]);

  // POST request s auth
  const post = useCallback(async (endpoint: string, data: any = null, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'POST',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : null,
      ...options,
    });

    if (!response.ok) {
      throw createHttpError(response.status);
    }

    return response.json();
  }, [createHttpError, getApiUrl, getAuthHeaders]);

  // PUT request s auth
  const put = useCallback(async (endpoint: string, data: any = null, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'PUT',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : null,
      ...options,
    });

    if (!response.ok) {
      throw createHttpError(response.status);
    }

    return response.json();
  }, [createHttpError, getApiUrl, getAuthHeaders]);

  // PATCH request s auth
  const patch = useCallback(async (endpoint: string, data: any = null, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'PATCH',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      body: data ? JSON.stringify(data) : null,
      ...options,
    });

    if (!response.ok) {
      // Try to extract error details from response body
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (typeof errorData === 'object') {
          // Format validation errors nicely
          const errorParts: string[] = [];
          for (const [key, value] of Object.entries(errorData)) {
            if (Array.isArray(value)) {
              errorParts.push(`${key}: ${value.join(', ')}`);
            } else if (typeof value === 'object') {
              errorParts.push(`${key}: ${JSON.stringify(value)}`);
            } else {
              errorParts.push(`${key}: ${value}`);
            }
          }
          if (errorParts.length > 0) {
            errorMessage = errorParts.join('; ');
          } else {
            errorMessage = JSON.stringify(errorData);
          }
        } else {
          errorMessage = String(errorData);
        }
      } catch {
        // If response is not JSON, use status text
        errorMessage = response.statusText || errorMessage;
      }
      const error = createHttpError(response.status, errorMessage);
      (error as any).response = response;
      throw error;
    }

    return response.json();
  }, [createHttpError, getApiUrl, getAuthHeaders]);

  // DELETE request s auth
  const del = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    const response = await fetch(url, {
      method: 'DELETE',
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw createHttpError(response.status);
    }

    // DELETE môže vrátiť prázdnu odpoveď
    const text = await response.text();
    return text ? JSON.parse(text) : null;
  }, [createHttpError, getApiUrl, getAuthHeaders]);

  // Raw fetch s auth (pre špeciálne prípady)
  const fetchWithAuth = useCallback(async (endpoint: string, options: RequestInit = {}) => {
    const url = `${getApiUrl()}${endpoint}`;
    
    return fetch(url, {
      credentials: 'include',
      headers: {
        ...getAuthHeaders(),
        ...options.headers,
      },
      ...options,
    });
  }, [getApiUrl, getAuthHeaders]);

  return useMemo(() => ({
    get,
    post,
    put,
    patch,
    delete: del,
    fetchWithAuth,
    getApiUrl,
    getAuthHeaders,
  }), [del, fetchWithAuth, get, getApiUrl, getAuthHeaders, patch, post, put]);
};