# AquaSense — Smart Irrigation Advisory System

AquaSense recommends exactly how much water to apply and when, using real
evapotranspiration science, live weather data, and per-field/per-crop
tracking — without requiring any physical sensors.

Agriculture accounts for ~70% of global freshwater use, and most irrigation
decisions are made on fixed schedules or guesswork rather than actual
crop/soil/weather conditions. AquaSense implements the FAO-56
Penman-Monteith reference evapotranspiration equation, applies crop
coefficients per growth stage, and runs a soil water balance to decide (1)
whether a field needs water today, (2) how much, and (3) for how long given
the field's irrigation method.

## Headline result

The **Water Savings** view compares AquaSense's demand-based irrigation
against a fixed calendar schedule (a common "irrigate every N days
regardless of soil moisture" practice) over the same historical weather —
quantifying the water saved by irrigating on actual need instead of habit.

## Architecture

```
┌───────────────────┐        ┌────────────────────────┐        ┌─────────────┐
│  React (Vite)      │◄──────►│  FastAPI backend        │◄──────►│ PostgreSQL   │
│  TypeScript         │  REST  │  JWT auth, CRUD,        │        │ (or SQLite   │
│  Tailwind CSS        │        │  recommendation engine   │        │  for local   │
│  Recharts            │        │                          │        │  dev)        │
└───────────────────┘        │  ┌────────────────────┐  │        └─────────────┘
                              │  │ ET0 (Penman-Monteith)│  │
                              │  │ Soil water balance    │  │◄──────►┌─────────────┐
                              │  │ Irrigation recommender │  │        │ Open-Meteo   │
                              │  └────────────────────┘  │        │ API (free,   │
                              └────────────────────────┘        │  no API key) │
                                                                  └─────────────┘
```

### Backend (`backend/`)

```
app/
├── main.py                 FastAPI app, CORS, startup seeding
├── config.py                env-based settings (pydantic-settings)
├── db.py                     SQLAlchemy engine/session
├── models/                   User, Field, Crop, FieldCrop
├── schemas/                  Pydantic request/response models
├── routers/                  auth, fields, crops, recommendations
├── services/
│   ├── et0.py                 FAO-56 Penman-Monteith (pure, unit-tested)
│   ├── water_balance.py        soil water balance + irrigation recommendation
│   ├── weather.py               Open-Meteo fetch + in-process cache
│   └── recommendation.py         orchestrates weather + ET0 + water balance
├── core/                      JWT security, auth dependency
└── seed_data/                  crop coefficients (10 crops) + soil properties (5 types)
tests/                          pytest — ET0, water balance, API
```

### Frontend (`frontend/`)

```
src/
├── api/          typed API client (axios)
├── components/    FieldCard, RecommendationCard, MoistureChart, WeatherStrip, ...
├── pages/          Dashboard, FieldDetail, FieldForm, WaterSavings, Login, Register
├── context/         AuthContext (JWT in localStorage)
└── types/           shared TypeScript types mirroring backend schemas
```

## The science

### Reference evapotranspiration (ET0)

Implements the FAO-56 Penman-Monteith equation (Allen et al., 1998,
*Irrigation and Drainage Paper 56*, Chapter 4):

```
ET0 = [0.408Δ(Rn − G) + γ(900/(T+273))u2(es − ea)] / [Δ + γ(1 + 0.34u2)]
```

Every intermediate term (saturation vapor pressure, psychrometric constant,
extraterrestrial/net radiation, wind speed adjustment) is its own pure,
independently-tested function in `app/services/et0.py`.

**Domain-science assumption (flagged):** full Penman-Monteith needs solar
radiation. Open-Meteo provides measured shortwave radiation for most
locations/dates, and that's used by default. When it's unavailable, ET0
falls back to the temperature-only **Hargreaves-Samani** estimate — less
accurate, but documented and surfaced to the user (`used_radiation_fallback`
in the API response, shown as a note in the UI).

### Crop coefficients (Kc) and crop evapotranspiration (ETc)

`ETc = ET0 × Kc`. Kc follows the FAO-56 curve, not a flat step function:
constant during the initial and mid-season stages, linearly interpolated
between `Kc_ini → Kc_mid` during development and `Kc_mid → Kc_end` during
the late season. Seed data covers 10 crops (maize, wheat, rice, tomato,
potato, cotton, soybean, sugarcane, onion, lettuce) with representative
stage lengths, root depths, and depletion fractions (FAO-56 Table 12/22-style
values).

**Assumption:** stage lengths are representative examples for a
sub-humid climate; real stage lengths vary by climate, cultivar, and
planting date.

### Soil water balance

A single-layer "bucket" model (FAO-56 Chapter 8):

```
Dr,i = Dr,i-1 − Peff,i + ETc,i − I,i        (bounded to [0, TAW])
```

- **TAW** (total available water) = `1000 × (field_capacity − wilting_point) × root_depth_m`
- **RAW** (readily available water) = `TAW × depletion_fraction_p` — irrigation triggers once depletion exceeds this
- **Effective rainfall** is a daily adaptation of the USDA SCS formula (originally defined for monthly totals) — a documented simplification rather than a runoff curve-number model
- Soil properties (field capacity, wilting point, infiltration rate) are seeded for 5 texture classes: sandy, sandy loam, loam, clay loam, clay

### Irrigation recommendation

Once depletion crosses RAW, the recommended **net depth** is the full
depletion (refill to field capacity), converted to a **gross depth** via the
irrigation method's application efficiency (drip 90%, sprinkler 75%, flood
60%), and to a **duration** via an assumed application rate (drip: fixed
4mm/hr; sprinkler: capped at 12mm/hr or the soil's infiltration rate,
whichever is lower; flood: the soil's infiltration rate).

**Known limitation:** the app doesn't yet persist an irrigation event log,
so the water balance simulation assumes no irrigation actually happened
during the simulated window — it's a worst-case "if nothing was done"
estimate re-computed from live weather each request, over a rolling window
(min(days since planting, 90 days)), not a persisted daily snapshot. Both
are deliberate scope cuts for this project, not silent bugs.

## Setup

### Option A — Docker Compose (recommended, one command)

```bash
docker compose up -d
```

This starts Postgres, the backend (http://localhost:8020), and the frontend
(http://localhost:5180). Swagger docs: http://localhost:8020/docs.

> Ports 8020/5180/5433 were chosen to avoid clashing with other local
> services; change them in `docker-compose.yml` if you'd rather use the
> conventional 8000/5173/5432.

### Option B — Local dev

**Backend:**

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # defaults to SQLite if DATABASE_URL is unset
uvicorn app.main:app --reload
```

**Frontend:**

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Running tests

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. pytest tests/ -v
```

27 tests, including reference values taken directly from FAO-56's own
worked examples (Table 3 saturation vapor pressure, Box 2 psychrometric
constant, and Example 18's full Bangkok ET0 calculation — 5.72mm/day).

## Screenshots

_(placeholder — add screenshots of the Dashboard, Field Detail, and Water
Savings pages here for the capstone writeup)_

## What I'd do with more time

- **Persist irrigation events** instead of re-simulating from a zero-depletion
  assumption each request — the single biggest accuracy gap right now.
- **Multi-layer soil model** (currently single-bucket) for deeper-rooted crops
  where water uptake isn't uniform with depth.
- **Runoff curve-number model** for effective rainfall instead of the daily
  SCS adaptation.
- **Background jobs** to pre-compute/cache daily recommendations instead of
  recomputing the full weather-window simulation on every request.
- **Alembic migrations** instead of `create_all` for schema evolution.
- Finish the Phase 3 stretch goals not yet built: multi-day forecasting
  regression, email notification delivery (currently mocked), PDF export,
  and a multi-field aggregate dashboard.

## Tech stack

Python, FastAPI, SQLAlchemy, PostgreSQL/SQLite, JWT auth · React, Vite,
TypeScript, Tailwind CSS, Recharts · Open-Meteo (weather) · pytest ·
Docker Compose
