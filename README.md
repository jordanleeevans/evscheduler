# Smart EV Charging Scheduler

Intelligently schedules EV charging during the cheapest half-hourly Octopus Agile tariff slots before your departure time.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Browser                               │
│  React + Apollo Client  →  /graphql  ←→  Vite Dev Proxy     │
└─────────────────────────────┬───────────────────────────────┘
                               │
              ┌────────────────▼────────────────┐
              │      FastAPI + Ariadne GraphQL   │
              │         (port 8000)              │
              └────┬───────────────────┬─────────┘
                   │                   │
        ┌──────────▼──────┐   ┌────────▼────────┐
        │  SQLite / SQLAlch│   │  Celery Worker   │
        │  ORM (models)    │   │  (schedule tasks)│
        └─────────────────┘   └────────┬─────────┘
                                        │
                               ┌────────▼────────┐
                               │   Redis Broker   │
                               │   (port 6379)    │
                               └─────────────────┘
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite, Apollo Client, Recharts |
| API | FastAPI, Ariadne (GraphQL), Python 3.14 |
| ORM | SQLAlchemy 2.0, SQLite (dev) |
| Task Queue | Celery 5, Redis |
| Tariff Data | Octopus Energy Agile API (mocked) |

## Quick Start (Docker Compose)

```bash
git clone <repo-url>
cd evscheduler
docker-compose up --build
```

- Frontend: http://localhost:3000  
- GraphQL Playground: http://localhost:8000/graphql  
- API Health: http://localhost:8000/health  

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt

# Run API server
uvicorn app.main:app --reload --port 8000

# Run Celery worker (separate terminal)
celery -A app.celery_app worker --loglevel=info

# Run tests
pytest tests/ -v
```

### Frontend

```bash
cd frontend
npm install
npm run dev   # starts at http://localhost:5173
```

## GraphQL API

Open http://localhost:8000/graphql for the interactive playground.

### Example Queries

```graphql
# List all vehicles
{ vehicles { id name batteryCapacityKwh currentBatteryPct } }

# Get tariff prices for next 24h
{ tariffPrices(from: "2024-01-15T00:00:00", to: "2024-01-16T00:00:00") {
    slotStart slotEnd pricePerKwh
  }
}
```

### Example Mutations

```graphql
# Register a vehicle
mutation {
  createVehicle(name: "Tesla Model 3", batteryCapacityKwh: 75, currentBatteryPct: 30) {
    id name
  }
}

# Schedule a charging session
mutation {
  scheduleChargingSession(
    vehicleId: "1"
    departureTime: "2024-01-16T07:30:00"
    targetChargePct: 80
  ) {
    id status slots { slotStart pricePerKwh isSelected }
  }
}
```

## Project Structure

```
evscheduler/
├── backend/
│   ├── app/
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── resolvers/       # Ariadne GraphQL resolvers
│   │   ├── services/        # Tariff feed + scheduler logic
│   │   ├── tasks/           # Celery async tasks
│   │   ├── schema.graphql   # GraphQL schema
│   │   ├── database.py      # DB engine + session
│   │   ├── celery_app.py    # Celery configuration
│   │   └── main.py          # FastAPI app entry point
│   └── tests/               # pytest test suite
├── frontend/
│   └── src/
│       ├── components/      # React components
│       ├── graphql/         # Apollo queries & mutations
│       └── types/           # TypeScript interfaces
└── docker-compose.yml
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./evscheduler.db` | SQLAlchemy database URL |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis broker URL |
