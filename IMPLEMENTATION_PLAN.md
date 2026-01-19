## Implementation Plan: Tournament Studio + Scorito Pro Web App

This plan translates the full UI spec (IA, wireframes, components) into
implementation steps with concrete deliverables, dependencies, and checkpoints.

---

## 1) Scope, Success Criteria, and Non-Goals

### Scope
- Build a production-grade web app using:
  - Frontend: Next.js + TypeScript + Tailwind + shadcn/ui
  - Charts: ECharts (primary) + D3 for bracket tree
  - Backend: FastAPI + SQLAlchemy
  - Infra: Docker + Postgres + Redis
- Implement the full IA:
  - Home, Players, Matchups, Brackets, Sim Lab, Scorito
- Implement the UI/UX ideas:
  - Confidence bands on Elo trajectories
  - Explainability panel
  - Scenario heatmap
  - Impact sliders
  - Matchup radar charts

### Success Criteria
- All IA pages match the spec, with real data powering core views.
- Core sim features from Streamlit are migrated.
- UX is consistent with the broadcast + fantasy theme.
- API supports caching and can scale to typical dashboard usage.

### Non-Goals (v1)
- Public account management / payments
- Real-time live scoring integration
- Fully automated editorial content generation

---

## 2) Architecture Overview

### Frontend
- Next.js App Router
- Tailwind + shadcn/ui
- ECharts components with shared wrapper
- D3-based bracket visualization

### Backend
- FastAPI app with versioned routers
- SQLAlchemy models for Postgres
- Redis for caching heavy or repeated queries

### Data Contracts
- Define shared types in `/packages/shared` (JSON schemas + TS types)
- Keep parity between DB schema and frontend types

---

## 3) Page-by-Page Implementation Plan

### 3.1 Home

#### Wireframe Elements
- Tournament Spotlight Hero
- Top Picks Carousel
- Prediction Summary Cards
- Form Movers
- Surface Specialists

#### Components
- `TournamentSpotlightHero`
- `TopPicksCarousel`
- `PredictionSummaryCards`
- `FormMoversList`
- `SurfaceSpecialistGrid`

#### Backend Needs
- GET `/tournaments/active`
- GET `/predictions/summary?tournament_id=...`
- GET `/players/top_picks?tournament_id=...`
- GET `/players/form_movers?tour=...`

#### Frontend Tasks
- Create layout and hero section
- Implement card-driven summary UI
- Wire data + loading states

---

### 3.2 Players

#### Wireframe Elements
- Filter panel
- Player table
- Player profile
- Elo trend with confidence bands
- Radar chart

#### Components
- `PlayerFilterPanel`
- `PlayerTable`
- `PlayerProfileCard`
- `EloTrendChart`
- `PlayerRadarChart`

#### Backend Needs
- GET `/players?filters=...`
- GET `/players/{id}`
- GET `/players/{id}/elo_history`

#### Frontend Tasks
- Implement filter -> query state sync
- Build table with sorting + tags
- Profile view and side panel
- Elo trend chart with confidence bands

---

### 3.3 Matchups

#### Wireframe Elements
- Player vs Player selector
- Win prob gauge
- Scoreline distribution
- Explainability panel
- H2H timeline

#### Components
- `MatchupSelector`
- `WinProbabilityGauge`
- `ScorelineDistributionChart`
- `ExplainabilityPanel`
- `HeadToHeadTimeline`

#### Backend Needs
- POST `/matchups/simulate`
- GET `/matchups/h2h?player1=...&player2=...`
- GET `/matchups/explain?player1=...&player2=...`

#### Frontend Tasks
- Create selection UX + query params
- Hook into simulation endpoint
- Explainability panel layout and data blocks

---

### 3.4 Brackets

#### Wireframe Elements
- Tournament selector
- Interactive D3 bracket
- Probability flow panel
- Upset watch

#### Components
- `BracketTree`
- `ProbabilityFlowPanel`
- `PathDifficultyCard`
- `UpsetWatchList`

#### Backend Needs
- GET `/draws/{tournament_id}/latest`
- GET `/draws/{snapshot_id}/tree`
- GET `/draws/{snapshot_id}/probabilities`

#### Frontend Tasks
- Build D3 bracket tree component
- Implement selection and rerender
- Show probability flow in side panel

---

### 3.5 Sim Lab

#### Wireframe Elements
- Weights sliders + presets
- Scenario heatmap
- Impact sliders
- Scenario comparison table

#### Components
- `WeightsPanel`
- `ScenarioHeatmap`
- `ImpactSliders`
- `ScenarioComparisonTable`

#### Backend Needs
- POST `/simulations/scenario`
- GET `/simulations/presets`

#### Frontend Tasks
- Implement slider state + validation
- Heatmap integration and tooltip logic
- Compare saved scenarios

---

### 3.6 Scorito

#### Wireframe Elements
- Scoring rules editor
- Optimizer output
- Expected value chart
- Risk profile panel
- Value picks list

#### Components
- `ScoringRulesEditor`
- `LineupOptimizerTable`
- `ExpectedValueChart`
- `RiskProfilePanel`
- `ValuePicksList`

#### Backend Needs
- POST `/scorito/optimize`
- POST `/scorito/score`
- GET `/scorito/value_picks`

#### Frontend Tasks
- Editable scoring table
- Optimization output table + EV chart
- Risk profile visualization

---

## 4) Shared UX Components & Patterns

### Global Components
- `AppShell`, `TopBar`, `SideNav`
- `TournamentSelector`
- `SurfaceToggle`
- `ContextChips`
- `KpiStrip`

### Shared Behaviors
- Consistent loading skeletons
- Error banners with retry
- Data freshness indicator

---

## 5) Backend Data & API Design

### Key Models (SQLAlchemy)
- `Player`, `EloSnapshot`, `EloRating`
- `DrawSource`, `DrawSnapshot`, `DrawMatch`, `DrawEntry`
- `TierSet`, `TierAssignment`

### API Conventions
- REST JSON with consistent pagination
- Cache frequent endpoints in Redis
- Versioned API (`/api/v1`)

### Caching Strategy
- Redis for:
  - draw snapshots
  - player list queries
  - computed probabilities
- Cache invalidation on snapshot update

---

## 6) Design System Implementation

### Theme Tokens
- Define CSS variables for:
  - background, surface, elevated
  - primary, secondary, accent, danger
  - text, muted

### Typography
- Configure:
  - `Space Grotesk` for display
  - `Inter` for body
  - `IBM Plex Mono` for metrics

### Motion
- Subtle hover glow on key cards
- Animated odds updates (micro trend)

---

## 7) Infrastructure and DevOps

### Docker
- `docker-compose` with:
  - `web` (Next.js)
  - `api` (FastAPI)
  - `db` (Postgres)
  - `cache` (Redis)

### Environments
- `.env` files for local and prod
- Secrets handled via environment variables

---

## 8) Migration from Streamlit

### Step-by-step
1) Extract data access logic into API services
2) Recreate Streamlit views in React
3) Validate parity for simulations
4) Move tier editing to admin-only area
5) Decommission Streamlit dashboard

### Risk Mitigation
- Keep Streamlit live until parity achieved
- Use snapshot compare to validate results

---

## 9) Milestones and Phases

### Phase 1: Foundation (Week 1–2)
- Repo structure
- App shell + routing
- Base theme system
- API scaffolding

### Phase 2: Core Data (Week 3–4)
- Players and Elo history endpoints
- Matchup sim endpoint
- Draw endpoints

### Phase 3: Page Implementation (Week 5–7)
- Home, Players, Matchups, Brackets
- Sim Lab + Scorito

### Phase 4: UX Polishing (Week 8)
- Explainability panel
- Scenario heatmap
- Impact sliders
- Confidence bands

---

## 10) Testing and Validation

### Frontend
- Component tests (React Testing Library)
- E2E smoke tests (Playwright)

### Backend
- Unit tests for simulation + data queries
- API contract tests

### Acceptance
- Cross-check Streamlit outputs
- Visual regression for charts and bracket

---

## 11) Deliverables Checklist

- [ ] UI layouts for all IA pages
- [ ] Component library & theme tokens
- [ ] D3 bracket visualization
- [ ] FastAPI endpoints for all data sources
- [ ] Redis caching on expensive queries
- [ ] Dockerized infrastructure
- [ ] Migration parity validated

