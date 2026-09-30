# DAGPS API Wrapper

FastAPI wrapper for [www.dagps.net](https://www.dagps.net)

## Setup

```bash
# Install dependencies
uv sync

# Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# Run development server
uv run uvicorn main:app --reload
```

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/live/all` | All devices, live data |
| GET | `/live?user_ids=a,b,c` | Specific devices, live data |
| GET | `/reports/mileage?start=YYYY-MM-DD&end=YYYY-MM-DD` | Mileage report (defaults to today) |
| GET | `/reports/daily-mileage?user_id=XXX&start=YYYY-MM-DD&end=YYYY-MM-DD` | Per-day mileage and stop count |
| GET | `/reports/stops?user_id=XXX&start=YYYY-MM-DD&end=YYYY-MM-DD&min_stay_seconds=300` | Stops/parking for one device |
| GET | `/address?lat=X&lng=Y` | Get address for coordinates |

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GPS_USER` | Yes | - | DAGPS login |
| `GPS_PASSWORD` | Yes | - | DAGPS password |
| `GPS_BASE_URL` | No | `https://www.dagps.net` | Base URL |
| `GPS_TZ` | No | `5.5` | Timezone offset (Sri Lanka = UTC+5:30) |

## Development

```bash
# Install dev dependencies
uv sync --dev

# Run tests
uv run pytest
```
