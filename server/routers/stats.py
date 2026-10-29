import time

from fastapi import APIRouter
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from .. import models
from ..auth import DbSession

router = APIRouter(prefix="/api/public", tags=["public"])

CACHE_TTL_SECONDS = 60
_cache = {"data": None, "expires": 0.0}

# Fill-to-fill consumption: pair every refueling with the previous one of the same car.
CONSUMPTION_BY_MODEL = text("""
    WITH paired AS (
        SELECT
            car_id,
            quantity_liters,
            odometer,
            LAG(odometer) OVER (PARTITION BY car_id ORDER BY odometer) AS prev_odometer
        FROM refuelings
        WHERE quantity_liters IS NOT NULL
    )
    SELECT
        c.make,
        c.model,
        AVG(paired.quantity_liters * 100.0 / (paired.odometer - paired.prev_odometer)) AS avg_l_per_100km,
        COUNT(*) AS sample_count
    FROM paired
    JOIN cars c ON c.id = paired.car_id
    WHERE paired.odometer > paired.prev_odometer
    GROUP BY c.make, c.model
    ORDER BY avg_l_per_100km
""")


def cars_by_make(db: Session):
    rows = db.execute(select(models.Car.make, func.count()).group_by(models.Car.make))
    return [{"make": make, "count": count} for make, count in rows]


def cost_by_year(db: Session):
    year = func.extract("year", models.Refueling.date)
    rows = db.execute(
        select(year.label("year"), func.sum(models.Refueling.cost_eur).label("total"))
        .group_by(year)
        .order_by(year)
    )
    return [{"year": int(row.year), "total_eur": round(row.total or 0.0, 2)} for row in rows]


def consumption_by_model(db: Session):
    return [
        {
            "make": row.make,
            "model": row.model,
            "avg_l_per_100km": round(float(row.avg_l_per_100km), 2),
            "sample_count": row.sample_count,
        }
        for row in db.execute(CONSUMPTION_BY_MODEL)
    ]


def cost_per_km_by_car(db: Session):
    distance = func.max(models.Refueling.odometer) - func.min(models.Refueling.odometer)
    rows = db.execute(
        select(
            models.Car.make,
            models.Car.model,
            models.Car.engine_volume,
            models.Car.model_year,
            (func.sum(models.Refueling.cost_eur) / distance).label("cost_per_km"),
        )
        .join(models.Refueling)
        .group_by(models.Car.id)
        .having(distance > 0)
    )
    return [
        {
            "make": row.make,
            "model": row.model,
            "engine_volume": row.engine_volume,
            "model_year": row.model_year,
            "avg_cost_per_km": round(float(row.cost_per_km), 4),
        }
        for row in rows
    ]


@router.get("/stats")
def public_stats(db: DbSession):
    # The landing page hits this on every visit; the numbers barely move, so
    # serve them from memory for a minute instead of re-running four aggregates.
    if _cache["data"] is not None and time.monotonic() < _cache["expires"]:
        return _cache["data"]

    data = {
        "cars_by_make": cars_by_make(db),
        "cost_by_year": cost_by_year(db),
        "consumption_by_model": consumption_by_model(db),
        "consumption_by_car": cost_per_km_by_car(db),
    }
    _cache.update(data=data, expires=time.monotonic() + CACHE_TTL_SECONDS)
    return data
