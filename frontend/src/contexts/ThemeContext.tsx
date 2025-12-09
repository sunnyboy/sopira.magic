//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/contexts/ThemeContext.tsx
//*       Theme management context (light/dark/auto)
//*........................................................

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { API_BASE } from '@/config/api';

type Theme = 'light' | 'dark' | 'auto';
type ThemeColor = 'blue' | 'green' | 'orange';

interface ThemeContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  themeColor: ThemeColor;
  setThemeColor: (color: ThemeColor) => void;
  effectiveTheme: 'light' | 'dark'; // Actual theme being applied (resolves 'auto')
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export function useTheme(): ThemeContextType {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  // Initialize theme from localStorage
  const [theme, setThemeState] = useState<Theme>(() => {
    const stored = localStorage.getItem('sm-theme') as Theme | null;
    return stored && ['light', 'dark', 'auto'].includes(stored) ? stored : 'auto';
  });

  // Initialize theme color from localStorage
  const [themeColor, setThemeColorState] = useState<ThemeColor>(() => {
    const stored = localStorage.getItem('sm-theme-color') as ThemeColor | null;
    return stored && ['blue', 'green', 'orange'].includes(stored) ? stored : 'blue';
  });

  // Load theme from user preferences on login
  // Use try-catch to safely access AuthContext (it might not be available yet)
  useEffect(() => {
    let isMounted = true;
    
    const loadTheme = async () => {
      try {
        // Try to get auth context - it might not be available yet
        const authContext = React.useContext ? undefined : undefined; // We'll use a different approach
        // Instead, we'll check if user is authenticated by trying to fetch preferences
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/';
        const res = await fetch(prefsUrl, {
          credentials: 'include',
        });
        
        if (res.ok && isMounted) {
          const data = await res.json();
          const savedTheme = data?.general_settings?.theme;
          if (savedTheme && ['light', 'dark', 'auto'].includes(savedTheme)) {
            // Only update if different to avoid unnecessary re-renders
            setThemeState(prev => {
              if (prev !== savedTheme) {
                localStorage.setItem('sm-theme', savedTheme);
                return savedTheme as Theme;
              }
              return prev;
            });
          }
          
          const savedColor = data?.general_settings?.theme_color;
          if (savedColor && ['blue', 'green', 'orange'].includes(savedColor)) {
            // Only update if different to avoid unnecessary re-renders
            setThemeColorState(prev => {
              if (prev !== savedColor) {
                localStorage.setItem('sm-theme-color', savedColor);
                return savedColor as ThemeColor;
              }
              return prev;
            });
          }
        }
      } catch (err) {
        // Silently fail if not authenticated or other error
        // This is expected before login
      }
    };

    // Try to load theme from backend (will fail silently if not authenticated)
    loadTheme();
    
    return () => {
      isMounted = false;
    };
  }, []); // Only run once on mount

  // Get effective theme (resolve 'auto' to system preference)
  const getEffectiveTheme = (currentTheme: Theme): 'light' | 'dark' => {
    if (currentTheme === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return currentTheme;
  };

  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>(() => {
    const initialTheme = theme;
    const effective = getEffectiveTheme(initialTheme);
    
    // Apply immediately to prevent flash
    const root = document.documentElement;
    if (effective === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Apply theme color
    const storedColor = localStorage.getItem('sm-theme-color') as ThemeColor | null;
    const initialColor = storedColor && ['blue', 'green', 'orange'].includes(storedColor) ? storedColor : 'blue';
    root.classList.remove('theme-blue', 'theme-green', 'theme-orange');
    root.classList.add(`theme-${initialColor}`);
    
    return effective;
  });

  // Apply theme to HTML element
  useEffect(() => {
    const applyTheme = () => {
      // Get effective theme based on current theme state
      let effective: 'light' | 'dark';
      if (theme === 'auto') {
        effective = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      } else {
        effective = theme;
      }
      
      setEffectiveTheme(effective);
      
      // Apply to HTML element
      const root = document.documentElement;
      if (effective === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    };

    // Apply immediately
    applyTheme();

    // Listen for system theme changes when in 'auto' mode
    if (theme === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = () => {
        applyTheme();
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [theme]);

  // Apply theme color to HTML element
  useEffect(() => {
    const root = document.documentElement;
    root.classList.remove('theme-blue', 'theme-green', 'theme-orange');
    root.classList.add(`theme-${themeColor}`);
  }, [themeColor]);

  // Save theme to localStorage and backend when changed
  const setTheme = async (newTheme: Theme, skipBackendSave: boolean = false) => {
    // Skip if value hasn't changed
    if (theme === newTheme) return;
    
    // Update state immediately
    setThemeState(newTheme);
    localStorage.setItem('sm-theme', newTheme);
    
    // Apply theme immediately (before async save)
    const root = document.documentElement;
    let effective: 'light' | 'dark';
    if (newTheme === 'auto') {
      effective = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    } else {
      effective = newTheme;
    }
    
    if (effective === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    setEffectiveTheme(effective);
    
    // Apply theme color
    root.classList.remove('theme-blue', 'theme-green', 'theme-orange');
    root.classList.add(`theme-${themeColor}`);

    // Save to backend only if skipBackendSave is false and user is authenticated
    if (!skipBackendSave) {
      try {
        // Get current preferences
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/';
        const prefRes = await fetch(prefsUrl, {
          credentials: 'include',
        });
        
        if (prefRes.ok) {
          const prefData = await prefRes.json();
          const existingSettings = prefData?.general_settings || {};
          
          // Only save if theme actually changed in backend
          if (existingSettings.theme !== newTheme) {
            // Update theme in general_settings
            const updatedSettings = {
              ...existingSettings,
              theme: newTheme,
              theme_color: themeColor, // Include current theme color
            };

            // Get CSRF token from cookie if available
            function getCookie(name: string): string | null {
              const value = `; ${document.cookie}`;
              const parts = value.split(`; ${name}=`);
              if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
              return null;
            }

            const csrfToken = getCookie('csrftoken');

            // Save updated preferences
            await fetch(prefsUrl, {
              method: 'PUT',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
              },
              body: JSON.stringify({
                selected_factories: prefData?.selected_factories || [],
                general_settings: updatedSettings,
              }),
            });
          }
        }
      } catch (err) {
        // Silently fail if not authenticated or other error
        // This is expected before login
      }
    }
  };

  // Save theme color to localStorage and backend when changed
  const setThemeColor = async (newColor: ThemeColor, skipBackendSave: boolean = false) => {
    // Skip if value hasn't changed
    if (themeColor === newColor) return;
    
    setThemeColorState(newColor);
    localStorage.setItem('sm-theme-color', newColor);
    
    // Apply immediately
    const root = document.documentElement;
    root.classList.remove('theme-blue', 'theme-green', 'theme-orange');
    root.classList.add(`theme-${newColor}`);

    // Save to backend only if skipBackendSave is false and user is authenticated
    if (!skipBackendSave) {
      try {
        const prefsUrl = API_BASE 
          ? `${API_BASE}/api/user/preferences/`
          : '/api/user/preferences/';
        const prefRes = await fetch(prefsUrl, {
          credentials: 'include',
        });
        
        if (prefRes.ok) {
          const prefData = await prefRes.json();
          const existingSettings = prefData?.general_settings || {};
          
          // Only save if theme_color actually changed in backend
          if (existingSettings.theme_color !== newColor) {
            const updatedSettings = {
              ...existingSettings,
              theme_color: newColor,
            };

            // Get CSRF token from cookie if available
            function getCookie(name: string): string | null {
              const value = `; ${document.cookie}`;
              const parts = value.split(`; ${name}=`);
              if (parts.length === 2) return parts.pop()?.split(';').shift() || null;
              return null;
            }

            const csrfToken = getCookie('csrftoken');

            await fetch(prefsUrl, {
              method: 'PUT',
              credentials: 'include',
              headers: {
                'Content-Type': 'application/json',
                ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}),
              },
              body: JSON.stringify({
                selected_factories: prefData?.selected_factories || [],
                general_settings: updatedSettings,
              }),
            });
          }
        }
      } catch (err) {
        // Silently fail if not authenticated or other error
        // This is expected before login
      }
    }
  };

  const value: ThemeContextType = {
    theme,
    setTheme,
    themeColor,
    setThemeColor,
    effectiveTheme,
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
};

