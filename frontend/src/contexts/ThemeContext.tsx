//*........................................................
//*       ~/sopira.magic/version_01/frontend/src/contexts/ThemeContext.tsx
//*       Theme management context (light/dark/auto)
//*........................................................

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';

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

  // Save theme to localStorage when changed
  const setTheme = async (newTheme: Theme) => {
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
  };

  // Save theme color to localStorage when changed
  const setThemeColor = async (newColor: ThemeColor) => {
    setThemeColorState(newColor);
    localStorage.setItem('sm-theme-color', newColor);
    
    // Apply immediately
    const root = document.documentElement;
    root.classList.remove('theme-blue', 'theme-green', 'theme-orange');
    root.classList.add(`theme-${newColor}`);
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

