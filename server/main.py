from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from . import models, schemas, auth
from .database import engine

models.Base.metadata.create_all(bind=engine)

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

@app.get("/api/public/stats")
def public_stats(db: Session = Depends(auth.get_db)):
    # Cars by make
    make_counts = db.query(models.Car.make, func.count(models.Car.id)).group_by(models.Car.make).all()

    # Total refueling cost per year
    refuelings = db.query(models.Refueling).all()
    cost_by_year = {}
    for r in refuelings:
        year = str(r.date.year)
        cost_by_year[year] = round(cost_by_year.get(year, 0) + r.cost_eur, 2)

    # Avg fuel consumption by make/model (cost per km as proxy)
    cars = db.query(models.Car).all()
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
    }
