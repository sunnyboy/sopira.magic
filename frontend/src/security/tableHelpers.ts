/************************************************************************
 *  src/utils/tableHelpers.ts
 *  Shared utility functions for table components
 ************************************************************************/

import { useEffect, useState } from 'react';
import React from 'react';

/**
 * Debounce hook - delays updating value until after specified delay
 */
export function useDebounced<T>(value: T, delay = 300): T {
  const [deb, setDeb] = useState(value);
  useEffect(() => {
    const h = setTimeout(() => setDeb(value), delay);
    return () => clearTimeout(h);
  }, [value, delay]);
  return deb;
}

/**
 * Extract search terms from search query (removes operators, handles quotes)
 */
export function extractSearchTerms(searchQuery: string): string[] {
  if (!searchQuery) return [];
  const terms: string[] = [];
  const tokens = searchQuery.match(/"[^"]+"|[^\s]+/g) || [];
  for (const tok of tokens) {
    // Remove quotes and parentheses
    const clean = tok.replace(/["()]/g, '').trim();
    if (clean && !['AND', 'OR', 'NOT'].includes(clean.toUpperCase())) {
      terms.push(clean);
    }
  }
  return terms;
}

/**
 * Highlight matching search terms in text
 */
export function highlightText(text: string, searchTerms: string[]): React.ReactNode {
  if (!text || !searchTerms.length) return text;
  const parts: React.ReactNode[] = [];
  let remaining = String(text);
  let key = 0;

  while (remaining.length > 0) {
    let earliestIndex = -1;
    let matchedTerm = '';

    for (const term of searchTerms) {
      const index = remaining.toLowerCase().indexOf(term.toLowerCase());
      if (index !== -1 && (earliestIndex === -1 || index < earliestIndex)) {
        earliestIndex = index;
        matchedTerm = term;
      }
    }

    if (earliestIndex === -1) {
      parts.push(React.createElement('span', { key: key++ }, remaining));
      break;
    }

    if (earliestIndex > 0) {
      parts.push(React.createElement('span', { key: key++ }, remaining.substring(0, earliestIndex)));
    }

    const actualMatch = remaining.substring(earliestIndex, earliestIndex + matchedTerm.length);
    parts.push(
      React.createElement(
        'mark',
        { 
          key: key++, 
          style: { background: 'rgba(255,255,0,0.5)', padding: '0 2px', borderRadius: '2px' } 
        },
        actualMatch
      )
    );

    remaining = remaining.substring(earliestIndex + matchedTerm.length);
  }

  return React.createElement(React.Fragment, null, ...parts);
}

/**
 * Build query parameters for date range filter
 * If only 'from' is set -> exact match
 * If both 'from' and 'to' are set -> range
 * 
 * @param params - URLSearchParams to append to
 * @param filterValue - Filter value with from/to dates
 * @param options - Either fieldName string or {exact, from, to} parameter names
 */
export function buildDateRangeParams(
  params: URLSearchParams,
  filterValue: { from?: string; to?: string } | undefined,
  options: string | { exact: string; from: string; to: string }
) {
  if (!filterValue) return;
  const { from, to } = filterValue;
  
  // Determine parameter names
  const paramNames = typeof options === 'string'
    ? { exact: options, from: `${options}_from`, to: `${options}_to` }
    : options;
  
  if (from && !to) {
    // Exact match
    params.set(paramNames.exact, from);
  } else if (from && to) {
    // Range
    params.set(paramNames.from, from);
    params.set(paramNames.to, to);
  } else if (!from && to) {
    // Only 'to' (edge case)
    params.set(paramNames.to, to);
  }
}

/**
 * Build query parameters for time range filter
 * Same logic as date range: exact if only 'from', range if both
 * 
 * @param params - URLSearchParams to append to
 * @param filterValue - Filter value with from/to times
 * @param options - Either fieldName string or {exact, from, to} parameter names
 */
export function buildTimeRangeParams(
  params: URLSearchParams,
  filterValue: { from?: string; to?: string } | undefined,
  options: string | { exact: string; from: string; to: string }
) {
  if (!filterValue) return;
  const { from, to } = filterValue;
  
  // Determine parameter names
  const paramNames = typeof options === 'string'
    ? { exact: options, from: `${options}_from`, to: `${options}_to` }
    : options;
  
  if (from && !to) {
    // Exact match
    params.set(paramNames.exact, from);
  } else if (from && to) {
    // Range
    params.set(paramNames.from, from);
    params.set(paramNames.to, to);
  } else if (!from && to) {
    // Only 'to' (edge case)
    params.set(paramNames.to, to);
  }
}

/**
 * Build query parameters for numeric range filter
 */
export function buildNumericRangeParams(
  params: URLSearchParams,
  filterValue: { min?: number; max?: number } | undefined,
  fieldName: string
) {
  if (!filterValue || typeof filterValue !== 'object') return;
  const { min, max } = filterValue;
  
  if (min !== undefined && !Number.isNaN(min)) {
    params.set(`${fieldName}_min`, String(min));
  }
  if (max !== undefined && !Number.isNaN(max)) {
    params.set(`${fieldName}_max`, String(max));
  }
}

/**
 * Build query parameters for text contains filter
 * @param params - URLSearchParams to append to
 * @param filterValue - Filter value (string)
 * @param fieldName - Field name (e.g., 'id', 'pit_number', 'comment')
 */
export function buildTextContainsParams(
  params: URLSearchParams,
  filterValue: string | undefined,
  fieldName: string
) {
  if (filterValue && String(filterValue).trim()) {
    params.set(`${fieldName}_icontains`, String(filterValue));
  }
}

/**
 * Build query parameters for tags filter (comma-separated list)
 * @param params - URLSearchParams to append to
 * @param filterValue - Filter value (comma-separated string of tag names)
 */
export function buildTagsParams(
  params: URLSearchParams,
  filterValue: string | undefined
) {
  if (filterValue && String(filterValue).trim()) {
    params.set('tags', String(filterValue).trim());
  }
}
