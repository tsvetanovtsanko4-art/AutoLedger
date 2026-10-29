from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import DbSession
from .cars import OwnedCar

router = APIRouter(prefix="/api/cars/{car_id}", tags=["logs"])


def save(db: Session, record):
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.post("/insurances", response_model=schemas.Insurance, status_code=201)
def create_insurance(insurance: schemas.InsuranceCreate, car: OwnedCar, db: DbSession):
    return save(db, models.Insurance(**insurance.model_dump(), car_id=car.id))


@router.post("/inspections", response_model=schemas.Inspection, status_code=201)
def create_inspection(inspection: schemas.InspectionCreate, car: OwnedCar, db: DbSession):
    return save(db, models.Inspection(**inspection.model_dump(), car_id=car.id))


@router.post("/services", response_model=schemas.Service, status_code=201)
def create_service(service: schemas.ServiceCreate, car: OwnedCar, db: DbSession):
    return save(db, models.Service(**service.model_dump(), car_id=car.id))


@router.post("/refuelings", response_model=schemas.Refueling, status_code=201)
def create_refueling(refueling: schemas.RefuelingCreate, car: OwnedCar, db: DbSession):
    if refueling.odometer < car.current_odometer:
        raise HTTPException(status_code=400, detail="Odometer reading cannot be lower than current car mileage")
    car.current_odometer = refueling.odometer
    return save(db, models.Refueling(**refueling.model_dump(), car_id=car.id))
