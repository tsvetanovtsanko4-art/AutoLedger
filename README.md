# AutoLedger

Track what your cars cost: refuelings, services, insurance, inspections and
vignettes, with fuel consumption worked out from your fill-ups. Anonymous
visitors get a public dashboard of fleet-wide statistics.

**Stack:** React 19 + Vite 8 + Tailwind CSS 4 on the front, FastAPI +
SQLAlchemy 2 + PostgreSQL on the back, Alembic for migrations, Docker Compose
to run it all. Tests: pytest (API), Playwright (browser), JMeter (load).

## Running it

### With Docker

```bash
docker compose up --build
```

- App: https://localhost:5173 (Vite dev server, hot reload)
- API: http://localhost:8000/api, interactive docs at http://localhost:8000/docs

The API container applies migrations on start. Load sample data with:

```bash
docker compose exec server python -m server.seed
```

That creates `demo@example.com` / `password123` plus 1000 users and 3000 cars.

The first start generates a local certificate authority in `client/certs/`.
Trust it once so the browser accepts the HTTPS dev server (PowerShell as admin):

```powershell
certutil -addstore -f "ROOT" ".\client\certs\rootCA.pem"
```

For a production-like stack (nginx serving the built app and proxying `/api`):

```bash
cp .env.example .env    # fill in SECRET_KEY and POSTGRES_PASSWORD
docker compose -f docker-compose.prod.yml up --build -d
```

### Without Docker

The API falls back to a SQLite file when `DATABASE_URL` is not set.

```bash
python -m venv .venv && .venv/Scripts/activate      # macOS/Linux: source .venv/bin/activate
pip install -r server/requirements-dev.txt
export SECRET_KEY=dev-secret                        # PowerShell: $env:SECRET_KEY="dev-secret"
alembic -c server/alembic.ini upgrade head
python -m server.seed --users 50 --cars 100
uvicorn server.main:app --reload
```

```bash
cd client
npm install
npm run dev
```

### Configuration

| Variable | Default | |
|---|---|---|
| `SECRET_KEY` | none, required | Signs login tokens |
| `DATABASE_URL` | `sqlite:///./car_tracker.db` | e.g. `postgresql+psycopg://user:pass@host/db` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` | |
| `CORS_ORIGINS` | `["https://localhost:5173","http://localhost:5173"]` | JSON list |

## Tests

```bash
pytest                                   # API, from the repository root
```

```bash
cd client
npx playwright install chromium          # once
npm run test:e2e                         # starts its own API on SQLite and a dev server
```

Set `PYTHON` to your virtualenv's interpreter if `python` on PATH lacks the
server dependencies. GitHub Actions runs lint, build, pytest and Playwright on
every push and pull request (`.github/workflows/ci.yml`).

### Load tests

`performance_tests/autoledger_load_test.jmx` models three groups of users at
once: visitors on the landing page, signed-in drivers browsing their garage and
logging fuel, and a trickle of new sign-ups. It needs seeded data on the target
(`python -m server.seed`).

```powershell
cd performance_tests
.\run_test.ps1 -Profile smoke -JMeterHome D:\apache-jmeter-5.6.3
```

| Profile | Drivers / visitors / sign-ups | Duration |
|---|---|---|
| `smoke` | 3 / 2 / 1 | 1 min |
| `load` | 50 / 30 / 3 | 15 min |
| `stress` | 200 / 100 / 10 | 20 min |
| `soak` | 40 / 20 / 2 | 4 h |

The script exits non-zero when the 95th percentile of any read is above
500 ms, of any write above 1000 ms, or more than 1% of requests fail (all
adjustable with parameters). Reports go to `performance_tests/results/`.
`run_distributed.ps1` runs the same plan from two Docker load generators.

The public stats endpoint is cached in memory for 60 seconds per API worker,
so the visitor group mostly measures the cache; the drivers exercise the database.

## Database migrations

```bash
alembic -c server/alembic.ini revision --autogenerate -m "describe the change"
alembic -c server/alembic.ini upgrade head
```

`pytest` fails if a model changes without a migration. Databases created before
migrations existed are adopted as-is by the first revision.

## API

All routes except the public ones take `Authorization: Bearer <token>`.
Full, always up-to-date reference: `/docs` on a running API.

| Method | Path | |
|---|---|---|
| POST | `/api/auth/register` | Create an account |
| POST | `/api/auth/login` | Form login (`username`, `password`), returns a JWT |
| GET | `/api/me` | Current user |
| GET | `/api/me/cars` | My cars with all their logs, favourites first |
| POST | `/api/cars` | Add a car (409 if plate or VIN is taken) |
| GET / PATCH | `/api/cars/{id}` | Read / partly update a car |
| PATCH | `/api/cars/{id}/favorite` | Toggle favourite |
| GET | `/api/check/plate/{plate}`, `/api/check/vin/{vin}` | Is it still free? (`?exclude_car_id=` when editing) |
| POST | `/api/cars/{id}/refuelings` · `/services` · `/insurances` · `/inspections` | Log an expense |
| GET | `/api/cars/{id}/avg-consumption` | Average L/100km |
| PUT | `/api/cars/{id}/vignettes` | Add or replace the vignette for a country |
| GET | `/api/proxy/bgtoll/{plate}` | Live vignette lookup on check.bgtoll.bg |
| GET | `/api/public/stats` | Fleet statistics, no login |
| GET | `/api/health` | Health check |

## Layout

```
client/            React app
  src/components/  pages and forms
  e2e/             Playwright tests
server/            FastAPI app
  routers/         one module per area of the API
  migrations/      Alembic revisions
  tests/           pytest suite
  seed.py          sample data
performance_tests/ JMeter plan and runners
```
