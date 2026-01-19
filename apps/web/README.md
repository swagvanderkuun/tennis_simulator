# Tournament Studio Web App

A professional tennis tournament analytics dashboard built with Next.js, TypeScript, and Tailwind CSS.

## Features

- **Home**: Tournament spotlight, top picks, predictions summary
- **Players**: Filter, search, compare players with Elo trends and radar charts
- **Matchups**: Head-to-head simulation with win probability and explainability
- **Brackets**: Interactive D3 bracket tree with probability flow
- **Sim Lab**: Weight configuration, scenario heatmaps, impact sliders
- **Scorito**: Fantasy optimization with value picks and risk profiles

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Components**: shadcn/ui (Radix)
- **Charts**: ECharts + D3
- **State**: React hooks + Zustand

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn

### Installation

```bash
cd apps/web
npm install
```

### Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Production Build

```bash
npm run build
npm run start
```

## Project Structure

```
apps/web/
├── app/                    # Next.js app router pages
│   ├── page.tsx           # Home page
│   ├── players/           # Players page
│   ├── matchups/          # Matchups page
│   ├── brackets/          # Brackets page
│   ├── sim-lab/           # Sim Lab page
│   └── scorito/           # Scorito page
├── components/
│   ├── charts/            # ECharts & D3 visualizations
│   ├── layout/            # AppShell, SideNav, TopBar
│   ├── pages/             # Page-level components
│   └── ui/                # shadcn/ui components
├── lib/
│   ├── api.ts             # API client
│   └── utils.ts           # Utility functions
└── styles/
    └── globals.css        # Theme & global styles
```

## Design System

### Colors

- **Primary**: Court green (`#38E07C`)
- **Secondary**: Broadcast cyan (`#4CC9F0`)
- **Accent**: Fantasy gold (`#F9C74F`)
- **Danger**: Risk magenta (`#F72585`)

### Typography

- **Display**: Space Grotesk
- **Body**: Inter
- **Mono**: IBM Plex Mono

## API Integration

The frontend connects to the FastAPI backend at `/api/v1`. Configure the API URL:

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

## Docker

Build and run with Docker:

```bash
docker build -t tennis-studio-web .
docker run -p 3000:3000 tennis-studio-web
```


