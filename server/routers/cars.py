from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from .. import models, schemas
from ..auth import CurrentUser, DbSession

router = APIRouter(prefix="/api", tags=["cars"])


def get_owned_car(car_id: int, db: DbSession, current_user: CurrentUser) -> models.Car:
    car = db.get(models.Car, car_id)
    if car is None or car.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


OwnedCar = Annotated[models.Car, Depends(get_owned_car)]

CAR_LOGS = (
    models.Car.insurances,
    models.Car.inspections,
    models.Car.services,
    models.Car.refuelings,
    models.Car.vignettes,
)


def commit_car(db: Session) -> None:
    # plate and vin are unique columns; report a clash as 409 so the form can
    # point at the field instead of showing a generic server error.
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        field = "VIN" if "vin" in str(e.orig).lower() else "Plate number"
        raise HTTPException(status_code=409, detail=f"{field} is already registered")


@router.post("/cars", response_model=schemas.Car, status_code=201)
def create_car(car_in: schemas.CarCreate, db: DbSession, current_user: CurrentUser):
    car = models.Car(**car_in.model_dump(), user_id=current_user.id)
    db.add(car)
    commit_car(db)
    db.refresh(car)
    return car


@router.get("/me/cars", response_model=List[schemas.Car])
def list_my_cars(db: DbSession, current_user: CurrentUser):
    # The response embeds every log list; load them in one query per list instead of per car.
    query = (
        select(models.Car)
        .where(models.Car.user_id == current_user.id)
        .order_by(models.Car.is_favorite.desc(), models.Car.id)
        .options(*(selectinload(rel) for rel in CAR_LOGS))
    )
    return db.scalars(query).all()


@router.get("/cars/{car_id}", response_model=schemas.Car)
def get_car(car: OwnedCar):
    return car


@router.patch("/cars/{car_id}", response_model=schemas.Car)
def update_car(car_update: schemas.CarUpdate, car: OwnedCar, db: DbSession):
    for key, value in car_update.model_dump(exclude_unset=True).items():
        setattr(car, key, value)
    commit_car(db)
    db.refresh(car)
    return car


@router.patch("/cars/{car_id}/favorite", response_model=schemas.Car)
def toggle_favorite(car: OwnedCar, db: DbSession):
    car.is_favorite = not car.is_favorite
    db.commit()
    db.refresh(car)
    return car


def is_available(db: Session, column, value: str, exclude_car_id: Optional[int]) -> dict:
    query = select(models.Car.id).where(column == value.strip().upper())
    if exclude_car_id:
        query = query.where(models.Car.id != exclude_car_id)
    return {"available": db.scalar(query) is None}


@router.get("/check/plate/{plate}")
def check_plate(plate: str, db: DbSession, _: CurrentUser, exclude_car_id: Optional[int] = None):
    return is_available(db, models.Car.plate, plate, exclude_car_id)


@router.get("/check/vin/{vin}")
def check_vin(vin: str, db: DbSession, _: CurrentUser, exclude_car_id: Optional[int] = None):
    return is_available(db, models.Car.vin, vin, exclude_car_id)


@router.get("/cars/{car_id}/avg-consumption")
def get_avg_consumption(car: OwnedCar):
    # Fill-to-fill method: the litres put in at a stop were burnt since the previous stop.
    refuels = sorted(car.refuelings, key=lambda r: r.odometer)
    values = [
        curr.quantity_liters / (curr.odometer - prev.odometer) * 100
        for prev, curr in zip(refuels, refuels[1:])
        if curr.quantity_liters and curr.odometer > prev.odometer
    ]
    avg = round(sum(values) / len(values), 2) if values else None
    return {"avg_l_per_100km": avg, "sample_count": len(values)}
