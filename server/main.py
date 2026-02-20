from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from sqlalchemy.types import Float as SAFloat
from typing import List, Optional
import requests
import time
from . import models, schemas, auth
from .database import engine

# ─── Simple in-memory cache for public stats ─────────────────────────────────
_stats_cache: dict = {"data": None, "ts": 0.0}
_CACHE_TTL = 60  # seconds

def wait_for_db(retries: int = 10, delay: int = 3) -> None:
    """Retry DB connection until available or give up."""
    for attempt in range(1, retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            return
        except Exception as e:
            print(f"[startup] DB not ready (attempt {attempt}/{retries}): {e}")
            if attempt == retries:
                raise
            time.sleep(delay)

wait_for_db()


app = FastAPI(title="Car Spending Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:5173", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Health ──────────────────────────────────────────────────────────────────

@app.get("/api/health")
def health_check():
    return {"status": "ok"}


# ─── Auth ────────────────────────────────────────────────────────────────────

@app.post("/api/auth/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = models.User(
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.post("/api/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@app.get("/api/me", response_model=schemas.UserOut)
def get_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


# ─── Cars (authenticated) ────────────────────────────────────────────────────

@app.post("/api/cars", response_model=schemas.Car, status_code=201)
def create_car(
    car: schemas.CarCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db_car = models.Car(**car.dict(), user_id=current_user.id)
    db.add(db_car)
    db.commit()
    db.refresh(db_car)
    return db_car


@app.get("/api/me/cars", response_model=List[schemas.Car])
def get_my_cars(
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    cars = (
        db.query(models.Car)
        .filter(models.Car.user_id == current_user.id)
        .order_by(models.Car.is_favorite.desc(), models.Car.id)
        .all()
    )
    return cars


@app.get("/api/cars/{car_id}", response_model=schemas.Car)
def get_car(
    car_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(
        models.Car.id == car_id,
        models.Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@app.get("/api/check/plate/{plate}")
def check_plate(plate: str, db: Session = Depends(auth.get_db), exclude_car_id: Optional[int] = None):
    """Check if a plate number is already in use. Optional exclude_car_id for edit mode."""
    q = db.query(models.Car).filter(models.Car.plate == plate.upper())
    if exclude_car_id:
        q = q.filter(models.Car.id != exclude_car_id)
    exists = q.first() is not None
    return {"available": not exists}


@app.get("/api/check/vin/{vin}")
def check_vin(vin: str, db: Session = Depends(auth.get_db), exclude_car_id: Optional[int] = None):
    """Check if a VIN is already in use. Optional exclude_car_id for edit mode."""
    q = db.query(models.Car).filter(models.Car.vin == vin.upper())
    if exclude_car_id:
        q = q.filter(models.Car.id != exclude_car_id)
    exists = q.first() is not None
    return {"available": not exists}


@app.patch("/api/cars/{car_id}/favorite", response_model=schemas.Car)
def toggle_favorite(
    car_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(
        models.Car.id == car_id,
        models.Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    car.is_favorite = not car.is_favorite
    db.commit()
    db.refresh(car)
    return car


@app.patch("/api/cars/{car_id}", response_model=schemas.Car)
def update_car(
    car_id: int,
    car_update: schemas.CarUpdate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(
        models.Car.id == car_id,
        models.Car.user_id == current_user.id
    ).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    for key, value in car_update.dict(exclude_unset=True).items():
        setattr(car, key, value)
    db.commit()
    db.refresh(car)
    return car


# ─── Insurances ──────────────────────────────────────────────────────────────

@app.post("/api/cars/{car_id}/insurances", response_model=schemas.Insurance, status_code=201)
def create_insurance(
    car_id: int,
    insurance: schemas.InsuranceCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_ins = models.Insurance(**insurance.dict(), car_id=car_id)
    db.add(db_ins)
    db.commit()
    db.refresh(db_ins)
    return db_ins


# ─── Inspections ─────────────────────────────────────────────────────────────

@app.post("/api/cars/{car_id}/inspections", response_model=schemas.Inspection, status_code=201)
def create_inspection(
    car_id: int,
    inspection: schemas.InspectionCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_insp = models.Inspection(**inspection.dict(), car_id=car_id)
    db.add(db_insp)
    db.commit()
    db.refresh(db_insp)
    return db_insp


# ─── Services ────────────────────────────────────────────────────────────────

@app.post("/api/cars/{car_id}/services", response_model=schemas.Service, status_code=201)
def create_service(
    car_id: int,
    service: schemas.ServiceCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    db_svc = models.Service(**service.dict(), car_id=car_id)
    db.add(db_svc)
    db.commit()
    db.refresh(db_svc)
    return db_svc


# ─── Refueling ───────────────────────────────────────────────────────────────

@app.post("/api/cars/{car_id}/refuelings", response_model=schemas.Refueling, status_code=201)
def create_refueling(
    car_id: int,
    refueling: schemas.RefuelingCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    if refueling.odometer < car.current_odometer:
        raise HTTPException(status_code=400, detail="Odometer reading cannot be lower than current car mileage")
    db_ref = models.Refueling(**refueling.dict(), car_id=car_id)
    db.add(db_ref)
    car.current_odometer = refueling.odometer
    db.commit()
    db.refresh(db_ref)
    return db_ref


# ─── Public Stats (no auth) ──────────────────────────────────────────────────


# ─── Vignettes ───────────────────────────────────────────────────────────────

@app.put("/api/cars/{car_id}/vignettes", response_model=schemas.Vignette, status_code=200)
def upsert_vignette(
    car_id: int,
    vignette: schemas.VignetteCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    # Upsert: find existing vignette for same car+country, update it; otherwise create new
    db_vig = db.query(models.Vignette).filter(
        models.Vignette.car_id == car_id,
        models.Vignette.country_code == vignette.country_code
    ).first()
    if db_vig:
        for key, value in vignette.dict().items():
            setattr(db_vig, key, value)
    else:
        db_vig = models.Vignette(**vignette.dict(), car_id=car_id)
        db.add(db_vig)
    db.commit()
    db.refresh(db_vig)
    return db_vig


@app.get("/api/proxy/bgtoll/{plate}")
def proxy_bgtoll(plate: str, current_user: models.User = Depends(auth.get_current_user)):
    url = f"https://check.bgtoll.bg/check/vignette/plate/BG/{plate}"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Referer": "https://check.bgtoll.bg/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not(A:Brand";v="8", "Chromium";v="144", "Google Chrome";v="144"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─── Public Stats (no auth) ──────────────────────────────────────────────────

@app.get("/api/public/stats")
def public_stats(db: Session = Depends(auth.get_db)):
    global _stats_cache

    # ── Cache hit ────────────────────────────────────────────────────────────
    if _stats_cache["data"] and (time.time() - _stats_cache["ts"]) < _CACHE_TTL:
        return _stats_cache["data"]

    # ── 1. Cars by make (already a SQL aggregation) ──────────────────────────
    make_counts = (
        db.query(models.Car.make, func.count(models.Car.id))
        .group_by(models.Car.make)
        .all()
    )

    # ── 2. Total refueling cost per year (SQL GROUP BY) ──────────────────────
    cost_by_year_rows = (
        db.query(
            func.extract("year", models.Refueling.date).label("year"),
            func.sum(models.Refueling.cost_eur).label("total_eur"),
        )
        .group_by(func.extract("year", models.Refueling.date))
        .order_by("year")
        .all()
    )

    # ── 3. Avg L/100km by make+model using PostgreSQL LAG() window function ───
    consumption_sql = text("""
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
            ROUND(
                AVG(paired.quantity_liters * 100.0 / NULLIF(paired.odometer - paired.prev_odometer, 0))::numeric,
                2
            ) AS avg_l_per_100km,
            COUNT(*) AS sample_count
        FROM paired
        JOIN cars c ON c.id = paired.car_id
        WHERE paired.prev_odometer IS NOT NULL
          AND paired.odometer > paired.prev_odometer
        GROUP BY c.make, c.model
        HAVING COUNT(*) >= 1
        ORDER BY avg_l_per_100km ASC
    """)
    consumption_by_model = [
        {
            "make": row.make,
            "model": row.model,
            "avg_l_per_100km": float(row.avg_l_per_100km) if row.avg_l_per_100km is not None else None,
            "sample_count": row.sample_count,
        }
        for row in db.execute(consumption_sql)
    ]

    # ── 4. Avg cost per km per car (SQL GROUP BY) ─────────────────────────────
    consumption_by_car_rows = (
        db.query(
            models.Car.make,
            models.Car.model,
            models.Car.engine_volume,
            models.Car.model_year,
            (
                func.sum(models.Refueling.cost_eur) /
                (func.max(models.Refueling.odometer) - func.min(models.Refueling.odometer))
            ).label("avg_cost_per_km"),
        )
        .join(models.Refueling, models.Refueling.car_id == models.Car.id)
        .group_by(models.Car.id)
        .having(
            (func.max(models.Refueling.odometer) - func.min(models.Refueling.odometer)) > 0
        )
        .all()
    )

    result = {
        "cars_by_make": [{"make": m, "count": c} for m, c in make_counts],
        "cost_by_year": [{"year": int(row.year), "total_eur": round(float(row.total_eur), 2) if row.total_eur else 0.0} for row in cost_by_year_rows],
        "consumption_by_model": consumption_by_model,
        "consumption_by_car": [
            {
                "make": row.make,
                "model": row.model,
                "engine_volume": row.engine_volume,
                "model_year": row.model_year,
                "avg_cost_per_km": round(float(row.avg_cost_per_km), 4) if row.avg_cost_per_km is not None else None,
            }
            for row in consumption_by_car_rows
        ],
    }


    # ── Store in cache ────────────────────────────────────────────────────────
    _stats_cache["data"] = result
    _stats_cache["ts"] = time.time()

    return result

@app.get("/api/cars/{car_id}/avg-consumption")
def get_car_avg_consumption(
    car_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    car = db.query(models.Car).filter(models.Car.id == car_id, models.Car.user_id == current_user.id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    refuels = sorted(car.refuelings, key=lambda r: r.odometer)
    values = []
    for i in range(1, len(refuels)):
        prev, curr = refuels[i - 1], refuels[i]
        km = curr.odometer - prev.odometer
        if curr.quantity_liters and km > 0:
            values.append((curr.quantity_liters / km) * 100)
    avg = round(sum(values) / len(values), 2) if values else None
    return {"avg_l_per_100km": avg, "sample_count": len(values)}
