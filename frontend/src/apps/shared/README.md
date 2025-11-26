# Shared App Module

This app module contains shared utilities, hooks, and types that are used across multiple apps.

## Structure

```
shared/
├── components/    # Shared components specific to this module
├── hooks/         # Shared hooks (e.g., useApi, useAuth)
├── utils/         # Shared utility functions
├── types/         # Shared TypeScript types
└── index.ts       # Module exports
```

## Difference from `src/components/shared/`

- **`src/components/shared/`**: React components (UI + business logic)
- **`src/apps/shared/`**: Utilities, hooks, types, and module-specific components

## Examples

### Hooks
- `useApi` - API call hook
- `useAuth` - Authentication hook
- `useLocalStorage` - Local storage hook
- `useDebounce` - Debounce hook

### Utils
- API client functions
- Data transformation utilities
- Validation helpers

### Types
- Common TypeScript interfaces
- API response types
- Shared enums

