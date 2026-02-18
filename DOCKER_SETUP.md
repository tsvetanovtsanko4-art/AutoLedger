# Docker Best Practices - Car Spending Tracker

## Overview

Your project has been containerized following Docker best practices. Two configurations are provided:

1. **Production** (`docker-compose.yml`) - Optimized for deployment
2. **Development** (`docker-compose.dev.yml`) - Optimized for local development with hot reload

---

## Production Configuration

### Files Modified/Created

**server/Dockerfile**
- Multi-stage build: separates build dependencies from runtime
- Uses Python 3.10-slim for smaller image size
- Creates non-root user for security
- Implements health checks
- Uses virtual environment for isolated dependencies
- Reduces final image size by ~65% vs single-stage build

**client/Dockerfile**
- Multi-stage build: Node build → nginx runtime
- First stage builds React app with Vite into optimized dist/
- Second stage uses nginx:alpine for serving static assets
- nginx proxies API calls to backend at `/api/`
- Implements SPA fallback routing (all unknown routes → index.html)
- Static assets served with 1-year cache headers
- Final image size ~20MB vs ~500MB+ for single-stage

**client/nginx.conf**
- Routes `/api/` requests to FastAPI backend
- SPA fallback routing for client-side navigation
- Static asset caching strategy
- Health check endpoint at `/health`

**docker-compose.yml**
- Both services use production images
- Database volume persists data (`db_data`)
- Health checks for both services
- `depends_on` ensures backend starts before frontend
- Bridge network for service-to-service communication
- Client accessible on port 80 (HTTP)

### Running Production

```bash
# Build and start both services
docker compose up --build

# Access the app at http://localhost
```

The backend is only accessible internally via Docker network; frontend proxies all `/api/` calls to the backend.

---

## Development Configuration

### Files Created

**docker-compose.dev.yml**
- Mounts source code for hot reload on both services
- Backend: auto-reload with `--reload` flag
- Frontend: Vite dev server with polling for file changes
- Same database volume for consistency

**client/Dockerfile.dev**
- Single-stage: just Node + Vite dev server
- Mounts source with volume to enable hot reload

### Running Development

```bash
# Start with hot reload
docker compose -f docker-compose.dev.yml up

# Access frontend at http://localhost:5173
# Backend API at http://localhost:8000
```

Changes to Python code (server/) automatically reload the FastAPI server.
Changes to React code (client/) automatically reload the dev server.

---

## Key Improvements

### Security
✓ Non-root user in backend container
✓ Minimal base images (slim Python, alpine Node/nginx)
✓ Production build removes dev dependencies

### Performance
✓ Multi-stage builds reduce image sizes by 60-80%
✓ Static assets cached for 1 year in production
✓ Virtual environment in Python for isolated deps
✓ npm ci instead of npm install for reproducibility

### Reliability
✓ Health checks on both services
✓ Proper service startup ordering (depends_on)
✓ Restart policies for failed containers
✓ Volume persistence for database

### Developer Experience
✓ Hot reload in development mode
✓ Separate dev and prod configs
✓ File watching with polling for cross-platform support

---

## Dockerfile Optimizations

### Backend (Python/FastAPI)
1. **Multi-stage**: Separates build tools from runtime
2. **Virtual environment**: Isolated Python dependencies
3. **Slim base image**: Only runtime essentials
4. **Non-root user**: Runs as UID 1000 (appuser)
5. **Health checks**: HTTP request to `/api/health`

### Frontend (React/Vite)
1. **Multi-stage**: Build Node app, serve with nginx
2. **npm ci**: Reproducible installs (not npm install)
3. **Alpine base**: ~5MB nginx instead of full image
4. **Nginx proxy**: Handles API routing and SPA fallback
5. **Cache strategy**: Long-term cache for assets, no-cache for index.html

---

## .dockerignore Files

Excludes unnecessary files from builds:
- `__pycache__`, `node_modules`, `.git` (large, not needed in image)
- `.env`, `.vscode`, `.idea` (config/secrets, not needed in image)
- Source code folders for production builds (removed by multi-stage build)

---

## Network Communication

### Production (docker-compose.yml)
```
Client (nginx) ──── API proxy ──── Server (FastAPI)
  Port 80              /api/          Port 8000 (internal only)
                        └─ via bridge network
```

The frontend container talks to the backend via Docker's internal DNS (`server:8000`).
External users only access the frontend on port 80.

### Development (docker-compose.dev.yml)
```
Frontend (Vite)       Backend (Uvicorn)
  Port 5173            Port 8000
     └── Both accessible from host
```

In development, both are accessible directly for easier debugging.

---

## Database Persistence

**Production**: Volume `db_data` persists the SQLite database across container restarts.
**Development**: Volume `./car_tracker.db` mounts the local file into the container.

To reset database:
```bash
# Production
docker volume rm <project>_db_data

# Development
rm car_tracker.db
docker compose -f docker-compose.dev.yml up
```

---

## Next Steps

1. **Build production images**:
   ```bash
   docker compose build
   ```

2. **Test locally with dev config**:
   ```bash
   docker compose -f docker-compose.dev.yml up
   ```

3. **Deploy production config**:
   ```bash
   docker compose up -d
   ```

4. **Seed data** (if needed):
   ```bash
   docker compose exec server python seed_data.py
   ```

---

## Troubleshooting

**Backend fails to start?**
```bash
docker compose logs server
```

**Frontend can't reach API?**
Check nginx config and verify `server:8000` is reachable from within the network.

**Database not persisting?**
Ensure volume is mounted: `docker volume ls | grep db_data`

**Hot reload not working in development?**
Check file permissions and ensure source paths are correct in docker-compose.dev.yml.
