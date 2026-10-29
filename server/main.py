from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import cars, logs, stats, users, vignettes

# The schema is managed by Alembic (server/migrations): run `alembic upgrade head` before starting.
app = FastAPI(title="AutoLedger API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for module in (users, cars, logs, vignettes, stats):
    app.include_router(module.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
