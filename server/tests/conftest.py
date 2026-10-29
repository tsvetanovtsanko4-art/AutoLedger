import os

os.environ.setdefault("DATABASE_URL", "sqlite://")
os.environ.setdefault("SECRET_KEY", "test-secret-key-that-is-long-enough-for-hs256")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from server import database, main, models
from server.routers import stats


@pytest.fixture
def db_session():
    # StaticPool keeps the single in-memory connection, so every session sees the same tables.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    models.Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False)
    engine.dispose()


@pytest.fixture
def client(db_session):
    def get_test_db():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    main.app.dependency_overrides[database.get_db] = get_test_db
    stats._cache.update(data=None, expires=0.0)
    yield TestClient(main.app)
    main.app.dependency_overrides.clear()


def register_and_login(client, email="driver@example.com", password="secret123"):
    client.post("/api/auth/register", json={"email": email, "password": password})
    resp = client.post("/api/auth/login", data={"username": email, "password": password})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def refuel(client, headers, car_id, odometer, liters=40.0, cost=70.0):
    return client.post(
        f"/api/cars/{car_id}/refuelings",
        json={
            "date": "2026-01-10",
            "fuel_type": "Petrol",
            "cost_eur": cost,
            "quantity_liters": liters,
            "odometer": odometer,
        },
        headers=headers,
    )


@pytest.fixture
def auth_headers(client):
    return register_and_login(client)


@pytest.fixture
def car(client, auth_headers):
    resp = client.post(
        "/api/cars",
        json={
            "plate": "CA1234AB",
            "vin": "WVWZZZ1KZAW000001",
            "make": "VW",
            "model": "Golf",
            "current_odometer": 1000,
        },
        headers=auth_headers,
    )
    return resp.json()
