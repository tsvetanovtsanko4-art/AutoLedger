from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import requests
from . import models, schemas, auth
from .database import engine

import time

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
    # Cars by make
    make_counts = db.query(models.Car.make, func.count(models.Car.id)).group_by(models.Car.make).all()

    # Total refueling cost per year
    refuelings_all = db.query(models.Refueling).all()
    cost_by_year = {}
    for r in refuelings_all:
        year = str(r.date.year)
        cost_by_year[year] = round(cost_by_year.get(year, 0) + r.cost_eur, 2)

    # Avg L/100km by make+model (only cars with quantity_liters data)
    cars = db.query(models.Car).all()
    model_consumption: dict = {}  # key: (make, model) -> list of l_per_100km values

    for car in cars:
        refuels = sorted(car.refuelings, key=lambda r: r.odometer)
        for i in range(1, len(refuels)):
            prev, curr = refuels[i - 1], refuels[i]
            km = curr.odometer - prev.odometer
            if curr.quantity_liters and km > 0:
                l_per_100 = (curr.quantity_liters / km) * 100
                key = (car.make, car.model)
                model_consumption.setdefault(key, []).append(l_per_100)

    consumption_by_model = []
    for (make, model), values in model_consumption.items():
        if values:
            consumption_by_model.append({
                "make": make,
                "model": model,
                "avg_l_per_100km": round(sum(values) / len(values), 2),
                "sample_count": len(values),
            })
    consumption_by_model.sort(key=lambda x: x["avg_l_per_100km"])

    # Avg cost per km per car (legacy table)
    consumption_data = []
    for car in cars:
        if car.refuelings:
            total_cost = sum(r.cost_eur for r in car.refuelings)
            max_odo = max(r.odometer for r in car.refuelings)
            min_odo = min(r.odometer for r in car.refuelings)
            km_driven = max_odo - min_odo
            if km_driven > 0:
                consumption_data.append({
                    "make": car.make,
                    "model": car.model,
                    "engine_volume": car.engine_volume,
                    "model_year": car.model_year,
                    "avg_cost_per_km": round(total_cost / km_driven, 4),
                })

    return {
        "cars_by_make": [{"make": m, "count": c} for m, c in make_counts],
        "cost_by_year": [{"year": y, "total_eur": v} for y, v in sorted(cost_by_year.items())],
        "consumption_by_car": consumption_data,
        "consumption_by_model": consumption_by_model,
    }

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
