//*........................................................
//*       frontend/src/contexts/AuthContext.tsx
//*       Authentication context pre správu stavu prihlásenia
//*       Config-driven authentication using backend SSOT
//*........................................................

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { API_BASE } from '@/config/api';

interface User {
  id: number;
  username: string;
  email: string;
  is_staff: boolean;  // Backward compatibility (deprecated, use is_admin instead)
  is_superuser: boolean;  // Backward compatibility (deprecated, use is_superuser_role instead)
  role: string;
  role_display?: string;
  role_priority?: number;
  
  // SSOT Permission fields (from backend UserSerializer)
  can_read?: boolean;
  can_edit?: boolean;
  can_export?: boolean;
  can_manage_factories?: boolean;
  can_manage_users?: boolean;
  can_generate_seeds?: boolean;
  is_admin?: boolean;  // ADMIN or SUPERUSER role
  is_superuser_role?: boolean;  // SUPERUSER role only
  
  // Backward compatibility (deprecated, DON'T USE - use is_admin instead)
  can_admin?: boolean;
  
  first_name: string;
  last_name: string;
  date_joined?: string;
  last_login?: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  csrfToken: string;
  login: (username: string, password: string) => Promise<boolean>;
  signup: (username: string, password: string, email?: string, first_name?: string, last_name?: string) => Promise<{ success: boolean; error?: string }>;
  forgotPassword: (email: string) => Promise<{ success: boolean; error?: string; message?: string }>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [csrfToken, setCsrfToken] = useState('');
  
  // Ref to track if checkAuth is currently in progress (prevents duplicate calls)
  const checkingAuthRef = React.useRef(false);
  // Ref to track if initial check has been completed
  const initialCheckDoneRef = React.useRef(false);

  const isAuthenticated = user !== null;

  // Kontrola autentifikácie pri načítaní
  // PROTECTED: Only one checkAuth call at a time to prevent duplicate requests
  const checkAuth = React.useCallback(async (): Promise<void> => {
    // Prevent duplicate calls - if already checking, return immediately
    if (checkingAuthRef.current) {
      return;
    }
    
    checkingAuthRef.current = true;
    
    try {
      const response = await fetch(`${API_BASE}/api/auth/check/`, {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authenticated) {
          setUser(data.user);
        } else {
          setUser(null);
        }
        setCsrfToken(data.csrf_token || '');
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Error checking authentication:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
      checkingAuthRef.current = false;
      initialCheckDoneRef.current = true;
    }
  }, []); // Empty deps - API_BASE is stable

  // Prihlásenie
  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      // Získaj CSRF token, ak nie je nastavený
      let token = csrfToken;
      if (!token) {
        try {
          const csrfResponse = await fetch(`${API_BASE}/api/auth/csrf/`, {
            method: 'GET',
            credentials: 'include',
          });
          if (csrfResponse.ok) {
            const csrfData = await csrfResponse.json();
            token = csrfData.csrf_token || '';
            setCsrfToken(token);
          }
        } catch (csrfError) {
          console.error('Error getting CSRF token:', csrfError);
        }
      }

      const response = await fetch(`${API_BASE}/api/auth/login/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        body: JSON.stringify({ username, password }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUser(data.user);
          setCsrfToken(data.csrf_token || token);
          return true;
        }
      }
      
      // Ak bol problém s CSRF, skús znovu bez tokenu (niektoré konfigurácie to umožňujú)
      if (response.status === 403 && !token) {
        const retryResponse = await fetch(`${API_BASE}/api/auth/login/`, {
          method: 'POST',
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ username, password }),
        });
        
        if (retryResponse.ok) {
          const retryData = await retryResponse.json();
          if (retryData.success) {
            setUser(retryData.user);
            setCsrfToken(retryData.csrf_token || '');
            return true;
          }
        }
      }
      
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    }
  };

  // Registrácia
  const signup = async (username: string, password: string, email?: string, first_name?: string, last_name?: string): Promise<{ success: boolean; error?: string }> => {
    try {
      let token = csrfToken;
      if (!token) {
        try {
          const csrfResponse = await fetch(`${API_BASE}/api/auth/csrf/`, {
            method: 'GET',
            credentials: 'include',
          });
          if (csrfResponse.ok) {
            const csrfData = await csrfResponse.json();
            token = csrfData.csrf_token || '';
            setCsrfToken(token);
          }
        } catch (csrfError) {
          console.error('Error getting CSRF token:', csrfError);
        }
      }

      const response = await fetch(`${API_BASE}/api/auth/signup/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': token,
        },
        body: JSON.stringify({ 
          username, 
          password, 
          email: email || '',
          first_name: first_name || '',
          last_name: last_name || ''
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setUser(data.user);
          setCsrfToken(data.csrf_token || token);
          return { success: true };
        }
      }
      
      const errorData = await response.json().catch(() => ({ error: 'Registration failed' }));
      return { success: false, error: errorData.error || 'Registration failed' };
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Network error during registration' };
    }
  };

  // Forgot Password
  const forgotPassword = async (email: string): Promise<{ success: boolean; error?: string; message?: string }> => {
    try {
      const response = await fetch(`${API_BASE}/api/auth/forgot-password/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, message: data.message || 'Password reset email sent' };
      }
      
      const errorData = await response.json().catch(() => ({ error: 'Failed to send reset email' }));
      return { success: false, error: errorData.error || 'Failed to send reset email' };
    } catch (error) {
      console.error('Error sending reset email:', error);
      return { success: false, error: 'Network error' };
    }
  };

  // Odhlásenie
  const logout = async (): Promise<void> => {
    try {
      await fetch(`${API_BASE}/api/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfToken,
        },
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setCsrfToken('');
    }
  };

  // Kontrola pri načítaní aplikácie
  // Only run once on mount - React Strict Mode may cause double render, but we have protection
  // NOTE: checkAuth is stable (memoized with useCallback), so we can safely use empty deps
  useEffect(() => {
    // Only run initial check if not already done (protects against React Strict Mode double render)
    if (!initialCheckDoneRef.current) {
      checkAuth();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty deps - only run once on mount, checkAuth is stable

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    csrfToken,
    login,
    signup,
    forgotPassword,
    logout,
    checkAuth,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

