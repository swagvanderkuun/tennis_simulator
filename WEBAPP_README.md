# Tournament Studio - Professional Tennis Analytics Web App

A modern, broadcast-grade web application for tennis tournament analytics, simulation, and fantasy optimization.

## Overview

Tournament Studio transforms the existing Streamlit dashboard into a professional web application with:

- **Broadcast-grade aesthetics**: Dark theme with court-green accents
- **Fantasy/Scorito optimization**: Value picks and risk profiling
- **Interactive visualizations**: ECharts + D3 bracket trees
- **Real-time simulations**: Impact sliders and scenario heatmaps

## Architecture

```
tennis_simulator/
├── apps/
│   └── web/                # Next.js frontend
├── services/
│   └── api/                # FastAPI backend
├── infra/
│   └── docker/             # Docker infrastructure
└── packages/
    └── shared/             # Shared types
```

## Quick Start

### Option 1: Docker (Recommended)

```bash
cd infra/docker
./scripts/up.sh
```

Access:
- Frontend: http://localhost:3003
- API: http://localhost:8001
- API Docs: http://localhost:8001/api/docs

> **Note:** Ports are configured to avoid conflicts with existing containers:
> - Web: 3003 (avoids 3000-3002 used by other apps)
> - API: 8001 (avoids 8000/8080)
> - Postgres: 5435 (avoids 5432-5434)
> - Redis: 6380 (avoids 6379)

### Option 2: Manual Development

**Backend:**
```bash
cd services/api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd apps/web
npm install
npm run dev
```

## Pages

### Home
- Tournament spotlight with live predictions
- Top picks carousel with win probabilities
- Form movers and surface specialists
- Quick actions for navigation

### Players
- Searchable player database
- Filter by tier (A, B, C, D)
- Player profile with Elo trend charts
- Surface profile radar charts
- Confidence bands on Elo trajectories

### Matchups
- Head-to-head player comparison
- Win probability gauge
- Explainability panel (why this probability?)
- Score distribution chart
- Surface profile comparison

### Brackets
- Interactive D3 bracket tree
- Probability flow visualization
- Upset watch alerts
- Click nodes for match details

### Sim Lab
- Weight configuration sliders
- Preset configurations
- Scenario heatmaps (surface × form)
- Sensitivity analysis
- Real-time impact preview

### Scorito
- Scoring rules editor
- Value picks optimizer
- Expected value calculations
- Risk profile visualization
- Tier-based analysis

## Design System

### Colors
| Token | Value | Usage |
|-------|-------|-------|
| Primary | `#38E07C` | Court green, wins, positive |
| Secondary | `#4CC9F0` | Broadcast cyan, stats |
| Accent | `#F9C74F` | Fantasy gold, value picks |
| Danger | `#F72585` | Risk magenta, losses |

### Typography
- **Display**: Space Grotesk (headings)
- **Body**: Inter (text)
- **Mono**: IBM Plex Mono (numbers, stats)

### Components
- Glass cards with backdrop blur
- Metric cards with left accent
- Tier badges (color-coded)
- Probability bars
- Interactive sliders

## API Endpoints

See `services/api/README.md` for full API documentation.

## Migration from Streamlit

The new web app replaces the Streamlit dashboard with enhanced features:

| Streamlit Feature | Web App Equivalent |
|-------------------|-------------------|
| Database Overview | Home + Players pages |
| Player Search | Players page with filters |
| Match Simulation | Matchups page |
| Elo Weights | Sim Lab page |
| Tournament Explorer | Brackets + Sim Lab |
| Scorito Analysis | Scorito page |
| Tier Editor | (Admin area - TBD) |

## Development

### Frontend Development
```bash
cd apps/web
npm run dev      # Development server
npm run build    # Production build
npm run lint     # Run linter
```

### Backend Development
```bash
cd services/api
uvicorn app.main:app --reload
```

### Full Stack (Docker)
```bash
cd infra/docker
./scripts/dev.sh   # Development mode with hot reload
./scripts/up.sh    # Production mode
./scripts/down.sh  # Stop all services
./scripts/logs.sh  # View logs
```

## Contributing

1. Follow the design system for consistency
2. Add TypeScript types for all data
3. Use the shared types package
4. Write API schemas for new endpoints

## License

Private - Tennis Simulator Project

