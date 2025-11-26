# Shared Components

Shared business components that are used across multiple apps.

## Examples of Shared Components

- `MyTable` - Universal table component with sorting, filtering, pagination
- `FieldFactory` - Dynamic field renderer based on field type
- `ScopedFKCell` - Foreign key cell component for tables
- `useOptimisticField` - Hook for optimistic field updates
- `DataTable` - Advanced data table with all features
- `FormBuilder` - Dynamic form builder
- `SearchBar` - Universal search component
- `FilterPanel` - Filter panel component
- `Pagination` - Pagination component
- `LoadingSpinner` - Loading indicator
- `ErrorBoundary` - Error boundary component
- `ConfirmDialog` - Confirmation dialog
- `Toast` - Toast notification component

## Usage

```tsx
import { MyTable, FieldFactory } from '@/components/shared'
```

## When to use Shared vs App-specific

- **Shared components**: Used by 2+ apps, contain business logic, reusable patterns
- **App-specific components**: Used only by one app, specific to that app's domain

