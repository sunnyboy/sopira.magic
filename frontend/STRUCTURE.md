# Frontend Structure

Frontend structure mirrors backend apps structure exactly.

## Directory Structure

```
src/
├── apps/                    # Application modules (mirrors BE apps/)
│   ├── core/               # Core utilities and base components
│   │   ├── components/     # Base components
│   │   ├── hooks/         # Base hooks
│   │   ├── utils/         # Base utilities
│   │   └── index.ts       # Module exports
│   ├── user/              # User management
│   ├── authentification/  # Authentication
│   ├── dashboard/         # Dashboard
│   ├── company/           # Company management
│   ├── factory/           # Factory management
│   ├── productionline/    # Production line
│   ├── utility/           # Utility functions
│   ├── equipment/         # Equipment management
│   ├── resource/          # Resource management
│   ├── worker/            # Worker management
│   ├── material/          # Material management
│   ├── process/          # Process management
│   ├── endpoint/         # External endpoints
│   ├── search/           # Search functionality
│   ├── notification/     # Notifications
│   ├── reporting/        # Reporting
│   ├── analytics/        # Analytics
│   ├── alarm/            # Alarm management
│   ├── api/              # API Gateway
│   ├── audit/            # Audit logs
│   ├── logging/          # Logging
│   ├── file_storage/     # File storage
│   ├── document/         # Document management
│   ├── video/            # Video gallery
│   ├── photo/            # Photo gallery
│   ├── tag/              # Tag management
│   ├── scheduler/        # Scheduler
│   ├── caching/          # Caching
│   ├── state/            # UI state
│   ├── internationalization/ # i18n
│   ├── impex/            # Import/Export
│   ├── mobileapp/        # Mobile app
│   ├── shared/           # Shared components
│   ├── relation/         # Relation management
│   └── generator/        # Data generator
├── components/           # Global shared components
│   ├── ui/               # shadcn/ui base components (Button, Card, Input, etc.)
│   │   └── index.ts     # UI component exports
│   ├── shared/          # Shared business components (used across multiple apps)
│   │   └── index.ts     # Shared component exports
│   └── index.ts         # All component exports
├── lib/                  # Library utilities
│   └── utils.ts          # Utility functions (cn helper)
├── App.tsx               # Main app component
├── main.tsx              # Entry point
└── index.css             # Global styles (Tailwind + CSS variables)
```

## Each App Structure

Each app in `src/apps/` follows the same structure:

```
app_name/
├── components/    # React components
│   └── index.ts   # Component exports
├── hooks/         # Custom React hooks
│   └── index.ts   # Hook exports
├── utils/         # Utility functions
│   └── index.ts   # Utility exports
├── types/         # TypeScript types
│   └── index.ts   # Type exports
└── index.ts       # Main module exports
```

## Styling

- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Component library (installed via CLI)
- **CSS Variables**: Centralized in `src/index.css` for theming
- **Dark Mode**: Supported via CSS variables

## Setup

```bash
cd frontend
npm install
npm run dev
```

## Adding shadcn/ui Components

```bash
npx shadcn-ui@latest add [component-name]
```

Components will be added to `src/components/ui/`.
