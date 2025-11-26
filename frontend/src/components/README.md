# Components Directory

## Structure

```
components/
├── ui/              # shadcn/ui base components (Button, Card, Input, etc.)
│   └── index.ts    # UI component exports
├── shared/         # Shared business components (used across multiple apps)
│   └── index.ts    # Shared component exports
└── index.ts        # All component exports
```

## Usage

### UI Components (shadcn/ui)
Base UI components from shadcn/ui library. These are low-level, reusable UI primitives.

```tsx
import { Button, Card } from '@/components/ui'
```

### Shared Components
Business-logic components that are shared across multiple apps. These are higher-level components that combine UI components with business logic.

```tsx
import { MyTable, FieldFactory } from '@/components/shared'
```

### App-specific Components
Components specific to a single app should be in `src/apps/{app_name}/components/`

```tsx
import { CompanyForm } from '@/apps/company/components'
```

## Adding Components

### Adding shadcn/ui components:
```bash
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
```

### Adding shared components:
Create component in `src/components/shared/` and export from `src/components/shared/index.ts`

### Adding app-specific components:
Create component in `src/apps/{app_name}/components/` and export from `src/apps/{app_name}/components/index.ts`

