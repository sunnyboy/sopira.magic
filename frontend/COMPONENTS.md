# Component Organization Guide

## Component Hierarchy

### 1. UI Components (`src/components/ui/`)
**Purpose**: Base UI primitives from shadcn/ui
**When to use**: Low-level UI building blocks
**Examples**: Button, Card, Input, Select, Dialog, etc.

```tsx
import { Button, Card } from '@/components/ui'
```

### 2. Shared Components (`src/components/shared/`)
**Purpose**: Business-logic components shared across multiple apps
**When to use**: Components used by 2+ apps with business logic
**Examples**: MyTable, FieldFactory, DataTable, FormBuilder, etc.

```tsx
import { MyTable, FieldFactory } from '@/components/shared'
```

### 3. App-specific Components (`src/apps/{app}/components/`)
**Purpose**: Components specific to one app
**When to use**: Components only used by one app
**Examples**: CompanyForm, FactoryList, etc.

```tsx
import { CompanyForm } from '@/apps/company/components'
```

### 4. Shared App Module (`src/apps/shared/`)
**Purpose**: Shared utilities, hooks, types (not React components)
**When to use**: Reusable logic, hooks, utilities, types
**Examples**: useApi hook, API client, common types

```tsx
import { useApi } from '@/apps/shared/hooks'
import { ApiClient } from '@/apps/shared/utils'
```

## Decision Tree

```
Is it a React component?
├─ Yes
│  ├─ Is it a base UI primitive (Button, Input, etc.)?
│  │  └─ Yes → src/components/ui/
│  │
│  └─ Is it used by 2+ apps?
│     ├─ Yes → src/components/shared/
│     └─ No → src/apps/{app}/components/
│
└─ No (hook, util, type)
   └─ src/apps/shared/
```

## Examples

### UI Component (shadcn/ui)
```tsx
// src/components/ui/button.tsx
export { Button } from './button'
```

### Shared Business Component
```tsx
// src/components/shared/MyTable.tsx
export { MyTable } from './MyTable'

// Used in multiple apps:
import { MyTable } from '@/components/shared'
```

### App-specific Component
```tsx
// src/apps/company/components/CompanyForm.tsx
export { CompanyForm } from './CompanyForm'

// Used only in company app:
import { CompanyForm } from '@/apps/company/components'
```

### Shared Hook
```tsx
// src/apps/shared/hooks/useApi.ts
export { useApi } from './useApi'

// Used in multiple apps:
import { useApi } from '@/apps/shared/hooks'
```
