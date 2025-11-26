# Sopira Magic Frontend

React 19 frontend application with TypeScript, Vite, Tailwind CSS, and shadcn/ui.

## Structure

Frontend structure mirrors backend apps structure:

```
src/
├── apps/                    # Application modules (mirrors BE apps)
│   ├── core/               # Core utilities and base components
│   ├── user/               # User management
│   ├── authentification/   # Authentication
│   ├── dashboard/          # Dashboard
│   ├── company/            # Company management
│   ├── factory/            # Factory management
│   ├── productionline/     # Production line
│   ├── utility/            # Utility functions
│   ├── equipment/          # Equipment management
│   ├── resource/           # Resource management
│   ├── worker/             # Worker management
│   ├── material/           # Material management
│   ├── process/            # Process management
│   ├── endpoint/           # External endpoints
│   ├── search/             # Search functionality
│   ├── notification/       # Notifications
│   ├── reporting/          # Reporting
│   ├── analytics/          # Analytics
│   ├── alarm/              # Alarm management
│   ├── api/                # API Gateway
│   ├── audit/              # Audit logs
│   ├── logging/            # Logging
│   ├── file_storage/       # File storage
│   ├── document/           # Document management
│   ├── video/              # Video gallery
│   ├── photo/              # Photo gallery
│   ├── tag/                # Tag management
│   ├── scheduler/          # Scheduler
│   ├── caching/            # Caching
│   ├── state/              # UI state
│   ├── internationalization/ # i18n
│   ├── impex/              # Import/Export
│   ├── mobileapp/          # Mobile app
│   ├── shared/             # Shared components
│   ├── relation/           # Relation management
│   └── generator/          # Data generator
├── components/             # Global components
│   └── ui/                 # shadcn/ui components
├── lib/                    # Library utilities
└── App.tsx                 # Main app component
```

## Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Styling

- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: Component library built on Radix UI
- Centralized CSS in `src/index.css` with CSS variables for theming

## Development

- Development server runs on `http://localhost:5173`
- API proxy configured to `http://localhost:8000`
- TypeScript for type safety
- Path aliases: `@/*` maps to `./src/*`

