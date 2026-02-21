from typing import List, Optional
import re
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from .models import FuelType, InsuranceType, TransmissionType, DriveType

_EMAIL_REGEX = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Email is required.')
        if re.search(r'\s', v):
            raise ValueError('Email must not contain spaces.')
        if not _EMAIL_REGEX.match(v):
            raise ValueError('Please enter a valid email address (e.g. you@example.com).')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError('Password is required.')
        if re.search(r'\s', v):
            raise ValueError('Password must not contain spaces.')
        return v


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Email is required.')
        if re.search(r'\s', v):
            raise ValueError('Email must not contain spaces.')
        if not _EMAIL_REGEX.match(v):
            raise ValueError('Please enter a valid email address (e.g. you@example.com).')
        return v.strip()

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not v:
            raise ValueError('Password is required.')
        if re.search(r'\s', v):
            raise ValueError('Password must not contain spaces.')
        return v


class Token(BaseModel):
    access_token: str
    token_type: str

class UserOut(BaseModel):
    id: int
    email: str
    model_config = ConfigDict(from_attributes=True)


# ─── Insurance ───────────────────────────────────────────────────────────────

class InsuranceBase(BaseModel):
    type: InsuranceType
    renewed_date: date
    expiry_date: date

class InsuranceCreate(InsuranceBase):
    pass

class Insurance(InsuranceBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─── Inspection ──────────────────────────────────────────────────────────────

class InspectionBase(BaseModel):
    renewed_date: date
    expiry_date: date

class InspectionCreate(InspectionBase):
    pass

class Inspection(InspectionBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─── Service ─────────────────────────────────────────────────────────────────

class ServiceBase(BaseModel):
    date: date
    parts_list: Optional[List[str]] = []
    part_numbers: Optional[List[str]] = []
    next_service_date: Optional[date] = None
    next_service_odometer: Optional[int] = None

class ServiceCreate(ServiceBase):
    pass

class Service(ServiceBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─── Refueling ───────────────────────────────────────────────────────────────

class RefuelingBase(BaseModel):
    date: date
    fuel_type: FuelType
    cost_eur: float
    quantity_liters: Optional[float] = None
    odometer: int

class RefuelingCreate(RefuelingBase):
    pass

class Refueling(RefuelingBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─── Vignette ────────────────────────────────────────────────────────────────

class VignetteBase(BaseModel):
    country_code: str
    date_start: date
    date_end: date
    price: Optional[float] = None
    currency: Optional[str] = "EUR"
    status: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_class: Optional[str] = None

class VignetteCreate(VignetteBase):
    pass

class Vignette(VignetteBase):
    id: int
    car_id: int
    model_config = ConfigDict(from_attributes=True)


# ─── Car ─────────────────────────────────────────────────────────────────────

class CarBase(BaseModel):
    plate: str
    make: str
    model: str
    model_year: Optional[int] = None
    current_odometer: int = 0
    vin: Optional[str] = None
    engine_model: Optional[str] = None
    engine_volume: Optional[float] = None
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None
    tire_size: Optional[str] = None

class CarCreate(CarBase):
    pass

class CarUpdate(BaseModel):
    plate: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    model_year: Optional[int] = None
    current_odometer: Optional[int] = None
    engine_model: Optional[str] = None
    engine_volume: Optional[float] = None
    transmission: Optional[TransmissionType] = None
    drive_type: Optional[DriveType] = None
    tire_size: Optional[str] = None
    is_favorite: Optional[bool] = None

class Car(CarBase):
    id: int
    user_id: int
    is_favorite: bool
    insurances: List[Insurance] = []
    inspections: List[Inspection] = []
    services: List[Service] = []
    refuelings: List[Refueling] = []
    vignettes: List[Vignette] = []

    model_config = ConfigDict(from_attributes=True)
