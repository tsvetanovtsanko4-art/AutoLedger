# 🚗 Car Spending Tracker

A full-stack web application for tracking vehicle expenses, maintenance, fleet analytics, and vignette compliance. Built with **React** (Vite + Tailwind CSS v4) and **Python FastAPI**, backed by **PostgreSQL**, fully containerized with **Docker**.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-15-blue.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)

---

## ✨ Features

### 🔐 Authentication
- JWT-based user registration and login
- Secure password hashing with `pbkdf2_sha256`
- All private routes protected via Bearer tokens

### 🚙 My Garage
- Add, edit, and delete cars with full profile:
  - **Plate Number** (unique, validated) and **VIN** (unique, validated)
  - Make, Model, Year, Engine Code, Engine Volume
  - Transmission type (Manual / Automatic / CVT / DCT)
  - Drive type (FWD / RWD / AWD)
  - Tire size and current odometer
- **Plate & VIN uniqueness check** — live validation before saving
- **Favorite car** — pin one car to the top of your dashboard
- **Edit mode** — partial updates with conflict exclusion (VIN/plate checks skip the current car)

### ⛽ Expense Tracking (per car)
| Type | Fields |
|---|---|
| **Refueling** | Date, Fuel type (Petrol / Diesel / LPG / CNG / Electricity), Cost (€), Liters, Odometer |
| **Service** | Date, Parts list, Part numbers, Next service date & odometer |
| **Insurance** | Type (Civil Liability / Casco), Renewed date, Expiry date |
| **Inspection** | Renewed date, Expiry date |

- Odometer validation: cannot log a refueling below the car's current mileage
- Each refueling automatically updates the car's current odometer

### 🛂 Vignette Management
- Add / update vignettes per car per country
- Fields: Country code, Start & End date, Price, Currency, Status, Vehicle type & class
- **BG Toll live proxy** — real-time vignette status check from [check.bgtoll.bg](https://check.bgtoll.bg) by plate number (no CORS issues, requests go server-side)

### 📊 Public Analytics Dashboard (no login required)
- **Manufacturer Popularity** — bar chart of car counts by make
- **Global Spending Trends** — line chart of total fuel spend per year
- **Average Fuel Consumption** — horizontal bar chart (L/100km) per make+model computed from consecutive refueling pairs using a PostgreSQL `LAG()` window function
- **Efficiency Leaderboard** — table of average cost per km per car
- **Animated skeleton loader** — instant perceived load, no blank screen while data fetches
- **60-second server-side cache** — repeat visitors get sub-20ms API responses

---

## 🛠️ Tech Stack

### Frontend
| Tool | Role |
|---|---|
| React 18 + Vite | SPA framework + fast dev server |
| Tailwind CSS v4 | Utility-first styling |
| Recharts | Interactive data visualization |
| Axios | API integration |
| React Router | Client-side routing |
| vite-plugin-mkcert | Trusted local HTTPS certificate |

### Backend
| Tool | Role |
|---|---|
| FastAPI | High-performance Python API |
| SQLAlchemy | ORM + raw SQL support |
| Pydantic | Schema validation & serialization |
| PostgreSQL 15 | Primary database |
| Passlib (pbkdf2_sha256) | Password hashing |
| Python-Jose | JWT handling |
| Uvicorn | ASGI server with hot-reload |

### Infrastructure
| Tool | Role |
|---|---|
| Docker + Compose | Container orchestration |
| PostgreSQL 15 container | Persistent DB with named volume |
| mkcert (vite-plugin-mkcert) | Locally-trusted HTTPS certs |
| ngrok / Cloudflare Tunnel | Optional external access |

---

## 🚀 Getting Started (Docker — Recommended)

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)

### 1. Clone & start
```bash
git clone <repo-url>
cd MyProjects
docker compose up -d
```

All three containers start automatically:
| Container | Purpose | Port |
|---|---|---|
| `car_tracker_client_dev` | React frontend (HTTPS) | `5173` |
| `car_tracker_server` | FastAPI backend | `8000` |
| `car_tracker_db` | PostgreSQL 15 | internal only |

### 2. Trust the HTTPS certificate (one-time)

On first run, `vite-plugin-mkcert` generates a root CA into `client/certs/` on your host.

**Install it so the browser trusts it** (run PowerShell as Administrator):
```powershell
certutil -addstore -f "ROOT" ".\client\certs\rootCA.pem"
```

Then close and reopen your browser.

### 3. Open the app

```
https://localhost:5173
```

---

## 🌱 Seeding Sample Data (Optional)

Populate the database with realistic Bulgarian car data:

```bash
# From the project root (with containers running)
docker exec car_tracker_server python server/seed.py
```

This creates:
- **User**: `demo@example.com` / `password123`
- **Cars**: Multiple makes (Toyota, BMW, Audi, etc.) with Bulgarian plates
- **Logs**: Random refueling and service history

---

## 🌐 External Access (ngrok)

To share the app with external clients:

```bash
# 1. Expose the backend
ngrok http 8000

# 2. Update client/src/api.js baseURL to the ngrok backend URL
#    e.g. https://xyz456.ngrok-free.app/api

# 3. Expose the frontend
ngrok http https://localhost:5173 --host-header="localhost:5173"
```

Share the frontend ngrok URL with clients. Revert `api.js` after your session.

---

## 📡 API Reference

All authenticated routes require `Authorization: Bearer <token>`.

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Login, returns JWT |
| `GET` | `/api/me` | Get current user info |

### Cars
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/cars` | Create a car |
| `GET` | `/api/me/cars` | List my cars (favorites first) |
| `GET` | `/api/cars/{id}` | Get a specific car |
| `PATCH` | `/api/cars/{id}` | Update a car |
| `PATCH` | `/api/cars/{id}/favorite` | Toggle favorite |
| `GET` | `/api/check/plate/{plate}` | Check plate availability |
| `GET` | `/api/check/vin/{vin}` | Check VIN availability |

### Expense Logs (per car)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/cars/{id}/refuelings` | Log a refueling |
| `POST` | `/api/cars/{id}/services` | Log a service |
| `POST` | `/api/cars/{id}/insurances` | Log an insurance |
| `POST` | `/api/cars/{id}/inspections` | Log an inspection |
| `GET` | `/api/cars/{id}/avg-consumption` | Get avg L/100km for a car |

### Vignettes
| Method | Endpoint | Description |
|---|---|---|
| `PUT` | `/api/cars/{id}/vignettes` | Add or update a vignette (upsert by country) |
| `GET` | `/api/proxy/bgtoll/{plate}` | Live BG toll vignette status check |

### Public (no auth)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/public/stats` | Aggregated fleet analytics (cached 60s) |
| `GET` | `/api/health` | Health check |

---

## 📂 Project Structure

```
MyProjects/
├── client/                     # React frontend
│   ├── certs/                  # mkcert certificates (gitignored)
│   ├── src/
│   │   ├── api.js              # Axios instance
│   │   ├── App.jsx             # Router & layout
│   │   ├── context/            # Auth context
│   │   └── components/
│   │       ├── PublicDashboard.jsx   # Landing page + charts + skeleton
│   │       ├── Dashboard.jsx         # Authenticated garage view
│   │       ├── CarForm.jsx           # Add car form (with validation)
│   │       ├── CarEditForm.jsx       # Edit car form
│   │       ├── CarDetails.jsx        # Car detail view + logs
│   │       ├── RefuelingForm.jsx     # Log refueling
│   │       ├── ServiceForm.jsx       # Log service
│   │       ├── InsuranceForm.jsx     # Log insurance
│   │       ├── AddVignette.jsx       # Vignette management + BG toll check
│   │       ├── LoginForm.jsx         # Login
│   │       └── RegisterForm.jsx      # Register
│   ├── vite.config.js          # Vite + mkcert + proxy config
│   └── Dockerfile
├── server/                     # FastAPI backend
│   ├── main.py                 # All API routes + 60s stats cache
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # JWT + password hashing
│   ├── database.py             # DB engine + session
│   ├── seed.py                 # Sample data seeder
│   └── Dockerfile
├── docker-compose.yml          # Main compose (dev mode)
├── docker-compose.prod.yml     # Production compose
├── seed_data.py                # Root-level seeder script
└── .gitignore
```

---

## 🔒 Security Notes

- Certificates in `client/certs/` are excluded from git (`.gitignore`)
- The `client/certs/` folder is tracked via `.gitkeep`
- JWT secrets should be moved to environment variables for production deployments
- CORS is restricted to `localhost:5173` in development

---

## 📄 License

Open-source under the MIT License.
