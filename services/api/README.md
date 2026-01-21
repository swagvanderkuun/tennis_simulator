# Tournament Studio API

FastAPI backend for tennis tournament analytics and simulation.

## Features

- **Players API**: Query players, Elo history, form movers
- **Tournaments API**: Active tournaments, draw sources
- **Matchups API**: Match simulation with explainability
- **Draws API**: Draw snapshots, bracket tree, probabilities
- **Simulations API**: Scenario simulation, weight presets
- **Scorito API**: Fantasy optimization, value picks

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL + SQLAlchemy
- **Cache**: Redis
- **Validation**: Pydantic

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- Redis (optional)

### Installation

```bash
cd services/api
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```bash
DATABASE_URL=postgresql://tennis:tennis@localhost:5432/tennis
REDIS_URL=redis://localhost:6379/0
CORS_ORIGINS=["http://localhost:3000"]
DEBUG=true
```

### Development

```bash
uvicorn app.main:app --reload --port 8000
```

### API Documentation

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Project Structure

```
services/api/
├── app/
│   ├── core/              # Configuration
│   ├── db/                # Database session & cache
│   ├── routers/           # API endpoints
│   ├── schemas/           # Pydantic models
│   ├── services/          # Business logic
│   └── main.py            # FastAPI app
└── requirements.txt
```

## API Endpoints

### Players
- `GET /api/v1/players` - List players with filters
- `GET /api/v1/players/{id}` - Get player by ID
- `GET /api/v1/players/{id}/elo_history` - Get Elo history
- `GET /api/v1/players/form_movers` - Get form movers

### Tournaments
- `GET /api/v1/tournaments` - List tournaments
- `GET /api/v1/tournaments/active` - Get active tournament
- `GET /api/v1/tournaments/{id}` - Get tournament by ID

### Matchups
- `POST /api/v1/matchups/simulate` - Simulate match
- `GET /api/v1/matchups/explain` - Get match explanation

### Draws
- `GET /api/v1/draws/{tournament_id}/latest` - Get latest snapshot
- `GET /api/v1/draws/{snapshot_id}/tree` - Get draw tree
- `GET /api/v1/draws/{snapshot_id}/probabilities` - Get probabilities

### Simulations
- `GET /api/v1/simulations/presets` - Get weight presets
- `POST /api/v1/simulations/scenario` - Run scenario

### Scorito
- `POST /api/v1/scorito/optimize` - Optimize lineup
- `GET /api/v1/scorito/value_picks` - Get value picks
- `POST /api/v1/scorito/score` - Calculate score

## Docker

```bash
docker build -t tennis-studio-api .
docker run -p 8000:8000 tennis-studio-api
```



